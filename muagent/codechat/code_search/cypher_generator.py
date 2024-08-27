# encoding: utf-8
'''
@author: 温进
@file: cypher_generator.py
@time: 2023/11/24 上午10:17
@desc:
'''
from langchain.prompts import PromptTemplate
from loguru import logger

from muagent.llm_models.openai_model import getChatModelFromConfig
from muagent.llm_models.llm_config import LLMConfig
from muagent.utils.postprocess import replace_lt_gt
from muagent.db_handler.graph_db_handler.nebula_handler import NebulaHandler
from langchain.schema import (
    HumanMessage,
)
# from langchain.chains.graph_qa.prompts import NGQL_GENERATION_PROMPT, CYPHER_GENERATION_TEMPLATE
from langchain_community.chains.graph_qa.prompts import CYPHER_GENERATION_TEMPLATE

schema = '''
Node properties: [{'tag': 'package', 'properties': []}, {'tag': 'class', 'properties': []}, {'tag': 'method', 'properties': []}]
Edge properties: [{'edge': 'contain', 'properties': []}, {'edge': 'depend', 'properties': []}]
Relationships: ['(:package)-[:contain]->(:class)', '(:class)-[:contain]->(:method)', '(:package)-[:contain]->(:package)']
'''


class CypherGenerator:
    # TODO 这里应该是将图数据库的信息填入到默认的schema中property的，但没成果，不知道为什么
    def __init__(self, llm_config: LLMConfig, nh: NebulaHandler):
        self.model = getChatModelFromConfig(llm_config)
        self.nh = nh

        # try:
        #     resp = self.nh.cypher_info()
        # except Exception as e:
        #     print(e)
        #     logger.error(f"{e}")

        NEBULAGRAPH_EXTRA_INSTRUCTIONS = """
        Instructions:

        First, generate cypher then convert it to NebulaGraph Cypher dialect(rather than standard):
        1. it requires explicit label specification only when referring to node properties: v.`Foo`.name
        2. note explicit label specification is not needed for edge properties, so it's e.name instead of e.`Bar`.name
        3. it uses double equals sign for comparison: `==` rather than `=`
        4. only use id(Foo) to get the name of node or edge
        ```\n"""

        NGQL_GENERATION_TEMPLATE = CYPHER_GENERATION_TEMPLATE.replace(
            "Generate Cypher", "Generate NebulaGraph Cypher"
        ).replace("Instructions:", NEBULAGRAPH_EXTRA_INSTRUCTIONS)

        self.NGQL_GENERATION_PROMPT = PromptTemplate(
            input_variables=["schema", "question"], template=NGQL_GENERATION_TEMPLATE
        )
        # print(self.NGQL_GENERATION_PROMPT)

    def get_cypher(self, query: str):
        '''
        get cypher from query
        @param query:
        @return:
        '''
        schema = self.nh.cypher_info()
        content = self.NGQL_GENERATION_PROMPT.format(schema=schema, question=query)
        # logger.info(content)
        ans = ''
        message = [HumanMessage(content=content)]
        # chat_res = self.model.predict_messages(message)
        # ans = chat_res.content

        ans = replace_lt_gt(ans)

        ans = self.model(message)
        ans = self.post_process(ans)
        return ans

    def post_process(self, cypher_res: str):
        '''
        判断是否为正确的 cypher
        @param cypher_res:
        @return:
        '''
        if '(' not in cypher_res or ')' not in cypher_res:
            return ''

        return cypher_res


if __name__ == '__main__':
    query = '代码库里有哪些函数，返回5个就可以'
    cg = CypherGenerator()

    ans = cg.get_cypher(query)
    logger.debug(f'ans=\n{ans}')
