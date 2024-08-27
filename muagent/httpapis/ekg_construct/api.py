from fastapi import FastAPI
from typing import Dict
import asyncio
import uvicorn
from loguru import logger

from muagent.service.ekg_construct.ekg_construct_base import EKGConstructService
from muagent.schemas.apis.ekg_api_schema import *


# 
# def init_app(llm, embeddings, ekg_construct_service: EKGConstructService):
def init_app(llm, embeddings):

    app = FastAPI()

    # ~/llm/params
    @app.get("/llm/params", response_model=LLMParamsResponse)
    async def llm_params():
        return llm.params()

    # ~/llm/params
    @app.post("/llm/generate", response_model=LLMResponse)
    async def llm_predict(request: LLMRequest):
        # 添加预测逻辑的代码
        errorMessage = "ok"
        successCode = True
        try:
            answer = llm.predict(request.text, request.stop)
        except Exception as e:
            errorMessage = str(e)
            successCode = False
            answer = "error"
            
        return LLMResponse(
            successCode=successCode, errorMessage=errorMessage,
            answer=answer
        )

    # ~/llm/params/update
    @app.post("/llm/params/update", response_model=EKGResponse)
    async def update_llm_params(kwargs: Dict):
        # 添加预测逻辑的代码
        errorMessage = "ok"
        successCode = True
        try:
            llm.update_params(**kwargs)
        except Exception as e:
            errorMessage = str(e)
            successCode = False
            
        return EKGResponse(
            successCode=successCode, errorMessage=errorMessage,
        )

    # ~/embeddings/params
    @app.get("/embeddings/params", response_model=EmbeddingsParamsResponse)
    async def embedding_params():
        return embeddings.params()

    # ~/embeddings/params/update
    @app.post("/embeddings/params/update", response_model=EKGResponse)
    async def update_embedding_params(kwargs: Dict):
        # 添加预测逻辑的代码
        errorMessage = "ok"
        successCode = True
        try:
            embeddings.update_params(**kwargs)
        except Exception as e:
            errorMessage = str(e)
            successCode = False
            
        return EKGResponse(
            successCode=successCode, errorMessage=errorMessage,
        )
    
    @app.post("/embeddings/generate", response_model=EmbeddingsResponse)
    async def embedding_predict(request: EmbeddingsRequest):
        # 添加预测逻辑的代码
        errorMessage = "ok"
        successCode = True
        try:
            embeddings_list = embeddings.embed_documents(request.texts)
        except Exception as e:
            logger.exception(e)
            errorMessage = str(e)
            successCode = False
            embeddings_list = []
            
        return EmbeddingsResponse(
            successCode=successCode, errorMessage=errorMessage,
            embeddings=embeddings_list
        )
    # # ~/ekg/text2graph
    # @app.post("/ekg/text2graph", response_model=EKGGraphResponse)
    # async def text2graph(request: EKGT2GRequest):
    #     # 添加预测逻辑的代码
    #     errorMessage = "ok"
    #     successCode = True
    #     try:
    #         result = ekg_construct_service.create_ekg(
    #             text=request.text, teamid=request.teamid,
    #             service_name="text2graph",
    #             intent_text=request.intentText,
    #             intent_nodes=request.intentNodeids,
    #             all_intent_list=request.intentPath,
    #             do_save=request.write2kg
    #         )
    #         graph = result["graph"]
    #         nodes = [node.dict() for node in graph.nodes]
    #         edges = [edge.dict() for edge in graph.edges]
    #     except Exception as e:
    #         errorMessage = str(e)
    #         successCode = False
    #         nodes = []
    #         edges = []
            
    #     return EKGGraphResponse(
    #         successCode=successCode, errorMessage=errorMessage,
    #         nodes=nodes, edges=edges
    #     )


    # # ~/ekg/graph/update
    # @app.post("/ekg/graph/update", response_model=EKGResponse)
    # async def update_graph(request: UpdateGraphRequest):
    #     # 添加预测逻辑的代码
    #     errorMessage = "ok"
    #     successCode = True
    #     try:
    #         result = ekg_construct_service.update_graph(
    #             origin_nodes=request.originNodes,
    #             origin_edges=request.originEdges,
    #             nodes=request.nodes,
    #             edges=request.edges,
    #             teamid=request.teamid
    #         )
    #     except Exception as e:
    #         errorMessage = str(e)
    #         successCode = False
            
    #     return EKGResponse(
    #         successCode=successCode, errorMessage=errorMessage,
    #     )



    # # ~/ekg/node/search
    # @app.get("/ekg/node", response_model=GetNodeResponse)
    # def get_node(request: GetNodeRequest):
    #     # 添加预测逻辑的代码
    #     errorMessage = "ok"
    #     successCode = True
    #     try:
    #         node = ekg_construct_service.get_node_by_id(
    #             request.node_id, request.node_type
    #         )
    #         node = node.dict()
    #     except Exception as e:
    #         errorMessage = str(e)
    #         successCode = False
    #         node = {}
            
    #     return GetNodeResponse(
    #         successCode=successCode, errorMessage=errorMessage,
    #         node=node
    #     )


    # # ~/ekg/node/search
    # @app.get("/ekg/graph", response_model=EKGGraphResponse)
    # def get_graph(request: GetGraphRequest):
    #     # 添加预测逻辑的代码
    #     errorMessage = "ok"
    #     successCode = True
    #     try:
    #         if request.layer == "first":
    #             graph = ekg_construct_service.get_graph_by_nodeid(
    #                 nodeid=request.nodeid, node_type=request.nodeType, 
    #                 hop=8, block_attributes={"type": "opsgptkg_task"})
    #         else:
    #             graph = ekg_construct_service.get_graph_by_nodeid(
    #                 nodeid=request.nodeid, node_type=request.nodeType, 
    #                 hop=request.hop
    #             )
    #         nodes = graph.nodes.dict()
    #         edges = graph.edges.dict()
    #     except Exception as e:
    #         errorMessage = str(e)
    #         successCode = False
    #         nodes, edges = {}, {}
            
    #     return EKGGraphResponse(
    #         successCode=successCode, errorMessage=errorMessage,
    #         nodes=nodes, edges=edges
    #     )



    # # ~/ekg/node/search
    # @app.post("/ekg/node/search", response_model=GetNodesResponse)
    # def search_node(request: SearchNodesRequest):
    #     # 添加预测逻辑的代码
    #     errorMessage = "ok"
    #     successCode = True
    #     try:
    #         nodes = ekg_construct_service.search_nodes_by_text(
    #             request.text, teamid=request.teamid
    #         )
    #         nodes = [node.dict() for node in nodes]
    #     except Exception as e:
    #         errorMessage = str(e)
    #         successCode = False
    #         nodes = []
            
    #     return GetNodesResponse(
    #         successCode=successCode, errorMessage=errorMessage,
    #         nodes=nodes
    #     )

    # # ~/ekg/graph/ancestor
    # @app.get("/ekg/graph/ancestor", response_model=EKGGraphResponse)
    # def get_ancestor(request: SearchAncestorRequest):
    #     # 添加预测逻辑的代码
    #     errorMessage = "ok"
    #     successCode = True
    #     try:
    #         graph = ekg_construct_service.search_rootpath_by_nodeid(
    #             nodeid=request.nodeid, node_type=request.nodeType, 
    #             rootid=request.rootid
    #         )
    #         nodes = graph.nodes.dict()
    #         edges = graph.edges.dict()
    #     except Exception as e:
    #         errorMessage = str(e)
    #         successCode = False
    #         nodes, edges = {}, {}
            
            
    #     return EKGGraphResponse(
    #         successCode=successCode, errorMessage=errorMessage,
    #         nodes=nodes, edges=edges
    #     )

    return app


def create_api(llm, embeddings):
    app = init_app(llm, embeddings)
    uvicorn.run(app, host="localhost", port=3737)

# def create_api(ekg_construct_service: EKGConstructService):
#     app = init_app(ekg_construct_service)
#     uvicorn.run(app, host="localhost", port=3737)
