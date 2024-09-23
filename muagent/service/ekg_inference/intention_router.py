import re
import numpy as np
import pandas as pd
import muagent.base_configs.prompts.intention_template_prompt as itp
from collections import defaultdict, deque
from loguru import logger
from jieba.analyse import extract_tags
from dataclasses import dataclass, field, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Union, Optional, Any
from muagent.db_handler.graph_db_handler.base_gb_handler import GBHandler
from muagent.db_handler.vector_db_handler.tbase_handler import TbaseHandler
from muagent.schemas.ekg.ekg_graph import NodeTypesEnum
from muagent.schemas.common import GNode, GEdge
from muagent.llm_models.get_embedding import get_embedding
from muagent.utils.common_utils import double_hashing
from .intention_match_rule import MatchRule


@dataclass
class NLPRetInfo:
    node_id: str
    is_leaf: bool = False
    nodes_to_choose: Optional[list[dict]] = field(default=None)
    answer: str = None
    error_msg: str = ''


@dataclass
class RuleRetInfo:
    node_id: str
    is_leaf: bool = False
    error_msg: str = ''


class IntentionRouter:
    Rule_type = Optional[str]

    def __init__(
        self, agent=None, gb_handler: GBHandler = None, tb_handler: TbaseHandler = None,
        embed_config=None
    ):
        self.agent = agent
        self.gb_handler = gb_handler
        self.tb_handler = tb_handler
        self.embed_config = embed_config
        self._node_type = NodeTypesEnum.INTENT.value
        self._max_num_tb_retrieval = 5
        self._filter_max_depth = 5
        self._dis_threshold = 16

    def get_intention_by_info2id(
        self, gb_handler: GBHandler, rule: Union[str, Callable] = ':', **kwargs
    ) -> str:
        gb_handler = gb_handler if gb_handler is not None else self.gb_handler
        node_id = rule.join(kwargs.values()) if isinstance(
            rule, str) else rule(**kwargs)
        if not self._node_exist(node_id):
            logger.error(f'Node(id={node_id}, node_type={self._node_type}) does not exist!')
            return None
        return node_id

    def _get_intention_by_node_info_match(
        self, gb_handler: GBHandler, root_node_id: str, rule: Rule_type = None, **kwargs
    ) -> str:
        def _func(node: GNode, rule: Callable):
            return rule(node, **kwargs), node.id

        error_msg, rule_str = '', rule
        rule = self._get_rule_by_str(rule)
        if rule is None:
            error_msg = f'Rule {rule_str} is not valid!'
            return None, error_msg

        intention_nodes = gb_handler.get_neighbor_nodes({'id': root_node_id}, self._node_type)
        intention_nodes = [
            node for node in intention_nodes if node.type == self._node_type
        ]
        if len(intention_nodes) == 0:
            return root_node_id, error_msg
        elif len(intention_nodes) == 1:
            return intention_nodes[0].id, error_msg
        elif len(intention_nodes) < self._dis_threshold:
            scores = [_func(node, rule) for node in intention_nodes]
        else:
            params = [(node, rule) for node in intention_nodes]
            scores = _execute_func_distributed(_func, params)

        max_score = max(scores)[0]
        select_nodes = [x[-1] for x in scores if x[0] == max_score]
        select_node = self._equal_score_route_info_match(select_nodes, gb_handler)
        return select_node, error_msg

    def get_intention_by_node_info_match(
        self, root_node_id: str, filter_attribute: Optional[dict] = None,
        gb_handler: Optional[GBHandler] = None,
        rule: Union[Rule_type, list[Rule_type]] = None, **kwargs
    ) -> dict[str, Any]:
        gb_handler = gb_handler if gb_handler is not None else self.gb_handler
        root_node_id = self._filter_from_root_node(
            gb_handler, root_node_id, filter_attribute
        )

        is_leaf = False
        if len(kwargs) == 0:
            error_msg = 'No information in query to be matched.'
            return asdict(
                RuleRetInfo(node_id=root_node_id, error_msg=error_msg))

        args_list = _parse_kwargs(**kwargs)
        if not isinstance(rule, (list, tuple)):
            rule = [rule] * len(args_list)
        if len(rule) != len(args_list):
            error_msg = 'Length of rule should be equal to the length of Arguments.'
            return asdict(
                RuleRetInfo(node_id=root_node_id, error_msg=error_msg))

        if not root_node_id:
            error_msg = f'No node matches attribute {filter_attribute}.'
            return asdict(
                RuleRetInfo(node_id=root_node_id, error_msg=error_msg))

        for cur_kw_arg, cur_rule in zip(args_list, rule):
            next_node_id, error_msg = self._get_intention_by_node_info_match(
                gb_handler, root_node_id, cur_rule, **cur_kw_arg)
            if next_node_id is None or next_node_id == root_node_id:
                is_leaf = True if next_node_id else False
                return asdict(RuleRetInfo(
                    node_id=root_node_id, is_leaf=is_leaf, error_msg=error_msg
                ))
            root_node_id = next_node_id

        next_node_id = root_node_id
        while next_node_id:
            root_node_id = next_node_id
            intention_nodes = gb_handler.get_neighbor_nodes(
                {'id': next_node_id}, self._node_type)
            intention_nodes = [
                node for node in intention_nodes
                if node.type == self._node_type
            ]
            if len(intention_nodes) == 1:
                next_node_id = intention_nodes[0].id
                continue
            next_node_id = None
            if len(intention_nodes) == 0:
                is_leaf = True

        if not is_leaf:
            error_msg = 'Not enough to arrive the leaf node.'
        return asdict(
            RuleRetInfo(node_id=root_node_id, is_leaf=is_leaf, error_msg=error_msg)
        )

    def get_intention_by_node_info_nlp(
        self,
        root_node_id: str,
        query: str,
        start_from_root: bool = False,
        gb_handler: Optional[GBHandler] = None,
        tb_handler: Optional[TbaseHandler] = None,
        agent=None,
    ) -> dict[str, Any]:
        gb_handler = gb_handler if gb_handler is not None else self.gb_handler
        tb_handler = tb_handler if tb_handler is not None else self.tb_handler
        agent = agent if agent is not None else self.agent

        if start_from_root:
            return self._get_intention_by_nlp_from_root(
                gb_handler, agent, root_node_id, query)

        nodes_tb = self._tb_match(tb_handler, query, self._node_type)
        filter_nodes_tb = self._filter_ancestors(gb_handler, nodes_tb, root_node_id)
        filter_nodes_tb = {
            k: v for k, v in filter_nodes_tb.items()
            if self.is_node_valid(k, gb_handler)
        }

        if len(filter_nodes_tb) == 0:
            error_msg = 'No intention matched after tb_handler retrieval.'
            ans = self._get_agent_ans_no_ekg(agent, query)
            return asdict(
                NLPRetInfo(root_node_id, answer=ans, error_msg=error_msg))
        elif len(filter_nodes_tb) > 1:
            error_msg = 'More than one intention matched after tb_handler retrieval.'
            desc_list = []
            for k, v in filter_nodes_tb.items():
                node_desc = gb_handler.get_current_node(
                    {'id': k}, node_type=self._node_type)
                node_desc = node_desc.attributes.get('description', '')
                desc_list.append({
                    'description': node_desc,
                    'path': ' -> '.join(v)
                })
            return asdict(
                NLPRetInfo(root_node_id, nodes_to_choose=desc_list, error_msg=error_msg)
            )

        root_node_id = list(filter_nodes_tb.keys())[0]
        return self._get_intention_by_nlp_from_root(gb_handler, agent, root_node_id, query)

    def _get_intention_by_nlp_from_root(
        self,
        gb_handler: GBHandler,
        agent,
        root_node_id: str,
        query: str,
    ) -> dict[str, Any]:
        canditates = gb_handler.get_neighbor_nodes({'id': root_node_id},
                                                   self._node_type)
        canditates = [n for n in canditates if n.type == self._node_type]
        if len(canditates) == 0:
            return asdict(NLPRetInfo(root_node_id, True))
        elif len(canditates) == 1:
            root_node_id = canditates[0].id
            return self._get_intention_by_nlp_from_root(
                gb_handler, agent, root_node_id, query)

        desc_list = [x.attributes.get('description', '') for x in canditates]
        desc_list.append('与上述意图都不匹配，属于其他类型的询问意图。')
        query_intention = itp.get_intention_prompt(
            '作为智能助手，您需要根据用户询问判断其主要意图，以确定接下来的行动。',
            desc_list).format(query=query)

        ans = agent.predict(query_intention).strip()
        ans = re.search('\d+', ans)
        if ans:
            ans = int(ans.group(0)) - 1
            if ans < len(desc_list) - 1:
                root_node_id = canditates[ans].id
                return self._get_intention_by_nlp_from_root(
                    gb_handler, agent, root_node_id, query)

        error_msg = f'No intention matched at Node(id={root_node_id}).'
        ans = self._get_agent_ans_no_ekg(agent, query)
        return asdict(NLPRetInfo(root_node_id, answer=ans,
                                 error_msg=error_msg))

    def get_intention_whether_execute(self, query: str, agent=None) -> bool:
        agent = agent if agent else self.agent
        query = itp.WHETHER_EXECUTE_PROMPT.format(query=query)
        ans = agent.predict(query).strip()
        ans = re.search('\d+', ans)
        if ans:
            ans = int(ans.group(0)) - 1
            if ans < len(itp.INTENTIONS_WHETHER_EXEC):
                return itp.INTENTIONS_WHETHER_EXEC[ans][0] == '执行'
        return False

    def get_intention_consult_which(self, query: str, agent=None) -> str:
        agent = agent if agent else self.agent
        query = itp.CONSULT_WHICH_PROMPT.format(query=query)
        ans = agent.predict(query).strip()
        ans = re.search('\d+', ans)
        if ans:
            ans = int(ans.group(0)) - 1
            if ans < len(itp.INTENTIONS_CONSULT_WHICH):
                return itp.INTENTIONS_CONSULT_WHICH[ans][0]

        return itp.INTENTIONS_CONSULT_WHICH[-1][0]

    def _filter_from_root_node(
        self, gb_handler: GBHandler, root_node_id: str, attribute: Optional[dict] = None
    ) -> Optional[str]:
        if attribute is None or len(attribute) == 0:
            return root_node_id
        canditates = gb_handler.get_hop_infos(
            {
                'id': root_node_id
            },
            self._node_type,
            hop=self._filter_max_depth,
        ).nodes
        canditates = [
            node for node in canditates if node.type == self._node_type
        ]

        for node in canditates:
            count = len(attribute)
            for k, v in attribute.items():
                if v in getattr(node, k):
                    count -= 1
            if not count:
                return node.id

        return None

    def _tb_match(self, tb_handler: TbaseHandler, query: str, node_type: str, teamid=None) -> set:
        def _vector_search(query_vector: bytes, key: str):
            prefix = f'(@node_str: *{teamid}*)' if teamid else ''
            prefix += '(@node_type: {})'.format(node_type)
            base_query = f'{prefix}=>[KNN {self._max_num_tb_retrieval} @{key} $vector AS distance]'
            query_params = {"vector": query_vector}
            r = tb_handler.vector_search(base_query, query_params=query_params)
            ret = [x.node_id for x in r.docs]
            return ret
        
        def _keyword_search(query: str, key: str):
            prefix = f'(@node_str: *{teamid}*)' if teamid else ''
            query = prefix + f'(@node_type: {node_type})(@{key}:{{{keyword}}})'
            r = tb_handler.search(query, limit=self._max_num_tb_retrieval)
            ret = [x.node_id for x in r.docs]
            return ret

        tb_results = []
        if self.embed_config:
            query_vector = self._get_embedding(query)
            ret = _execute_func_distributed(
                _vector_search,
                [(query_vector, key) for key in ('desc_vector', 'name_vector')]
            )
            for temp_ret in ret:
                tb_results.extend(temp_ret)
        
        keyword = '|'.join(extract_tags(query))
        ret = _execute_func_distributed(
            _keyword_search,
            [(keyword, key) for key in ('desc_keyword', 'name_keyword')]
        )
        for temp_ret in ret:
            tb_results.extend(temp_ret)

        return set(tb_results)

    def is_node_valid(self, node_id: str, gb_handler: Optional[GBHandler] = None) -> bool:
        gb_handler = gb_handler if gb_handler is not None else self.gb_handler
        canditates = gb_handler.get_neighbor_nodes({'id': node_id},
                                                   self._node_type)
        if len(canditates) == 0:
            return False
        canditates = [n.id for n in canditates if n.type == self._node_type]
        if len(canditates) == 0:
            return True
        return self.is_node_valid(canditates[0], gb_handler)

    def _get_agent_ans_no_ekg(self, agent, query: str) -> str:
        query = itp.DIRECT_CHAT_PROMPT.format(query=query)
        ans = agent.predict(query).strip()
        ans += f'\n\n以上内容由语言模型生成，仅供参考。'
        return ans

    def _filter_ancestors_hop(self, gb_handler: GBHandler, nodes: set, root_node: str) -> dict[str, list[str]]:
        gb_ret = gb_handler.get_hop_infos(
            {'id': root_node},
            self._node_type,
            hop=self._filter_max_depth,
        )
        paths, nodes = gb_ret.paths, gb_ret.nodes
        if len(paths) == 0:
            return dict()

        visited, ret_dict = set(), dict()
        for path_list in paths:
            ancestor, pos = path_list[0], 0
            for i, node_id in enumerate(path_list):
                if node_id in ret_dict:
                    ret_dict.pop(node_id)
                if node_id in nodes:
                    ancestor, pos = node_id, i
            if ancestor not in visited and ancestor in nodes:
                ret_dict[ancestor] = path_list[:pos + 1]
            for j in range(i + 1):
                visited.add(path_list[j])

        id2name = {node.id: node.attributes.get('name', '') for node in nodes}
        for k, v in ret_dict.items():
            ret_dict[k] = [id2name[x] for x in v]

        return ret_dict

    def _filter_ancestors(self, gb_handler: GBHandler, nodes: set, root_node: str) -> dict[str, list[str]]:
        split = '<->'

        def _dfs(s: str, ancestor: str, path: str, out: dict, visited: set):
            childs = gb_handler.get_neighbor_nodes({'id': s}, self._node_type)
            childs = [child.id for child in childs if child.type == self._node_type]

            if len(childs) == 0:
                if ancestor not in visited and ancestor in nodes:
                    index = path.index(ancestor)
                    out[ancestor] = path[:index + len(ancestor)]
                return

            for child in childs:
                if child in nodes:
                    if ancestor in out:
                        out.pop(ancestor)
                    temp_ancestor = child
                else:
                    temp_ancestor = ancestor
                child_path = split.join((path, child))
                _dfs(child, temp_ancestor, child_path, out, visited)
                if s in nodes:
                    visited.add(s)

        if len(nodes) == 0:
            return dict()
        filter_nodes = dict()
        _dfs(root_node, root_node, root_node, filter_nodes, set())

        for k, v in filter_nodes.items():
            filter_nodes[k] = v.split(split)
        return filter_nodes

    def _node_exist(self, node_id: str, gb_handler):
        try:
            gb_handler.get_current_node({'id': node_id}, node_type=self._node_type)
        except IndexError:
            return False
        return True

    def _get_embedding(self, text: str):
        text_vector = get_embedding(
            self.embed_config.embed_engine, [text], self.embed_config.embed_model_path,
            self.embed_config.model_device, self.embed_config
        )[text]
        return np.array(text_vector).astype(dtype=np.float32).tobytes()

    def _get_rule_by_str(self, rule: str) -> Optional[Callable]:
        if rule is None:
            return None
        has_func = re.search('def ([a-zA-Z0-9_]+)\(.*\):', rule)
        if not has_func:
            return getattr(MatchRule, rule.strip(), None)

        func_name = has_func.group(1)
        try:
            exec(rule)
        except Exception as e:
            logger.info(f'Rule {rule} cannot be executed!')
            logger.error(e)
            return None

        return locals().get(func_name, None)

    def _equal_score_route_info_match(self, node_ids: Union[list, tuple], gb_handler):
        if len(node_ids) == 1:
            return node_ids[0]
        for node_id in node_ids:
            if self.is_node_valid(node_id, gb_handler):
                return node_id
        return node_ids[-1]

    def intention_df2graph(
        self, data_df: pd.DataFrame, teamid: str, root_node_id: Optional[str] = None,
        gb_handler: Optional[GBHandler] = None,
        tb_handler: Optional[TbaseHandler] = None,
        embed_config=None
    ):
        def _check_columns():
            df_columns = set(data_df.columns)
            tar_columns = ('id', 'description', 'name', 'child_ids')
            tar_col_absent = set(tar_columns) - df_columns
            return tar_col_absent

        def _exist_cycle(in_degree: dict, out_graph: dict):
            in_degree = in_degree.copy()
            stack = deque(
                [node for node in out_graph if node not in in_degree])
            while stack:
                node = stack.popleft()
                if not out_graph[node]:
                    continue
                for i in out_graph[node]:
                    in_degree[i] -= 1
                    if in_degree[i] == 0:
                        stack.append(i)
                        in_degree.pop(i)
            return bool(in_degree)

        def _cat_id(*node_ids):
            node_ids = [x for x in node_ids if x]
            return '_'.join(node_ids)

        def _check_fail_num_gb(gb_results: list):
            ret = sum([
                int(x["status"]["errorMessage"] not in ["GDB_SUCCEED"])
                for x in gb_results
            ])
            return ret

        gb_handler = gb_handler if gb_handler is not None else self.gb_handler
        tb_handler = tb_handler if tb_handler is not None else self.tb_handler
        embed_config = embed_config if embed_config is not None else self.embed_config

        absent_cols = _check_columns()
        if absent_cols:
            return 'Columns {} do not exist!'.format(', '.join(absent_cols))

        in_degrees, out_graphs = defaultdict(int), dict()
        for _, row in data_df.iterrows():
            for child_id in row['child_ids']:
                in_degrees[child_id] += 1
            out_graphs[row['id']] = row['child_ids']
        if _exist_cycle(in_degrees, out_graphs):
            return 'Cycle exists!'

        edge_type = f'{self._node_type}_extend_{self._node_type}'
        add_nodes, update_nodes, add_edges, del_edges = [], [], [], []
        for _, row in data_df.iterrows():
            node_id = _cat_id(root_node_id, row['id'])
            node = GNode(
                id=node_id, type=self._node_type,
                attributes={'description': row['description'], 'name': row['name']}
            )
            if self._node_exist(node_id, gb_handler):
                update_nodes.append(node)
                child_nodes = gb_handler.get_neighbor_nodes({'id': node_id}, self._node_type)
                child_nodes = [node for node in child_nodes if node.node_type == self._node_type]
                del_edges.extend([
                    (double_hashing(node_id), double_hashing(child_node), edge_type)
                    for child_node in child_nodes
                ])
            else:
                add_nodes.append(node)
            for child_id in row['child_ids']:
                child_id = _cat_id(root_node_id, child_id)
                add_edges.append(GEdge(
                    start_id=node_id, end_id=child_id,
                    type=edge_type,
                    attributes=dict()
                ))
            if not in_degrees[row['id']] and root_node_id:
                add_edges.append(GEdge(
                    start_id=root_node_id, end_id=node_id,
                    type=edge_type,
                    attributes=dict()
                ))

        from muagent.service.ekg_construct import EKGConstructService
        ekg_construct = EKGConstructService(embed_config=embed_config)
        ekg_construct.gb = gb_handler
        ekg_construct.tb = tb_handler

        ret_add_nodes = ekg_construct.add_nodes(add_nodes, teamid=teamid)['gb_result']
        ret_update_nodes = ekg_construct.update_nodes(update_nodes, teamid=teamid)['gb_result']
        ret_del_edges = _execute_func_distributed(gb_handler.delete_edge, del_edges)
        add_edges = ekg_construct._update_new_attr_for_edges(add_edges)
        ret_add_edges = _execute_func_distributed(gb_handler.add_edge, add_edges)

        status, error_msg = True, ''
        for gb_ret, prefix in zip(
            (ret_add_nodes + ret_update_nodes, ret_add_edges, ret_del_edges),
            ('Add Nodes', 'Add Edges', 'Delete Edges')
        ):
            fail_num = _check_fail_num_gb(gb_ret)
            status &= fail_num == 0
            error_msg += '{}\tSuccess {}\tFail {}\n'.format(prefix, len(gb_ret) - fail_num, fail_num)

        return status, error_msg.strip()


def _parse_kwargs(**kwargs) -> list:
    keys = list(kwargs.keys())
    if not isinstance(kwargs[keys[0]], (list, tuple)):
        return [kwargs]

    ret_list = []
    max_len = max([len(v) for v in kwargs.values()])
    for i in range(max_len):
        cur_kwargs = dict()
        for k, v in kwargs.items():
            if i < len(v):
                cur_kwargs[k] = v[i]
        ret_list.append(cur_kwargs)

    return ret_list


def _execute_func_distributed(func: Callable, params: list[Union[tuple, dict]]):
    tasks = []
    with ThreadPoolExecutor(max_workers=8) as exec:
        for param in params:
            if isinstance(param, tuple):
                task = exec.submit(func, *param)
            else:
                task = exec.submit(func, **param)
            tasks.append(task)

    results = []
    for task in as_completed(tasks):
        results.append(task.result())
    return results
