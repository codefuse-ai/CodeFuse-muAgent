from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union
from enum import Enum
import copy
import json




#####################################################################
############################ LingSiResponse  #############################
#####################################################################
class LingSiResponse(BaseModel):
    '''
    lingsi的返回值， 算法的输入值
    '''
    currentNodeId: Optional[str]=None
    observation: Optional[Union[str,Dict]] # jsonstr
    scene: str
    sessionId: str
    startRootNodeId: Optional[str] = None
    intentionRule: Optional[Union[List,str] ]= None
    intentionData: Optional[Union[List,str] ] = None
    startFromRoot:   Optional[str] = None
    type: Optional[str] = None
    userAnswer: Optional[str]=None
    agentName:Optional[str]=None




#####################################################################
############################ #定义PlanningRunning  和 parallel 模式下大模型返回格式  #############################
#####################################################################

class ActionOneStep(BaseModel):
    '''
        指定下一步的动作由哪一个agent / player 完成
        example {"player_name":str, "agent_name":str}
    '''
    agent_name: str 
    player_name:str 

class ActionPlan(BaseModel):
    '''
        指定后续的动作由哪些agent / player 完成
        
        [{"player_name":str, "agent_name":str}, {"player_name":str, "agent_name":str}, ... ]
    '''
    data: List[ActionOneStep]
    def get_player_name_by_agent_name(self, agent_name:str)->str:
        '''
            根据agent_name 返回 player_name

        '''
        for i in range(len(self.data)):
            if self.data[i].agent_name == agent_name:
                return self.data[i].player_name
        return None #没找到合适的匹配




class ObservationItem(BaseModel):
    '''
       假设 agent 说话时返回的数据格式，除了content外，还有memory_tag, 指定这个信息有谁可见
    '''
    memory_tag: List[str]
    content: str





class PlanningRunningAgentReply(BaseModel):
    '''
    示例数据
    sss = {
        "thought": "思考内容",
        "action_plan": [
            {"player_name": "player1", "agent_name": "agent1"},
            {"player_name": "player2", "agent_name": "agent2"}
        ],
        "Dungeon_Master": [
            {"memory_tag": ["agent_name_a", "agent_name_b"], "content": "DM 内容1"},
            {"memory_tag": ["agent_name_c"], "content": "DM 内容2"}
        ]
    }
    '''
    thought: str = "None"
    action_plan: ActionPlan=[]
    observation: List[ObservationItem]=[]

    def __init__(self, **kwargs):
        # 处理 action_plan
        action_steps = [ActionOneStep(**step) for step in kwargs.get('action_plan', [])]
        action_plan = ActionPlan(data=action_steps)

        # 处理 observation
        observations = [ObservationItem(**item) for item in kwargs.get('Dungeon_Master', [])]

        # 调用父类的初始化方法
        super().__init__(
            thought=kwargs.get('thought', "None"),
            action_plan=action_plan,
            observation=observations
        )



#####################################################################
############################ #定义输出plan格式  #############################
#####################################################################

class QuestionContent(BaseModel):
    '''
        {'question': '请玩家根据当前情况发言',     'candidate': None }
    '''
    question:str 
    candidate:Optional[str]=None
    
class QuestionDescription(BaseModel):
    '''
        {'questionType': 'essayQuestion',
        'questionContent': {'question': '请玩家根据当前情况发言','candidate': None }}
    '''
    questionType:str 
    questionContent:QuestionContent 

class ToolPlanOneStep(BaseModel):
    '''
            tool_plan_one_step =  {'toolDescription': '请用户回答',
            'currentNodeId': nodeId,
            'memory': None,
            'type': 'userProblem',
            'questionDescription': {'questionType': 'essayQuestion',
            'questionContent': {'question': '请玩家根据当前情况发言',
            'candidate': None }}} 
    '''
    toolDescription:str 
    currentNodeId: Optional[str] = None
    currentNodeInfo:str
    memory:Optional[str] = None
    type:str 
    questionDescription:Optional[QuestionDescription]=None
    


if __name__ == '__main__':
    #     response_data = LingSiResponse(
    #     currentNodeId="node_1",
    #     observation='{"key": "value"}',
    #     scene="example_scene",
    #     sessionId="session_123",
    #     startRootNodeId="root_node_1",
    #     type="example_type",
    #     userAnswer="user_answer_example"
        
    # )
            
    #     print( response_data.type )
    # 示例数据
    # sss = {
    #     "thought": "思考内容",
    #     "action_plan": [
    #         {"player_name": "player1", "agent_name": "agent1"},
    #         {"player_name": "player2", "agent_name": "agent2"}
    #     ],
    #     "Dungeon_Master": [
    #         {"memory_tag": ["agent_name_a", "agent_name_b"], "content": "DM 内容1"},
    #         {"memory_tag": ["agent_name_c"], "content": "DM 内容2"}
    #     ]
    # }
    
    # # 直接使用 sss 创建 PlanningRunningAgentReply 对象
    # reply = PlanningRunningAgentReply(**sss)
    
    
    # #测试ToolPlanOneStep
    # # 定义 Sss
    # nodeId = 'somenodeid'
    # Sss = {
    #     'toolDescription': '请用户回答',
    #     'currentNodeId': nodeId,
    #     'memory': None,
    #     'type': 'userProblem',
    #     'questionDescription': {
    #         'questionType': 'essayQuestion',
    #         'questionContent': {
    #             'question': '请玩家根据当前情况发言',
    #             'candidate': None
    #         }
    #     }
    # }
    
    # # 将 Sss 转换为 ToolPlanOneStep 对象
    # tool_plan_one_step = ToolPlanOneStep(**Sss)
    
    
    # ###测试 LingSiResponse
    # sessionId = '349579720439752097847_25'
    # #谁是卧底 通用
    # params_string = \
    # {

    #       "scene": "NEXA",
    #       "startRootNodeId": '4bf08f20487bfb3d34048ddf455bf5dd', #hash_id('剧本杀' ),
    #       "intentionRule": ["nlp"],
    #       "intentionData": "执行谁是卧底进程",
    #       "observation": "{\"content\":\"开始游戏\"}",
    #       "sessionId": sessionId
    #     }
    
    # lingsi_response = LingSiResponse(**params_string)
    # print(lingsi_response)
    
    
    
    # ###测试 LingSiResponse
    # nodeId = 's'
    # execute_agent_name = 'n'
    
    # tool_one_step= ToolPlanOneStep(
    #     **{'toolDescription': '请用户回答',
    #     'currentNodeId': nodeId + '%%@@#' + execute_agent_name,
    #     'currentNodeInfo':execute_agent_name,
    #     'memory': None,
    #     'type': 'userProblem',
    #     'questionDescription': {'questionType': 'essayQuestion',
    #     'questionContent': {'question': '请玩家根据当前情况发言',
    #     'candidate': None }}}
    #     )
    # print(tool_one_step)
                
    
    
    ###测试 ActionPlan
    
    
    
    # ccc  = {'data': [{'agent_name': 'agent_2', 'player_name': 'player_1'},
    #   {'agent_name': '人类agent_a', 'player_name': '李四(人类玩家)'},
    #   {'agent_name': 'agent_3', 'player_name': 'player_2'},
    #   {'agent_name': 'agent_1', 'player_name': 'player_3'}]}
    
    ccc = [{"player_name": "主持人", "agent_name": "主持人"}, 
           {"player_name": "player_1", "agent_name": "agent_2"},
           {"player_name": "李四(人类玩家)", "agent_name": "人类agent_a"}, 
           {"player_name": "player_2", "agent_name": "agent_3"}, 
           {"player_name": "player_3", "agent_name": "agent_1"}]
    ccc = {'data':ccc}
    
    action_plan =ActionPlan(**ccc)
    print(action_plan)
    
    agent_name= action_plan.get_player_name_by_agent_name('人类agent_a')
    print(agent_name)
    
    
    
    
    
    
    
    