# 意图识别接口
import json
import requests
import logging
import copy
import os
from ..utils.logger import logging
# logger = logging.getLogger()
# logging.basicConfig(level=logging.DEBUG)
RETRY_MAX_NUM = 3
def intention_recognition_ekgfunc( root_node_id, rule, query, memory, start_from_root = True,
        url= os.environ['intention_url'] ):
    '''
        意图识别ekg, 意图识别的主程序， 不区分NLP还是基于规则
            return 
                node_id
                nodes_to_choose
                canditate_id
                answer
                intentionRecognitionSituation
                successCode
                errorMessage
    '''

    headers = {
        'Content-Type': 'application/json;charset=utf-8',
        'MPS-app-name': 'test',
        'MPS-http-version': '1.0'
    }


    data = {
                'service_name' : 'node_info_match', 
                'root_node_id':  root_node_id,
                'rule': rule,
                'query': query,
                'memory': memory,
                'start_from_root' : start_from_root,
            }

    body = {
        'features': {
            'query': json.dumps(data,ensure_ascii=False)
        }
    }

    logging.info( body )
    retry_num = 0
    while retry_num <= RETRY_MAX_NUM:
        retry_num = retry_num + 1
        try:
            r = requests.post(url, json=body, headers=headers)
        
        
            logging.info( str((r.json() )) )  #12:00:37
            output_1 =  (r.json())
            # logging.info('============意图识别的结果是================')
            # logging.info(f'意图识别结果是 {output_1}')
            # logging.info('============================================')
            res = json.loads(output_1['resultMap']['algorithmResult'])
            return res

        except Exception as e:

            logging.info(f'意图识别报错:{e}')
            sleep(1)
    raise ValueError(f'意图识别报错 超过了最大重试次数RETRY_MAX_NUM:{RETRY_MAX_NUM}')
    return None

    
    # r = requests.post(url, json=body, headers=headers)

    # logging.info( str((r.json() )) )  #12:00:37
    # output_1 =  (r.json())
    # # logging.info('============意图识别的结果是================')
    # # logging.info(f'意图识别结果是 {output_1}')
    # # logging.info('============================================')
    # res = json.loads(output_1['resultMap']['algorithmResult'])
    # return res



def intention_recognition_querypatternfunc( query,  
        url= os.environ['intention_url'] ):
    '''
        判断输入为查询问题还是执行计划， 只有在NLP模式下，才有此问题

            return 
                resultMap.algorithmResult.output	bool	True表示执行流程，False表示询问信息。
    '''

    headers = {
        'Content-Type': 'application/json;charset=utf-8',
        'MPS-app-name': 'test',
        'MPS-http-version': '1.0'
    }


    data = {
                'service_name' : 'whether_execute', 
                'query': query,
            }

    body = {
        'features': {
            'query': json.dumps(data,ensure_ascii=False)
        }
    }

    logging.info( body )

    retry_num = 0
    while retry_num <= RETRY_MAX_NUM:
        retry_num = retry_num + 1
        try:
            r = requests.post(url, json=body, headers=headers)
        
        
            logging.info( str((r.json() )) )  #12:00:37
            output_1 =  (r.json())
            # logging.info('============意图识别的结果是================')
            # logging.info(f'意图识别结果是 {output_1}')
            # logging.info('============================================')
            res = json.loads(output_1['resultMap']['algorithmResult'])
            if type(res) == 'str':
                res = json.loads(res)
            return res['output']
        except Exception as e:

            logging.info(f'意图识别报错:{e}')
            sleep(1)
    raise ValueError(f'意图识别报错 超过了最大重试次数RETRY_MAX_NUM:{RETRY_MAX_NUM}')
    return None







def intention_recognition_querytypefunc( query, 
        url= os.environ['intention_url'] ):
    '''
        意图识别ekg
            return 
                resultMap.algorithmResult.output	str	四种：
                    整体计划查询； 'allPlan'
                    下一步任务查询；'nextStep'
                    RAG（相关信息）；
                    闲聊; 'justChat'
    '''


    headers = {
        'Content-Type': 'application/json;charset=utf-8',
        'MPS-app-name': 'test',
        'MPS-http-version': '1.0'
    }


    data = {
                'service_name' : 'consult_which', 
                'query': query,
            }

    body = {
        'features': {
            'query': json.dumps(data,ensure_ascii=False)
        }
    }

    logging.info( body )

    retry_num = 0
    while retry_num <= RETRY_MAX_NUM:
        retry_num = retry_num + 1
        try:
            r = requests.post(url, json=body, headers=headers)
        
        
            logging.info( str((r.json() )) )  #12:00:37
            output_1 =  (r.json())
            # logging.info('============意图识别的结果是================')
            # logging.info(f'意图识别结果是 {output_1}')
            # logging.info('============================================')
            res = json.loads(output_1['resultMap']['algorithmResult'])
            if type(res) == 'str':
                res = json.loads(res)
            return res['output']
        except Exception as e:

            logging.info(f'意图识别报错:{e}')
            sleep(1)
    raise ValueError(f'意图识别报错 超过了最大重试次数RETRY_MAX_NUM:{RETRY_MAX_NUM}')
    return None





if __name__ == '__main__':
    pass