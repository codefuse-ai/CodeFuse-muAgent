

import uuid
import json
import os
import sys
#路径增加
import sys
import os
from typing import List, Dict, Optional, Union
src_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
# print(src_dir)
sys.path.append(src_dir)


src_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
)
sys.path.append(src_dir)
# print(src_dir)





import logging
logging.basicConfig(level=logging.INFO)






#muagent 依赖包
from muagent.connector.schema import Message
from muagent.schemas.db import TBConfig
from muagent.db_handler import *
from muagent.connector.memory_manager import TbaseMemoryManager
from muagent.llm_models.llm_config import EmbedConfig, LLMConfig
from muagent.schemas.db import GBConfig
from muagent.service.ekg_construct import EKGConstructService
from muagent.service.ekg_inference import IntentionRouter


class  GB_handler():
    def __init__(self, geabase_handler):
        self.geabase_handler = geabase_handler
        
    def geabase_is_react_node(self, start_nodeid, start_nodetype):
        '''
            判断一个节点是否为 react 模式的节点
        '''
        print('start_nodeid',start_nodeid, 'start_nodetype',start_nodetype)
        oneNode = self.geabase_handler.get_current_node(attributes={"id": start_nodeid,}, 
                                  node_type=start_nodetype)
        oneNodeDict = self.geabaseNodesFlatten(oneNode)
        print(oneNodeDict)
        extra = oneNodeDict['extra']
        if extra == '':
            return False

        extra = json.loads(extra)

        if 'pattern' in extra.keys():
            if extra['pattern'] == 'one-tool' or extra['pattern'] == 'single':
                return False
            elif extra['pattern'] == 'react' or extra['pattern'] == 'parallel' or extra['pattern'] == 'plan':
                return True
            else:
                return False
        
        else: #默认为 single
            return False




    def geabase_search_return_all_nodeandedge_(self,  start_nodeid = 'None', 
            start_nodetype = 'opsgptkg_intent', block_search_nodetype = []):
            '''
                #返回start_nodeid后续子树上的所有节点id , start_nodeid 是一个意图节点的末端节点， 可以设置停止探索的类型，比如
                #block_search_nodetype = ['opsgptkg_schedule', 'opsgptkg_task'] 时，代表这两种类型的节点不往后继续探索
                #同时返回边

                使用get_hop_infos，但是当hop较大的时候，速度很慢
            '''
            t = self.geabase_handler.get_hop_infos(attributes={"id": start_nodeid,}, node_type=start_nodetype, hop = 30,    )
            # print(t)
            # print(len(t.nodes))
            nodeid_in_subtree = []
            edge_in_subtree   = []
            for i in range(len(t.nodes)):
                nodeid_in_subtree.append({'nodeId':t.nodes[i].id, 'nodeType':t.nodes[i].type, 'nodeDescription':t.nodes[i].attributes['description'], 'nodeName':t.nodes[i].attributes['name']})
            for i in range(len(t.edges)):
                edge_in_subtree.append({ "startNodeId": t.edges[i].start_id, "endNodeId": t.edges[i].end_id  })
            return nodeid_in_subtree, edge_in_subtree
        
    
    def geabase_search_reture_nodeslist(self, start_nodeid:str,start_nodetype:str, block_search_nodetype:List=[] ):
        
        '''
            #返回start_nodeid后续子树上的所有节点id , start_nodeid 是一个意图节点的末端节点， 可以设置停止探索的类型，比如
            #block_search_nodetype = ['opsgptkg_schedule', 'opsgptkg_task'] 时，代表这两种类型的节点不往后继续探索
            #同时返回边
        
            不直接使用 get_hop_infos
            
            一个意图节点（非叶子意图节点）下可能有多个叶子节点，每个叶子节点也可能有多个意图节点。 在并行的时候，需要将某个意图节点单独成一个 nodeid_in_subtree
            如果直接调用 geabase_search_return_all_nodeandedge ，会把某个节点下所有的内容全放到一个list里
        '''
        
        nodeid_in_subtree = [{'nodeId':start_nodeid, 'nodeType':start_nodetype, 'nodeDescription':None, 'nodeName':None}]
        edge_in_subtree   = []
        nodeid_in_search  = [{'nodeId':start_nodeid, 'nodeType':start_nodetype}]
        count = 0
        
        reslist = []
        
        
        while len(nodeid_in_search)!= 0:
            # print(f'count is {count}')
            nodedict_now = nodeid_in_search.pop()
            nodeid_now      = nodedict_now['nodeId']
            nodetype_now    = nodedict_now['nodeType']
        
            
            neighborNodes = self.geabase_handler.get_neighbor_nodes(attributes= {"id": nodeid_now,}
                                   , node_type= nodetype_now )
        
            for i in range(len(neighborNodes)):
        
                    nodeid_new = neighborNodes[i].id
                    nodetype_new = neighborNodes[i].type
                    nodedescription_new = neighborNodes[i].attributes['description']
                    nodename_new = neighborNodes[i].attributes['name']
                    if nodetype_new in  block_search_nodetype:  #遇到阻塞的节点类型就终止， 不继续探索，也不纳入到结果中
                        continue 
                    if nodetype_new == 'opsgptkg_schedule':
                        
                        one_subtree, _ = self.geabase_search_return_all_nodeandedge(start_nodeid = nodeid_new, 
                                start_nodetype = nodetype_new, block_search_nodetype = [])
                        
                        one_subtree.append({'nodeId':nodeid_now, 'nodeType':nodetype_now, 'nodeDescription':None, 'nodeName':None})
                        reslist.append(one_subtree)
                    
                    
                    if { "startNodeId": nodeid_now, "endNodeId": nodeid_new  } not in edge_in_subtree:#避免重复导入相同的元素
                        nodeid_in_subtree.append({'nodeId':nodeid_new, 'nodeType':nodetype_new, 
                                                  'nodeDescription':nodedescription_new, 
                                                  'nodeName':nodename_new})
                        edge_in_subtree.append({ "startNodeId": nodeid_now, "endNodeId": nodeid_new  })
                        nodeid_in_search.append({'nodeId':nodeid_new, 'nodeType':nodetype_new})
                    else:
                        continue
            count = count +1
        
        #去重复
        unique_set = set(tuple(sorted(d.items())) for d in nodeid_in_subtree)
        # 将去重后的元组转换回字典形式，得到去重后的list
        nodeid_in_subtree = [dict(t) for t in unique_set]
        
        unique_set = set(tuple(sorted(d.items())) for d in edge_in_subtree)
        # 将去重后的元组转换回字典形式，得到去重后的list
        edge_in_subtree = [dict(t) for t in unique_set]
        
        return reslist

    def geabase_search_return_all_nodeandedge(self,  start_nodeid = 'None', 
            start_nodetype = 'opsgptkg_intent', block_search_nodetype = []):
            '''
                #返回start_nodeid后续子树上的所有节点id , start_nodeid 是一个意图节点的末端节点， 可以设置停止探索的类型，比如
                #block_search_nodetype = ['opsgptkg_schedule', 'opsgptkg_task'] 时，代表这两种类型的节点不往后继续探索
                #同时返回边

                不直接使用 get_hop_infos
            '''
            
            nodeid_in_subtree = [{'nodeId':start_nodeid, 'nodeType':start_nodetype, 'nodeDescription':None, 'nodeName':None}]
            edge_in_subtree   = []
            nodeid_in_search  = [{'nodeId':start_nodeid, 'nodeType':start_nodetype}]
            count = 0
            while len(nodeid_in_search)!= 0:
                # print(f'count is {count}')
                nodedict_now = nodeid_in_search.pop()
                nodeid_now      = nodedict_now['nodeId']
                nodetype_now    = nodedict_now['nodeType']

                
                neighborNodes = self.geabase_handler.get_neighbor_nodes(attributes= {"id": nodeid_now,}
                                       , node_type= nodetype_now )

                for i in range(len(neighborNodes)):

                        nodeid_new = neighborNodes[i].id
                        nodetype_new = neighborNodes[i].type
                        nodedescription_new = neighborNodes[i].attributes['description']
                        nodename_new = neighborNodes[i].attributes['name']
                        if nodetype_new in  block_search_nodetype:  #遇到阻塞的节点类型就终止， 不继续探索，也不纳入到结果中
                            continue 
                        
                        
                        
                        if { "startNodeId": nodeid_now, "endNodeId": nodeid_new  } not in edge_in_subtree:#避免重复导入相同的元素
                            nodeid_in_subtree.append({'nodeId':nodeid_new, 'nodeType':nodetype_new, 'nodeDescription':nodedescription_new, 'nodeName':nodename_new})
                            edge_in_subtree.append({ "startNodeId": nodeid_now, "endNodeId": nodeid_new  })
                            nodeid_in_search.append({'nodeId':nodeid_new, 'nodeType':nodetype_new})
                        else:
                            continue
                count = count +1

            #去重复
            unique_set = set(tuple(sorted(d.items())) for d in nodeid_in_subtree)
            # 将去重后的元组转换回字典形式，得到去重后的list
            nodeid_in_subtree = [dict(t) for t in unique_set]

            unique_set = set(tuple(sorted(d.items())) for d in edge_in_subtree)
            # 将去重后的元组转换回字典形式，得到去重后的list
            edge_in_subtree = [dict(t) for t in unique_set]

            return nodeid_in_subtree, edge_in_subtree


    

    def get_children_id(self, rootNodeId, rootNodeType):
        '''
            获取一个rootNodeId的孩子节点的id list
        '''


        neighborNodes = self.geabase_handler.get_neighbor_nodes(attributes= {"id": rootNodeId,}
                                       , node_type= rootNodeType )
        rootChildIdList = []

        for i  in range(len(neighborNodes)):
                rootChildIdList.append(neighborNodes[i].id)
        return rootChildIdList

    def get_children_type(self, rootNodeId, rootNodeType):
        '''
            获取一个rootNodeId的孩子节点的type list
        '''
        neighborNodes = self.geabase_handler.get_neighbor_nodes(attributes= {"id": rootNodeId,}
                                       , node_type= rootNodeType )
        rootChildIdList = []

        for i  in range(len(neighborNodes)):
                rootChildIdList.append(neighborNodes[i].type)
        return rootChildIdList

    def get_children_description(self, rootNodeId, rootNodeType):
        '''
            获取一个rootNodeId的孩子节点的id list
        '''


        neighborNodes = self.geabase_handler.get_neighbor_nodes(attributes= {"id": rootNodeId,}
                                       , node_type= rootNodeType )
        rootChildIdList = []

        for i  in range(len(neighborNodes)):
                rootChildIdList.append(neighborNodes[i].attributes['description'])
        return rootChildIdList

    def check_data_exist(self, startNodeId, startNodeType = 'opsgptkg_intent'):
        '''
            判断后续是否有数据填充，即一阶孩子节点是否有 opsgptkg_schedule  或者 opsgptkg_task，如有则为True，否则为False
        '''

        rootChildTypeList = self.get_children_type(startNodeId, startNodeType)
        #print('rootChildTypeList',  rootChildTypeList)
        if 'opsgptkg_schedule' in rootChildTypeList or 'opsgptkg_task' in rootChildTypeList:
            return True
        else:
            return False



    def geabase_find_paths(self, rootNodeId, rootNodeType, block_search_nodetype = ['opsgptkg_schedule', 'opsgptkg_task']):
        """ 
            返回从节点rootid到所有叶子节点id的路径列表。block_search_nodetype 设置了终止探索的节点类型
            # 这个函数可以被用来获取特定节点到叶子的所有路径
            # block_search_nodetype = ['opsgptkg_schedule', 'opsgptkg_task']
        """
        # 如果root是None，返回空列表
        if rootNodeId == [] or rootNodeType in block_search_nodetype:
            return [[]]

        # 如果这个节点是一个叶子节点（没有children），那么这里就是一条路径
        rootChildTypeList = self.get_children_type(rootNodeId, rootNodeType)
        print('rootChildTypeList', rootChildTypeList)
        if rootChildTypeList == []:
            return [[rootNodeId]]

        


        # 对于所有的孩子，递归找到它们的路径
        rootChildIdList     =   self.get_children_id(rootNodeId, rootNodeType)
        rootChildTypeList   =   self.get_children_type(rootNodeId, rootNodeType)

        paths = []
        for i in range(len(rootChildIdList)):
            childNodeId = rootChildIdList[i]
            rootChildType = rootChildTypeList[i]
            child_paths = self.geabase_find_paths(childNodeId, rootChildType, block_search_nodetype)  # 递归调用
            for path in child_paths:
                paths.append([rootNodeId] + path)  # 将当前节点添加到子路径的开头

        return paths



    def geabaseNodesFlatten(self, onenode):
        '''
         将Nodes 的id  type  attributes 展开到一个同级情况
        '''
        res = {}
        res['id'] = onenode.id
        res['type'] = onenode.type
        for key in onenode.attributes:
            res[key] = onenode.attributes[key]
        return res
    


    def geabaseGetGetOneHopNeighborsInfo(self, rootNodeId = 'None', rootNodeType = 'opsgptkg_intent'):
        '''
            先得到一阶近邻的所有节点
            再将其转换为【 dict， dict】的格式
        '''
 
        neighborNodes = self.geabase_handler.get_neighbor_nodes(attributes={"id": rootNodeId,}, 
                                  node_type=rootNodeType)
        resList = []
        for i in range(len(neighborNodes)):
            resList.append(  self.geabaseNodesFlatten(neighborNodes[i]) )

        return resList

    def geabaseGetOneNodeInfo(self, rootNodeId = 'None', rootNodeType = 'opsgptkg_intent'):
        '''
            先得到一阶近邻的所有节点
            再将其转换为{nodeId1: nodeId1Info, }的格式
            example{'oneNodeId': {'teamids': '', 'id': 'oneNodeId', 'description': 'oneNodeDescription', 'name': 'oneNodeDescription', 'extra': '', 'nodeType': 'opsgptkg_intent'}}
        '''
 
        resList = self.geabaseGetGetOneHopNeighborsInfo(rootNodeId = rootNodeId, rootNodeType = rootNodeType)
        resdict = {}
        for i in range(len(resList)):
            nodeid = resList[i]['id']
            resdict[nodeid] = resList[i]
        return resdict

    def geabaseGetOnlyOneNodeInfo(self, rootNodeId = 'None', rootNodeType = 'opsgptkg_intent'):
        '''
            先得到一个节点
            再将其转换为{nodeId1: nodeId1Info, }的格式

            example：{'oneNodeId': {'extra': '', 'teamids': '', 'id': 'oneNodeId', 'description': 'oneNodeDescription', 'name': 'oneNodeDescription', 'nodeType': 'opsgptkg_intent'}}
        '''
 
        
        oneNode = self.geabase_handler.get_current_node(attributes={"id": rootNodeId,}, 
                                  node_type=rootNodeType)
        oneNodeDict = self.geabaseNodesFlatten(oneNode)
        oneNodeId = oneNode.id

        resdict = {}
        resdict[oneNodeId] = oneNodeDict

        return resdict
    
    def geabaseGetOnlyOneNodeInfoWithKey(self, rootNodeId = 'None', 
        rootNodeType = 'opsgptkg_intent', key = 'id'):
        '''
            先得到一个节点
            再将其转换为{nodeId1: nodeId1Info, }的格式
            再得到其key的value， 如果不存在这个key，那么返回None
        '''
 

        resDict = self.geabaseGetOnlyOneNodeInfo(rootNodeId, rootNodeType)
        # print(resDict)
        if key in resDict[rootNodeId].keys():
            return resDict[rootNodeId][key]
        else:
            return None


    def all_nodetype_check(self,  rootNodeId = 'None', rootNodeType = 'opsgptkg_task', 
        neighborNodeType = 'opsgptkg_task'):
    
        #判断 geabase 查询rootNodeId 一阶近邻后的结果是否都是 neighborNodeType

 

        neighborNodes = self.geabase_handler.get_neighbor_nodes(attributes= {"id": rootNodeId,}
                                       , node_type= rootNodeType )
        # print(neighborNodes)
        if len(neighborNodes) == 0:
            #一阶邻居没有节点
            return False
        for i in range(len(  neighborNodes )):
            #res['resultSet']['rows'][i]
            print(neighborNodes[i].type)
            if neighborNodes[i].type != neighborNodeType:
                print(i, neighborNodes[i].type, neighborNodeType)
                return False #只要有一个不是phenomenon 则为False
        return True

 

    def  getNeighborNodeDescriptions(self,  rootNodeId = 'None', rootNodeType = 'opsgptkg_task'):
        '''
            #从res中得到 next_node_description_list
            得到一阶近邻的descriptionlist
            get_nodedescription_from_res
        '''
 

        neighborNodes = self.geabase_handler.get_neighbor_nodes(attributes={"id": rootNodeId,}, 
                                  node_type=rootNodeType)

        next_node_description_list = []

        for i in range(len(neighborNodes)):
            next_node_description_list.append(   neighborNodes[i].attributes['description']    )
        return next_node_description_list

    def  getNeighborNodeids(self,  rootNodeId = 'None', rootNodeType = 'opsgptkg_task'):
        '''
            #从res中得到 next_node_description_list
            得到一阶近邻的descriptionlist
            get_nodedescription_from_res
        '''
 

        neighborNodes = self.geabase_handler.get_neighbor_nodes(attributes={"id": rootNodeId,}, 
                                  node_type=rootNodeType)

        next_node_id_list = []

        for i in range(len(neighborNodes)):
            next_node_id_list.append(   neighborNodes[i].id    )
        return next_node_id_list

    def geabase_getDescription(self,  rootNodeId = 'None', rootNodeType = 'opsgptkg_task'):
        '''
            获取节点上的描述 name + description
        '''
 


        oneNode = self.geabase_handler.get_current_node(attributes={"id": rootNodeId,}, 
                                  node_type=rootNodeType)

        oneNodeName  = oneNode.attributes['name']
        oneNodeDescription  = oneNode.attributes['description']
        if oneNodeName != oneNodeDescription:
            res = oneNodeName + '\n' +  oneNodeDescription
        else:
            res = oneNodeName

        return res



    def geabase_getnodequestion(self,  rootNodeId = 'None', rootNodeType = 'opsgptkg_task'):
        '''
        #根据节点上的信息，获取选择题或者填空题，如果不满足条件，则返回None
        {
        "questionType" : "multipleChoice", # or "essayQuestion" #这个字段表示用户的返回值类型。选择题或者问答题， str
        "questionContent": {
        "question":"北京有多少个区？" #str 表示用户的提问
        "candidate": [ "12个", "16个", "100个"],  # list， 元素为 str， 表示用户可能的选项。 注意此项在问答题的时候为None
          }}
        '''
        if self.geabase_getnodetype( rootNodeId = rootNodeId , rootNodeType = rootNodeType) == 'onlyTool':
            return None
        elif self.geabase_getnodetype( rootNodeId = rootNodeId , rootNodeType = rootNodeType) == 'userProblem':
            if self.all_nodetype_check( rootNodeId = rootNodeId , rootNodeType = rootNodeType,  neighborNodeType = 'opsgptkg_phenomenon') == True: #后面都是事实节点，是选择题目
                questionType = 'multipleChoice'
            else:
                questionType  = 'essayQuestion'
            
            if questionType == 'essayQuestion':
                question = self.geabase_getDescription(rootNodeId = rootNodeId , rootNodeType = rootNodeType)
                candidate = None
            else:
                question = self.geabase_getDescription(rootNodeId = rootNodeId , rootNodeType = rootNodeType)
                candidate = self.getNeighborNodeDescriptions(rootNodeId = rootNodeId , rootNodeType = rootNodeType)
            res =         {
                "questionType" : questionType, #"multipleChoice", # or "essayQuestion" #这个字段表示用户的返回值类型。选择题或者问答题， str
                "questionContent": {
                "question":question, #str 表示用户的提问
                "candidate": candidate,  # list， 元素为 str， 表示用户可能的选项。 注意此项在问答题的时候为None
                }}
            return res
        else:
            return None


        


    def geabase_getnodetype(self,  rootNodeId = 'None', rootNodeType = 'opsgptkg_task'):
        #根据节点上的信息，返回节点类型， 当前就两个：onlyTool 或者  userProblem。 
        OneNodeInfo = self.geabaseGetOnlyOneNodeInfo(rootNodeId = rootNodeId, rootNodeType = rootNodeType)
        if OneNodeInfo[rootNodeId]['executetype'] == 'userProblem':
            return 'userProblem'
        else:
            return 'onlyTool'
    
    def get_extra_tag(self, rootNodeId = 'None', rootNodeType = 'opsgptkg_task', key = 'ignorememory'):
        # print(f'rootNodeId is {rootNodeId},  rootNodeType is {rootNodeType}')
        try:
            oneNode = self.geabase_handler.get_current_node(attributes={"id": rootNodeId,}, 
                                    node_type=rootNodeType)
        except:
            logging.info('get_extra_tag 没有找到合适的数据， 可能原因是当前查找对象不是 opsgptkg_task 类型的节点'  )
            return None
        # print(oneNode)
        if oneNode.attributes['extra'] == '':
            return None
        extra = oneNode.attributes['extra']
        try :
            extra = json.loads(extra)
        except:
            return None
        if key not in extra.keys():
            return None
        else:
            return extra[key]
        
    def get_tag(self, rootNodeId = 'None', rootNodeType = 'opsgptkg_task', key = 'ignorememory')->str:
        '''
            得到一个节点的属性值
        '''
        # print(f'rootNodeId is {rootNodeId},  rootNodeType is {rootNodeType}')
        try:
            oneNode = self.geabase_handler.get_current_node(attributes={"id": rootNodeId,}, 
                                    node_type=rootNodeType)
        except:
            logging.info(f'get_tag 没有找到合适的数据， 可能原因是当前对象为 {rootNodeType} 类型的节点'  )
            return None
        # print(oneNode)
        if key not in oneNode.attributes.keys():
            logging.info(f'get_tag 没有找到合适的数据， 可能原因key名错误'  )
            return None
        if oneNode.attributes[key] == '':
            logging.info(f'get_tag 没有找到合适的数据， 可能原因为空字符串'  )
            return None
        
        return oneNode.attributes[key]

        
        



    def user_input_memory_tag(self,  rootNodeId = 'None', rootNodeType = 'opsgptkg_task'):
        print(f'rootNodeId is {rootNodeId},  rootNodeType is {rootNodeType}')
        try:
            oneNode = self.geabase_handler.get_current_node(attributes={"id": rootNodeId,}, 
                                    node_type=rootNodeType)
        except:
            logging.info('user_input_memory_tag 没有找到合适的数据， 可能原因是当前查找对象不是 opsgptkg_task 类型的节点'  )
            return None
        # print(oneNode)
        if oneNode.attributes['extra'] == None:
            return None
        if oneNode.attributes['extra'] == '':
            return None
        extra = oneNode.attributes['extra']

        if type(extra) == str:
            extra_json = json.loads(extra)
        # print(extra_json)
        if 'memory_tag' not in extra_json.keys():
            return None
        else:
            memory_tag = extra_json['memory_tag']
        return memory_tag

        
if __name__ == "__main__":
    pass
