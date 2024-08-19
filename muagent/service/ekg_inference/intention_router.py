import re
import numpy as np
import muagent.base_configs.prompts.intention_template_prompt as itp
from loguru import logger
from dataclasses import dataclass, field, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Union, Optional, Any
from muagent.db_handler.graph_db_handler.base_gb_handler import GBHandler
from muagent.db_handler.vector_db_handler.tbase_handler import TbaseHandler
from muagent.schemas.ekg.ekg_graph import NodeTypesEnum, TYPE2SCHEMA
from muagent.schemas.common import GNode
from muagent.llm_models.get_embedding import get_embedding
from .intention_match_rule import rule_dict, MatchRule


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
    def __init__(self, agent=None, gb_handler: GBHandler=None, tb_handler: TbaseHandler=None, embed_config=None):
        self.agent = agent
        self.gb_handler = gb_handler
        self.tb_handler = tb_handler
        self.embed_config = embed_config
        self._node_type = NodeTypesEnum.INTENT.value
        self._max_num_tb_retrieval = 10
        self._filter_max_depth = 5

    def add_rule(self, node_id2rule: dict[str, str], gb_handler: Optional[GBHandler] = None):
        gb_handler = gb_handler if gb_handler is not None else self.gb_handler
        ori_len = len(rule_dict)
        fail_nodes, fail_rules = [], []
        for node_id, rule in node_id2rule.items():
            try:
               gb_handler.get_current_node({'id': node_id}, node_type=self._node_type)
            except IndexError:
                fail_nodes.append(node_id)
                continue

            rule_func = _get_rule_by_str(rule)
            if rule_func is None:
                fail_rules.append(node_id)
                continue

            rule_dict[node_id] = rule
        
        if len(rule_dict) > ori_len:
            rule_dict.save_to_odps()
        
        error_msg = ''
        if fail_nodes:
            error_msg += ', '.join([
                f'Node(id={node_id}, node_type={self._node_type})'
                for node_id in fail_nodes
            ])
            error_msg += ' do not exist! '
        if fail_rules:
            error_msg += 'Rule of '
            error_msg += ', '.join([
                f'Node(id={node_id}, node_type={self._node_type})'
                for node_id in fail_rules 
            ])
            error_msg += ' is not valid!'
        return error_msg

    def get_intention_by_info2id(self, gb_handler: GBHandler, rule: Union[str, Callable]=':', **kwargs) -> str:
        gb_handler = gb_handler if gb_handler is not None else self.gb_handler
        node_id = rule.join(kwargs.values()) if isinstance(rule, str) else rule(**kwargs)
        try:
            gb_handler.get_current_node({'id': node_id}, node_type=self._node_type)
        except IndexError:
            logger.error(f'Node(id={node_id}, node_type={self._node_type}) does not exist!')
            return None
        return node_id

    def _get_intention_by_node_info_match(
        self, gb_handler: GBHandler, root_node_id: str,
        rule: Rule_type = None, **kwargs
    ) -> str:
        def _func(node: GNode, rule: Callable):
            return rule(node, **kwargs), node.id

        error_msg, rule_str = '', rule
        if rule is None:
            if root_node_id in rule_dict:
                rule = rule_dict(root_node_id)
            else:
                rule = MatchRule.edit_distance
                rule_str = 'edit_distance'
        if isinstance(rule, str):
            rule = _get_rule_by_str(rule) 
            if isinstance(rule, str):
                try:
                    rule = getattr(MatchRule, rule)
                except AttributeError:
                    rule = None
            if rule is None:
                error_msg = f'Rule {rule_str} is not valid!'
                return None, error_msg

        intention_nodes = gb_handler.get_neighbor_nodes({'id': root_node_id}, self._node_type)
        intention_nodes = [node for node in intention_nodes if node.type == self._node_type]
        if len(intention_nodes) == 0:
            return root_node_id, error_msg
        elif len(intention_nodes) == 1:
            return intention_nodes[0].id, error_msg
        elif len(intention_nodes) < 20:
            scores = [_func(node, rule) for node in intention_nodes]
        else:
            params = [(node, rule) for node in intention_nodes]
            scores = _execute_func_distributed(_func, params)

        return max(scores)[-1], error_msg

    def get_intention_by_node_info_match(
        self, root_node_id: str, filter_attribute: Optional[dict]=None, gb_handler: Optional[GBHandler] = None,
        rule: Union[Rule_type, list[Rule_type]]=None, **kwargs
    ) -> dict[str, Any]:
        gb_handler = gb_handler if gb_handler is not None else self.gb_handler
        root_node_id = self._filter_from_root_node(gb_handler, root_node_id, filter_attribute)

        is_leaf = False
        if len(kwargs) == 0:
            error_msg = 'No information in query to be matched.'
            return asdict(RuleRetInfo(node_id=root_node_id, error_msg=error_msg))

        args_list = _parse_kwargs(**kwargs)
        if not isinstance(rule, (list, tuple)):
            rule = [rule] * len(args_list)
        if len(rule) != len(args_list):
            error_msg = 'Length of rule should be equal to the length of Arguments.'
            return asdict(RuleRetInfo(node_id=root_node_id, error_msg=error_msg))

        if not root_node_id:
            error_msg = f'No node matches attribute {filter_attribute}.'
            return asdict(RuleRetInfo(node_id=root_node_id, error_msg=error_msg))

        for cur_kw_arg, cur_rule in zip(args_list, rule):
            next_node_id, error_msg = self._get_intention_by_node_info_match(
                gb_handler, root_node_id, cur_rule, **cur_kw_arg
            )
            if next_node_id is None or next_node_id == root_node_id:
                is_leaf = True if next_node_id else False
                return asdict(RuleRetInfo(node_id=root_node_id, is_leaf=is_leaf, error_msg=error_msg))
            root_node_id = next_node_id

        next_node_id = root_node_id
        while next_node_id:
            root_node_id = next_node_id
            intention_nodes = gb_handler.get_neighbor_nodes({'id': next_node_id}, self._node_type)
            intention_nodes = [
                node for node in intention_nodes
                if node.type == self._node_type
            ]
            if len(intention_nodes) == 1:
                next_node_id = intention_nodes[0].id
            else:
                next_node_id = None
                if len(intention_nodes) == 0:
                    is_leaf = True
        
        if not is_leaf:
            error_msg = 'Not enough to arrive the leaf node.'
        return asdict(RuleRetInfo(node_id=root_node_id, is_leaf=is_leaf, error_msg=error_msg))

    def get_intention_by_node_info_nlp(
        self, root_node_id: str, query: str, start_from_root: bool = False,
        gb_handler: Optional[GBHandler] = None, tb_handler: Optional[TbaseHandler] = None, agent=None,
    ) -> dict[str, Any]:
        gb_handler = gb_handler if gb_handler is not None else self.gb_handler
        tb_handler = tb_handler if tb_handler is not None else self.tb_handler
        agent = agent if agent is not None else self.agent

        if start_from_root:
            return self._get_intention_by_nlp_from_root(gb_handler, agent, root_node_id, query)

        nodes_tb = self._tb_match(tb_handler, query, self._node_type)
        filter_nodes_tb = self._filter_ancestors_hop(gb_handler, set(nodes_tb), root_node_id)

        filter_nodes_tb = {
            k: v for k, v in filter_nodes_tb.items()
            if self.is_node_valid(gb_handler, k)
        }

        if len(filter_nodes_tb) == 0:
            error_msg = 'No intention matched after tb_handler retrieval.'
            ans = self._get_agent_ans_no_ekg(agent, query)
            return asdict(NLPRetInfo(root_node_id, answer=ans, error_msg=error_msg))
        elif len(filter_nodes_tb) > 1:
            error_msg = 'More than one intention matched after tb_handler retrieval.'
            desc_list = []
            for k, v in filter_nodes_tb.items():
                node_desc = gb_handler.get_current_node({'id': k}, node_type=self._node_type)
                node_desc = node_desc.attributes.get('description', '')
                desc_list.append({'description': node_desc, 'path': ' -> '.join(v)})
            return asdict(NLPRetInfo(root_node_id, nodes_to_choose=desc_list, error_msg=error_msg))

        root_node_id = list(filter_nodes_tb.keys())[0]
        return self._get_intention_by_nlp_from_root(gb_handler, agent, root_node_id, query)

    def _get_intention_by_nlp_from_root(
        self, gb_handler: GBHandler, agent, root_node_id: str, query: str,
    ) -> dict[str, Any]:
        canditates = gb_handler.get_neighbor_nodes({'id': root_node_id}, self._node_type)
        canditates = [n for n in canditates if n.type == self._node_type]
        if len(canditates) == 0:
            return asdict(NLPRetInfo(root_node_id, True))
        elif len(canditates) == 1:
            root_node_id = canditates[0].id
            return self._get_intention_by_nlp_from_root(gb_handler, agent, root_node_id, query)

        desc_list = [x.attributes.get('description', '') for x in canditates]
        desc_list.append('与上述意图都不匹配，属于其他类型的询问意图。')
        query_intention = itp.get_intention_prompt(
            '作为运维领域的客服，您需要根据用户询问判断其主要意图，以确定接下来的运维流程。', desc_list
        ).format(query=query)

        ans = agent.predict(query_intention).strip()
        ans = re.search('\d+', ans)
        if ans:
            ans = int(ans.group(0)) - 1
            if ans < len(desc_list) - 1:
                root_node_id = canditates[ans].id
                return self._get_intention_by_nlp_from_root(gb_handler, agent, root_node_id, query)

        error_msg = f'No intention matched at Node(id={root_node_id}).'
        ans = self._get_agent_ans_no_ekg(agent, query)
        return asdict(NLPRetInfo(root_node_id, answer=ans, error_msg=error_msg))

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
            {'id': root_node_id}, self._node_type, hop=self._filter_max_depth,
        ).nodes
        canditates = [node for node in canditates if node.type == self._node_type]

        for node in canditates:
            count = len(attribute)
            for k, v in attribute.items():
                if v in getattr(node, k):
                    count -= 1
            if not count:
                return node.id

        return None

    def _tb_match(self, tb_handler: TbaseHandler, query: str, node_type: str) -> list:
        base_query = f'(*)=>[KNN {self._max_num_tb_retrieval} @desc_vector $query AS distance]'

        query_vector = get_embedding(
            self.embed_config.embed_engine, [query],
            self.embed_config.embed_model_path, self.embed_config.model_device,
            self.embed_config
        )[query]

        query_params = {'query': np.array(query_vector).astype(dtype=np.float32).tobytes()}

        canditates = tb_handler.vector_search(
            base_query, limit=self._max_num_tb_retrieval, query_params=query_params
        ).docs
        canditates = [
            node.node_id for node in canditates
            if node.node_type == node_type
        ]
        return canditates

    def is_node_valid(self, node_id: str, gb_handler: Optional[GBHandler] = None) -> bool:
        gb_handler = gb_handler if gb_handler is not None else self.gb_handler
        canditates = gb_handler.get_neighbor_nodes({'id': node_id}, self._node_type)
        if len(canditates) == 0:
            return False
        canditates = [n.id for n in canditates if n.type == self._node_type]
        if len(canditates) == 0:
            return True
        return self.is_node_valid(gb_handler, canditates[0])

    def _get_agent_ans_no_ekg(self, agent, query: str) -> str:
        query = itp.DIRECT_CHAT_PROMPT.format(query=query)
        ans = agent.predict(query).strip()
        ans += f'\n\n以上内容由语言模型生成，仅供参考。'
        return ans
    
    def _filter_ancestors_hop(
        self, gb_handler: GBHandler, nodes: set, root_node: str
    ) -> dict[str, list[str]]:
        gb_ret = gb_handler.get_hop_infos(
            {'id': root_node}, self._node_type, hop=self._filter_max_depth,
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
    
    def _filter_ancestors(
        self, gb_handler: GBHandler, nodes: set, root_node: str
    ) -> dict[str, list[str]]:
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


def _get_rule_by_str(rule: str) -> Union[str, Callable]:
    has_func = re.search('def ([a-zA-Z0-9_]+)\(.*\):', rule)
    if not has_func:
        return getattr(MatchRule, rule.strip())
    
    func_name = has_func.group(1)
    try:
        exec(rule)
    except Exception as e:
        logger.info(f'Rule {rule} cannot be executed!')
        logger.error(e)
        return None

    return locals().get(func_name, None)
