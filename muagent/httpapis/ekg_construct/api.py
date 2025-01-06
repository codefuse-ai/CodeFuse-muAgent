from fastapi import FastAPI
from typing import Dict
import uvicorn
from loguru import logger
import ollama
import json
import os

from muagent.service.ekg_construct.ekg_construct_base import EKGConstructService
from muagent.schemas.apis.ekg_api_schema import *
from muagent.schemas.ekg import *
from muagent.service.utils import decode_biznodes, encode_biznodes
from muagent.service.ekg_reasoning.src.graph_search.graph_search_main import main


def wrapping_reponse(result, errorMessage="ok", success=0):
    return EKGAIResponse(
        resultMap=EKGALResponse(
            algorithmResult=json.dumps(result.dict(), ensure_ascii=False)),
        debugMessage="",
        errorMessage=errorMessage,
        serverIp="",
        success=success
    )

def autofill_nodes(nodes: List[GNode]):
    '''
    兼容
    '''
    new_nodes = []
    for node in nodes:
        schema = TYPE2SCHEMA.get(node.type,)
        node.attributes.update(node.attributes.pop("extra", {}))
        node_data = schema(
            **{**{"id": node.id, "type": node.type}, **node.attributes}
        )
        node_data = {
            k:v
            for k, v in node_data.dict().items()
            if k not in ["type", "ID", "id", "extra"]
        }
        new_nodes.append(GNode(**{
            "id": node.id, 
            "type": node.type,
            "attributes": {**node_data, **node.attributes}
        }))
    return new_nodes
    
# 
def init_app(
        llm, 
        llm_config, 
        embeddings, 
        ekg_construct_service: EKGConstructService, 
        memory_manager, 
        geabase_handler, 
        intention_router
):

    app = FastAPI()

    # ~/llm/params
    @app.get("/llm/params", response_model=LLMParamsResponse)
    async def llm_params():
        return llm.params()

    # ~/llm/ollama/pull
    @app.post("/llm/ollama/pull", response_model=EKGResponse)
    async def llm_params(request: LLMOllamaPullRequest):
        result = ollama.pull(request.model_name)
        return EKGResponse(
            successCode=True, errorMessage=json.dumps(result, ensure_ascii=False),
        )
    
    # ~/llm/params/update
    @app.post("/llm/params/update", response_model=EKGResponse)
    async def update_llm_params(request: LLMParamsRequest):
        # 添加预测逻辑的代码
        errorMessage = "ok"
        successCode = True
        try:
            model_names = [i["name"] for i in ollama.list()["models"]]
            if request.model_type=="ollama" and request.model_name not in model_names:
                errorMessage = f"{request.model_name} not in ollama.list {model_names}. " \
                f"please request llm/ollama/pull for downloading the ollama model"
                successCode = False
            else:
                kwargs = {
                    k: v for k, v in request.dict().items()
                    if not (k=="stop" or v is None )
                }
                os.environ["API_BASE_URL"] = request.url or os.environ["API_BASE_URL"]
                llm.update_params(**kwargs)
        except Exception as e:
            errorMessage = str(e)
            successCode = False
            
        return EKGResponse(
            successCode=successCode, errorMessage=errorMessage,
        )

    # ~/llm/generate
    @app.post("/llm/generate", response_model=LLMResponse)
    async def update_llm_params(request: LLMRequest):
        # 添加预测逻辑的代码
        errorMessage = "ok"
        successCode = True
        answer = ""
        try:
            model_names = [i["name"] for i in ollama.list()["models"]]
            if llm.model_type=="ollama" and llm.model_name not in model_names:
                errorMessage = f"{llm.model_name} not in ollama.list {model_names}. " \
                f"please request llm/ollama/pull for downloading the ollama model"
                successCode = False
            else:
                answer = llm.predict(request.text, request.stop)
        except Exception as e:
            logger.exception(e)
            errorMessage = str(e)
            successCode = False
            
        return LLMResponse(
            successCode=successCode, errorMessage=errorMessage,
            answer=answer
        )
    
    # ~/llm/generate
    @app.post("/functioncall/chat", response_model=LLMFCResponse)
    async def fc_chat(request: LLMFCRequest):
        # 添加预测逻辑的代码
        errorMessage = "ok"
        successCode = True
        choices = []
        try:
            model_names = [i["name"] for i in ollama.list()["models"]]
            if llm.model_type=="ollama" and llm.model_name not in model_names:
                errorMessage = f"{llm.model_name} not in ollama.list {model_names}. " \
                f"please request llm/ollama/pull for downloading the ollama model"
                successCode = False
            else:
                fc_output = llm.fc(request)
                choices = fc_output.choices
        except Exception as e:
            logger.exception(e)
            errorMessage = str(e)
            successCode = False
            
        logger.info(f"choices.type: {type(choices)}")
        logger.info(f"choices {choices}")
        return LLMFCResponse(
            successCode=successCode, errorMessage=errorMessage,
            choices=choices
        )
    
    # ~/embeddings/params
    @app.get("/embeddings/params", response_model=EmbeddingsParamsResponse)
    async def embedding_params():
        return embeddings.params()

    # ~/embeddings/params/update
    @app.post("/embeddings/params/update", response_model=EKGResponse)
    async def update_embedding_params(request: EmbeddingsParamsRequest):
        # 添加预测逻辑的代码
        errorMessage = "ok"
        successCode = True
        try:
            model_names = [i["name"] for i in ollama.list()["models"]]
            if request.embedding_type=="ollama" and request.model_name not in model_names:
                errorMessage = f"{request.model_name} not in ollama.list {model_names}. " \
                f"please request llm/ollama/pull for downloading the ollama model"
                successCode = False
            else:
                kwargs = {
                        k: v for k, v in request.dict().items()
                        if not (k=="stop" or v is None )
                    }
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
            model_names = [i["name"] for i in ollama.list()["models"]]
            if embeddings.embedding_type=="ollama" and embeddings.model_name not in model_names:
                errorMessage = f"{embeddings.model_name} not in ollama.list {model_names}. " \
                f"please request llm/ollama/pull for downloading the ollama model"
                successCode = False
            else:
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
    
    # ~/ekg/text2graph
    @app.post("/ekg/text2graph", response_model=EKGGraphResponse)
    async def text2graph(request: EKGT2GRequest):
        # 添加预测逻辑的代码
        errorMessage = "ok"
        successCode = True
        try:
            result = ekg_construct_service.create_ekg(
                text=request.text, teamid=request.teamid,rootid=request.rootid,
                service_name="text2graph",
                intent_text=request.intentText,
                intent_nodes=request.intentNodeids,
                all_intent_list=request.intentPath,
                do_save=request.write2kg
            )
            graph = result["graph"]
            nodes = [node.dict() for node in graph.nodes]
            edges = [edge.dict() for edge in graph.edges]
        except Exception as e:
            errorMessage = str(e)
            successCode = False
            nodes = []
            edges = []
            
        return EKGGraphResponse(
            successCode=successCode, errorMessage=errorMessage,
            nodes=nodes, edges=edges
        )


    # ~/ekg/graph/update
    @app.post("/ekg/graph/update", response_model=EKGAIResponse)
    async def update_graph(request: EKGFeaturesRequest):
        logger.info(request.features.query)

        # 解析 origin_nodes 和 nodes，构建 nodeid 到 type 的映射
        origin_nodes = request.features.query.get('originNodes', [])
        nodes = request.features.query.get('nodes', [])
        origin_edges = request.features.query.get('originEdges', [])
        edges = request.features.query.get('edges', [])

        # 将 origin_nodes 和 nodes 转换为 GNode 对象
        origin_nodes = [GNode(**n) for n in origin_nodes]
        # origin_nodes = autofill_nodes(origin_nodes)
        origin_nodes, origin_new_edges = decode_biznodes(origin_nodes)
        nodes = [GNode(**n) for n in nodes]
        # nodes = autofill_nodes(nodes)
        nodes, new_edges = decode_biznodes(nodes)

        origin_edges.extend([e.dict() for e in origin_new_edges])
        edges.extend([e.dict() for e in new_edges])
                                      
        # 构建 nodeid 到 type 的字典，方便后续查找
        nodeid2type_dict = {n.id: n.type for n in origin_nodes + nodes}

        # 处理 origin_edges，给每个 edge 设置 type 字段
        origin_edges = [
            GEdge(
                start_id=e['start_id'], 
                end_id=e['end_id'],
                 # 使用默认值 'unknown' 以防 id 不在字典中
                type=f"{nodeid2type_dict.get(e['start_id'], 'unknown')}_route_{nodeid2type_dict.get(e['end_id'], 'unknown')}",
                attributes=e.get("attributes", {})
            )
            for e in origin_edges
        ]

        # 处理 edges，给每个 edge 设置 type 字段
        edges = [
            GEdge(
                start_id=e['start_id'], 
                end_id=e['end_id'],
                type=f"{nodeid2type_dict.get(e['start_id'], 'unknown')}_route_{nodeid2type_dict.get(e['end_id'], 'unknown')}",
                attributes=e.get("attributes", {})
            )
            for e in edges
        ]

        # 添加预测逻辑的代码
        errorMessage = "ok"
        successCode = True
        try:

            old_graph, result = ekg_construct_service.update_graph(
                origin_nodes=origin_nodes,
                origin_edges=origin_edges,
                new_nodes=nodes,
                new_edges=edges,
                teamid=request.features.query.get("teamid"),
                rootid=request.features.query.get("rootNodeId")
            )
            old_nodes = [n.dict() for n in old_graph.nodes]
            old_edges = [e.dict() for e in old_graph.edges]
        except Exception as e:
            logger.exception(e)
            errorMessage = str(e)
            successCode = False
            old_nodes = []
            old_edges = []
            
        result = UpdateGraphResponse(
            successCode=successCode, errorMessage=errorMessage,
            nodes=old_nodes,edges=old_edges
        )
        return wrapping_reponse(result)

    # ~/ekg/node
    @app.post("/ekg/node", response_model=EKGAIResponse)
    def get_node(request: EKGFeaturesRequest):

        query = GetNodeRequest(**request.features.query)
        # 添加预测逻辑的代码
        errorMessage = "ok"
        successCode = True
        try:
            node = ekg_construct_service.get_node_by_id(
                query.nodeid, query.nodeType
            )
            # might lost agents and tools
        except Exception as e:
            errorMessage = str(e)
            successCode = False
            node = None

        result = GetNodeResponse(
            successCode=successCode, errorMessage=errorMessage,node=node
        )
        return wrapping_reponse(result)


    # ~/ekg/graph
    @app.post("/ekg/graph", response_model=EKGAIResponse)
    def get_graph(request: EKGFeaturesRequest):
        query = GetGraphRequest(**request.features.query)

        # 添加预测逻辑的代码
        errorMessage = "ok"
        successCode = True
        try:
            if query.layer == "first":
                graph = ekg_construct_service.get_graph_by_nodeid(
                    nodeid=query.nodeid, node_type=query.nodeType, 
                    hop=12, block_attributes=[{"type": "opsgptkg_task"}, {"type": "opsgptkg_analysis"}, {"type": "opsgptkg_phenomenon"}])
            else:
                graph = ekg_construct_service.get_graph_by_nodeid(
                    nodeid=query.nodeid, node_type=query.nodeType, 
                    hop=query.hop
                )
            nodes = graph.nodes
            edges = graph.edges
            nodes, edges = encode_biznodes(nodes, edges)
        except Exception as e:
            errorMessage = str(e)
            successCode = False
            nodes, edges = [], []
            
        result = EKGGraphResponse(
            successCode=successCode, errorMessage=errorMessage,
            nodes=nodes, edges=edges
        )
    
        return wrapping_reponse(result)

    # ~/ekg/node/search
    @app.post("/ekg/node/search", response_model=EKGAIResponse)
    def search_node(request: EKGFeaturesRequest):
        query = SearchNodesRequest(**request.features.query)
        
        print(f"search_nodes_by_text function: {ekg_construct_service.search_nodes_by_text}")
        # 添加预测逻辑的代码
        errorMessage = "ok"
        successCode = True
        try:
            nodes = ekg_construct_service.search_nodes_by_text(
                query.text, teamid=query.teamid
            )
            nodes = [node.dict() for node in nodes]
        except Exception as e:
            logger.exception(e)
            errorMessage = str(e)
            successCode = False
            nodes = []
            
        result = GetNodesResponse(
            successCode=successCode, errorMessage=errorMessage,
            nodes=nodes
        )

        return wrapping_reponse(result)

    # ~/ekg/graph/ancestor
    @app.post("/ekg/graph/ancestor", response_model=EKGAIResponse)
    def get_ancestor(request: EKGFeaturesRequest):
        query = SearchAncestorRequest(**request.features.query)

        # 添加预测逻辑的代码
        errorMessage = "ok"
        successCode = True
        try:
            graph = ekg_construct_service.search_rootpath_by_nodeid(
                nodeid=query.nodeid, node_type=query.nodeType, 
                rootid=query.rootid
            )
            nodes = graph.nodes
            edges = graph.edges
            nodes, edges = encode_biznodes(nodes, edges)
        except Exception as e:
            errorMessage = str(e)
            successCode = False
            nodes, edges = [], []
            
            
        result = EKGGraphResponse(
            successCode=successCode, errorMessage=errorMessage,
            nodes=nodes, edges=edges
        )

        return wrapping_reponse(result)



    # ~/ekg/graph/ekg_migration_reasoning
    @app.post("/ekg/graph/ekg_migration_reasoning", response_model=EKGMigrationSeasoningResponse)
    #def ekg_migration_reasoning(request:dict):
    def ekg_migration_reasoning(request: EKGFeaturesRequest):

        query = request.features.query
        # logger.info(f'request is {request}, type(request) is {type(request)}')
        # feature = request.get('features', {})
        
        # query = feature.get('query', None)
        
        # if query is not None:
        #     # 进一步处理 query
        #     print(f"Query: {query}")
        # elif feature == {}:
        #     raise KeyError("feature' is missing in the request dictionary.")
        # elif query == None:
        #     raise KeyError("The 'query' key is missing in the 'feature' dictionary")

        try:
            logger.info('query={}'.format(query))
            # try:
            # query_ = json.loads(query)

            result =  main(query,  memory_manager, geabase_handler, intention_router, llm_config)
            if type(result) != str:
                result = json.dumps(result,  ensure_ascii=False)

            resultCode = 0 # 结果码，0 为成功，其他为失败
            errorMessage = 'ok' # 异常信息
            resultMap = {
                'resultCode': resultCode,
                'errorMessage': errorMessage,
                'algorithmResult': result # 需要 dumps 为 str 格式
            }
            logger.info('返回结果={}'.format(resultMap))  # 可以在平台查看相关日志


        except Exception as e:
            resultCode = -1  # 结果码，0 为成功，其他为失败
            errorMessage = str(e)  # 异常信息
            resultMap = {
                'resultCode': resultCode,
                'errorMessage': errorMessage,
                'algorithmResult': ''}
            logger.exception(e)
        return EKGMigrationSeasoningResponse(resultCode= resultCode, 
                             errorMessage=errorMessage, resultMap=resultMap)        
        
    return app



def create_api(llm, llm_config, embeddings,ekg_construct_service: EKGConstructService, memory_manager, geabase_handler, intention_router):
    return init_app(llm, llm_config, embeddings,ekg_construct_service, memory_manager, geabase_handler, intention_router)
