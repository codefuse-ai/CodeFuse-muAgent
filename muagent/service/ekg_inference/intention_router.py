import re
import os
import jieba
import numpy as np
import pandas as pd
import muagent.base_configs.prompts.intention_template_prompt as itp
from collections import defaultdict, deque, OrderedDict
from loguru import logger
from enum import Enum
from jieba.analyse import extract_tags
from dataclasses import dataclass, field, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Union, Optional, Any
from muagent.base_configs.env_config import EXTRA_KEYWORDS_PATH
from muagent.db_handler.graph_db_handler.base_gb_handler import GBHandler
from muagent.db_handler.vector_db_handler.tbase_handler import TbaseHandler
from muagent.schemas.ekg.ekg_graph import NodeTypesEnum
from muagent.schemas.common import GNode, GEdge
from muagent.llm_models.get_embedding import get_embedding
from muagent.utils.common_utils import double_hashing
from .intention_match_rule import MatchRule


class RouterStatus(Enum):
    SUCCESS = 'success'
    ZERO = 'noMatch'
    MORE_THAN_ONE = 'toChoose'
    OTHERS = 'fail'


@dataclass
class RuleRetInfo:
    node_id: str
    is_leaf: bool = False
    error_msg: str = ''
    status: str = RouterStatus.SUCCESS.value


@dataclass
class NLPRetInfo(RuleRetInfo):
    nodes_to_choose: Optional[list[dict]] = field(default=None)
    answer: Optional[str] = None


@dataclass
class ToChooseInfo:
    id: str
    description: str
    path: list[str] = field(default_factory=list)

    def __post_init__(self):
        self.path = ' -> '.join(self.path)


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
        # load custom keywords
        if os.path.exists(EXTRA_KEYWORDS_PATH):
            jieba.load_userdict(EXTRA_KEYWORDS_PATH)

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
        self, root_node_id: str, gb_handler: Optional[GBHandler] = None,
        rule: Union[Rule_type, list[Rule_type]] = None, **kwargs
    ) -> dict[str, Any]:
        gb_handler = gb_handler if gb_handler is not None else self.gb_handler

        is_leaf = False
        if len(kwargs) == 0:
            error_msg = 'No information in query to be matched.'
            return asdict(RuleRetInfo(
                node_id=root_node_id, error_msg=error_msg, status=RouterStatus.OTHERS.value
            ))

        args_list = _parse_kwargs(**kwargs)
        if not isinstance(rule, (list, tuple)):
            rule = [rule] * len(args_list)
        if len(rule) != len(args_list):
            error_msg = 'Length of rule should be equal to the length of Arguments.'
            return asdict(RuleRetInfo(
                node_id=root_node_id, error_msg=error_msg, status=RouterStatus.OTHERS.value
            ))

        if not (root_node_id and self._node_exist(root_node_id, gb_handler)):
            error_msg = f'Node(id={root_node_id}, type={self._node_type}) does not exist!'
            return asdict(RuleRetInfo(
                node_id=root_node_id, error_msg=error_msg, status=RouterStatus.OTHERS.value
            ))

        for cur_kw_arg, cur_rule in zip(args_list, rule):
            next_node_id, error_msg = self._get_intention_by_node_info_match(
                gb_handler, root_node_id, cur_rule, **cur_kw_arg)
            if next_node_id is None or next_node_id == root_node_id:
                is_leaf = True if next_node_id else False
                status = RouterStatus.SUCCESS.value if next_node_id else RouterStatus.OTHERS.value
                return asdict(RuleRetInfo(
                    node_id=root_node_id, is_leaf=is_leaf, error_msg=error_msg, status=status
                ))
            root_node_id = next_node_id

        next_node_id = root_node_id
        while next_node_id:
            root_node_id = next_node_id
            intention_nodes = gb_handler.get_neighbor_nodes({'id': next_node_id}, self._node_type)
            intention_nodes = [
                node for node in intention_nodes if node.type == self._node_type
            ]
            if len(intention_nodes) == 1:
                next_node_id = intention_nodes[0].id
                continue
            next_node_id, is_leaf = None, not intention_nodes

        status = RouterStatus.SUCCESS.value
        if not is_leaf:
            error_msg = 'Not enough to arrive the leaf node.'
            status = RouterStatus.OTHERS.value
        elif not self.is_node_valid(root_node_id, gb_handler):
            error_msg = 'No other types of nodes connected after the leaf node.'
            status = RouterStatus.OTHERS.value
        return asdict(RuleRetInfo(
            node_id=root_node_id, is_leaf=is_leaf, error_msg=error_msg, status=status
        ))

    def get_intention_by_node_info_nlp(
        self, root_node_id: str, query: str, start_from_root: bool = False, gb_handler: Optional[GBHandler] = None,
        tb_handler: Optional[TbaseHandler] = None, agent=None,
    ) -> dict[str, Any]:
        gb_handler = gb_handler if gb_handler is not None else self.gb_handler
        tb_handler = tb_handler if tb_handler is not None else self.tb_handler
        agent = agent if agent is not None else self.agent

        try:
            root_node = gb_handler.get_current_node({'id': root_node_id}, node_type=self._node_type)
            teamids = getattr(root_node, 'teamids')
            if teamids:
                teamids = [x.strip() for x in teamids.split(',')]
        except Exception:
            error_msg = f'Node(id={root_node_id}, type={self._node_type}) does not exist!'
            return asdict(NLPRetInfo(
                root_node_id, error_msg=error_msg, status=RouterStatus.OTHERS.value
            ))

        if start_from_root:
            return self._get_intention_by_nlp_from_root(gb_handler, agent, root_node, query)

        nodes_tb = self._tb_match(tb_handler, query, self._node_type, teamids)
        filter_nodes_tb = self._filter_ancestors(gb_handler, nodes_tb, root_node_id)

        filter_nodes = OrderedDict()
        for k, v in filter_nodes_tb.items():
            if not self.is_node_valid(k, gb_handler):
                continue
            name_v = []
            for node_id in v:
                node = gb_handler.get_current_node({'id': node_id}, node_type=self._node_type)
                name_v.append(getattr(node, 'name'))
            filter_nodes[k] = asdict(ToChooseInfo(k, getattr(node, 'description'), name_v))
        
        intention_idx = self._get_intention_ekg(
            query, [x['description'] for x in filter_nodes.values()], agent,
            allow_multiple_choice=True
        )
        filter_nodes = {k: v for i, (k, v) in enumerate(filter_nodes.items()) if i in intention_idx}

        if len(filter_nodes) == 0:
            error_msg = 'No intention matched after tb_handler retrieval.'
            return asdict(NLPRetInfo(
                root_node_id, error_msg=error_msg, status=RouterStatus.OTHERS.value
            ))
        elif len(filter_nodes) > 1:
            error_msg = 'More than one intention matched after tb_handler retrieval.'
            desc_list = list(filter_nodes.values())
            return asdict(NLPRetInfo(
                root_node_id, nodes_to_choose=desc_list, error_msg=error_msg,
                status=RouterStatus.MORE_THAN_ONE.value
            ))

        root_node_id = list(filter_nodes.keys())[0]
        root_node = gb_handler.get_current_node({'id': root_node_id}, self._node_type)
        return self._get_intention_by_nlp_from_root(gb_handler, agent, root_node, query)

    def get_intention_by_node_info(
        self, query: Union[str, list, tuple], root_node_id: str,
        rule: Union[str, list[str]], start_from_root=True
    ) -> dict[str, Any]:
        if rule == 'nlp' or rule[0] == 'nlp':
            if not isinstance(query, str):
                query = query[0]
            return self.get_intention_by_node_info_nlp(root_node_id, query, start_from_root)
        return self.get_intention_by_node_info_match(root_node_id, rule=rule, query=query)

    def _get_intention_by_nlp_from_root(
        self, gb_handler: GBHandler, agent, root_node: GNode, query: str
    ) -> dict[str, Any]:
        canditates_0 = gb_handler.get_neighbor_nodes({'id': root_node.id}, self._node_type)
        canditates = [n for n in canditates_0 if n.type == self._node_type]

        paths = [getattr(root_node, 'name')]
        while canditates:
            if len(canditates) == 1:
                root_node = canditates[0]
            else:
                desc_list = [getattr(x, 'description') for x in canditates]
                intention_list: list[int] = self._get_intention_ekg(query, desc_list, agent)
                if not intention_list:
                    error_msg = f'No intention matched at Node(id={root_node.id}).'
                    desc_list = [
                        asdict(ToChooseInfo(node.id, desc, paths.copy() + [getattr(node, 'name')]))
                        for node, desc in zip(canditates, desc_list)
                    ]
                    return asdict(NLPRetInfo(
                        root_node.id, error_msg=error_msg, status=RouterStatus.ZERO.value,
                        nodes_to_choose=desc_list
                    ))
                root_node = canditates[intention_list[0]]
            
            paths.append(getattr(root_node, 'name'))
            canditates_0 = gb_handler.get_neighbor_nodes({'id': root_node.id}, self._node_type)
            canditates = [n for n in canditates_0 if n.type == self._node_type]
        
        if not canditates_0:
            error_msg = 'No other types of nodes connected after the leaf node.'
            status = RouterStatus.OTHERS.value
            return asdict(NLPRetInfo(root_node.id, True, error_msg, status))
        return asdict(NLPRetInfo(root_node.id, True))

    def get_intention_whether_execute(self, query: str, agent=None) -> bool:
        agent = agent if agent else self.agent
        query = itp.WHETHER_EXECUTE_PROMPT.format(query=query)
        ans = agent.predict(query)
  
        ans = [int(x) - 1 for x in re.findall('\d+', ans) if 0 < int(x) <= len(itp.INTENTIONS_WHETHER_EXEC)]
        if ans:
            return itp.INTENTIONS_WHETHER_EXEC[ans[0]] is itp.INTENTION_EXECUTE
        return False

    def get_intention_consult_which(
        self, query: Union[list, tuple, str], agent=None, root_node_id: Optional[str]=None
    ) -> str:
        if isinstance(query, (list, tuple)):
            query = query[0]
        agent = agent if agent else self.agent
        query_consult_which = itp.CONSULT_WHICH_PROMPT.format(query=query)
        ans = agent.predict(query_consult_which)

        ans = [int(x) - 1 for x in re.findall('\d+', ans) if 0 < int(x) <= len(itp.INTENTIONS_CONSULT_WHICH)]
        if ans and itp.INTENTIONS_CONSULT_WHICH[ans[0]] is not itp.INTENTION_CHAT:
            return itp.INTENTIONS_CONSULT_WHICH[ans[0]].tag
        
        if root_node_id:
            out = self.get_intention_by_node_info_nlp(root_node_id, query, start_from_root=False)
            if out['status'] == RouterStatus.SUCCESS.value:
                return itp.INTENTION_ALLPLAN.tag
        return itp.INTENTION_CHAT.tag

    def _tb_match(self, tb_handler: TbaseHandler, query: str, node_type: str, teamids=None) -> set:
        def _filter_by_keyword(r, key: str, query_keyword: set):
            ret = []
            for tnode in r.docs:
                keyword = getattr(tnode, f'{key}_keyword')
                keyword = {x.strip().lower() for x in keyword.split('|')}
                if query_keyword.intersection(keyword):
                    ret.append(getattr(tnode, 'node_id'))
            return ret

        def _vector_search(prefix: str, query_vector: bytes, query_keyword: list, key: str):
            base_query = f'({prefix})=>[KNN {self._max_num_tb_retrieval} @{key}_vector $vector AS distance]'
            query_params = {"vector": query_vector}
            r = tb_handler.vector_search(base_query, query_params=query_params)
            return _filter_by_keyword(r, key, set(query_keyword))
        
        def _keyword_search(prefix: str, query_keyword: list, key: str):
            query_keyword_str = '|'.join(query_keyword)
            query = f'{prefix}(@{key}_keyword:{{{query_keyword_str}}})'
            r = tb_handler.search(query, limit=self._max_num_tb_retrieval)
            return _filter_by_keyword(r, key, set(query_keyword))

        prefix = f'(@node_type: {node_type})'
        if teamids:
            prefix_team = ''
            if isinstance(teamids, str):
                teamids = [teamids]
            prefix_team = ' OR '.join([f'(@node_str: *{x}*)' for x in teamids])
            if len(teamids) > 1:
                prefix_team = f'({prefix_team})'
            prefix = f'({prefix} AND {prefix_team})'

        keyword = [x.lower() for x in extract_tags(query)]
        keys, tb_results = ('description', 'name'), []
        if self.embed_config:
            query_vector = self._get_embedding(query)
            ret = _execute_func_distributed(
                _vector_search,
                [(prefix, query_vector, keyword, key) for key in keys]
            )
            for temp_ret in ret:
                tb_results.extend(temp_ret)
        
        ret = _execute_func_distributed(_keyword_search, [(prefix, keyword, key) for key in keys])
        for temp_ret in ret:
            tb_results.extend(temp_ret)

        return set(tb_results)

    def is_node_valid(self, node_id: str, gb_handler: Optional[GBHandler] = None) -> bool:
        gb_handler = gb_handler if gb_handler is not None else self.gb_handler
        canditates = gb_handler.get_neighbor_nodes({'id': node_id}, self._node_type)
        if len(canditates) == 0:
            return False
        canditates = [n.id for n in canditates if n.type == self._node_type]
        if len(canditates) == 0:
            return True
        return self.is_node_valid(canditates[0], gb_handler)
    
    def _get_intention_ekg(self, query: str, intentions: list[str], agent, allow_multiple_choice=False):
        if len(intentions) <= 1:
            return [0] * len(intentions)
        
        intentions = [itp.IntentionInfo(description=x) for x in intentions] + [itp.INTENTION_NOMATCH]
        query_intention = itp.get_intention_prompt(
            intentions, allow_multiple_choice=allow_multiple_choice).format(query=query)
        ans = agent.predict(query_intention)
        ans = [int(x) - 1 for x in re.findall('\d+', ans) if 0 < int(x) < len(intentions)]
        return ans

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

    def _node_exist(self, node_id: str, gb_handler: GBHandler):
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
    
    def _cat_id(*node_ids):
        node_ids = [x for x in node_ids if x]
        return '/'.join(node_ids)

    def intention_df2graph(
        self, data_df: pd.DataFrame, teamid: str, root_node_id: Optional[str] = None,
        gb_handler: Optional[GBHandler] = None, tb_handler: Optional[TbaseHandler] = None,
        embed_config=None, cat_root_node_id=True, delete_edge=False
    ) -> tuple[bool, str]:
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

        def _check_fail_num_gb(gb_results: list):
            try:
                ret = sum([
                    int(x["status"]["errorMessage"] not in ["GDB_SUCCEED"])
                    for x in gb_results
                ])
            except Exception:
                ret = 0
            return ret

        def _equal_left(node1: GNode, node2: GNode):
            for key in node1.__fields__:
                node1_val, node2_val = getattr(node1, key), getattr(node2, key)
                if isinstance(node1_val, dict):
                    for k, v in node1_val.items():
                        if k not in node2_val or v != node2_val[k]:
                            return False
                elif node1_val != node2_val:
                    return False
            return True

        gb_handler = gb_handler if gb_handler is not None else self.gb_handler
        tb_handler = tb_handler if tb_handler is not None else self.tb_handler
        embed_config = embed_config if embed_config is not None else self.embed_config

        absent_cols = _check_columns()
        if absent_cols:
            return False, 'Columns {} do not exist!'.format(', '.join(absent_cols))

        in_degrees, out_graphs = defaultdict(int), dict()
        for _, row in data_df.iterrows():
            if not row['child_ids']:
                row['child_ids'] = []
            for child_id in row['child_ids']:
                in_degrees[child_id] += 1
            out_graphs[row['id']] = row['child_ids']
        if _exist_cycle(in_degrees, out_graphs):
            return False, 'Cycle exists!'

        node_id2ID = dict()
        if root_node_id:
            try:
                ret = gb_handler.get_current_node({'id': root_node_id}, node_type=self._node_type)
                node_id2ID[root_node_id] = getattr(ret, 'ID')
            except IndexError:
                return False, f'Node(id={root_node_id}, type={self._node_type}) does not exist!'

        edge_type = f'{self._node_type}_extend_{self._node_type}'
        add_nodes, update_nodes, add_edges, del_edges = [], [], [], []
        for _, row in data_df.iterrows():
            node_id = self._cat_id(root_node_id, row['id']) if cat_root_node_id else row['id']
            node = GNode(
                id=node_id, type=self._node_type,
                attributes={'description': row['description'], 'name': row['name']}
            )
            try:
                ret: GNode = gb_handler.get_current_node({'id': node_id}, node_type=self._node_type)
                node.attributes['ID'] = getattr(ret, 'ID')
                if not _equal_left(node, ret):
                    update_nodes.append(node)
                child_nodes = gb_handler.get_neighbor_nodes({'id': node_id}, self._node_type)
                child_nodes = [node for node in child_nodes if node.type == self._node_type]
                del_edges.extend([
                    (getattr(node, 'ID'), getattr(child_node, 'ID'), edge_type)
                    for child_node in child_nodes
                ])
            except IndexError:
                node.attributes['ID'] = double_hashing(node_id)
                add_nodes.append(node)
            node_id2ID[node_id] = getattr(node, 'ID')

            if not in_degrees[row['id']] and root_node_id is not None:
                add_edges.append(GEdge(
                    start_id=root_node_id, end_id=node_id, type=edge_type,
                    attributes=dict(SRCID=node_id2ID[root_node_id], DSTID=node_id2ID[node_id])
                ))

        for _, row in data_df.iterrows():
            if not row['child_ids']:
                continue
            node_id = self._cat_id(root_node_id, row['id']) if cat_root_node_id else row['id']
            for child_id in row['child_ids']:
                child_id = self._cat_id(root_node_id, child_id) if cat_root_node_id else row['id']
                add_edges.append(GEdge(
                    start_id=node_id, end_id=child_id,
                    type=edge_type,
                    attributes=dict(SRCID=node_id2ID[node_id], DSTID=node_id2ID[child_id])
                ))

        from muagent.service.ekg_construct import EKGConstructService
        ekg_construct = EKGConstructService(embed_config=embed_config, llm_config=None)
        ekg_construct.gb = gb_handler
        ekg_construct.tb = tb_handler

        ret_add_nodes = ekg_construct.add_nodes(add_nodes, teamid=teamid, ekg_type=self._node_type)['gb_result']
        ret_update_nodes = ekg_construct.update_nodes(update_nodes, teamid=teamid)['gb_result']

        if delete_edge:
            ret_del_edges = _execute_func_distributed(gb_handler.delete_edge, del_edges)
        else:
            ret_del_edges = []
            del_edges = set([tuple(x[:2]) for x in del_edges])
            add_edges = [
                edge for edge in add_edges
                if (edge.attributes['SRCID'], edge.attributes['DSTID']) not in del_edges
            ]
        add_edges = ekg_construct._update_new_attr_for_edges(add_edges)
        ret_add_edges = _execute_func_distributed(gb_handler.add_edge, add_edges)

        status, error_msg = True, ''
        for gb_ret, prefix in zip(
            (ret_add_nodes, ret_update_nodes, ret_add_edges, ret_del_edges),
            ('Add Nodes', 'Update Nodes', 'Add Edges', 'Delete Edges')
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



def _execute_func_distributed(func: Callable, params: list[Any]):
    tasks = []
    with ThreadPoolExecutor(max_workers=16) as exec:
        for param in params:
            if isinstance(param, (tuple, list)):
                task = exec.submit(func, *param)
            elif isinstance(param, dict):
                task = exec.submit(func, **param)
            else:
                task = exec.submit(func, param)
            tasks.append(task)

    results = [task.result() for task in as_completed(tasks)]
    return results
