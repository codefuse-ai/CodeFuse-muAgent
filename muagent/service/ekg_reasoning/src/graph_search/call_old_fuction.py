# lingsi 游走推理服务 old
import json
import requests
# import logging
from ..utils.logger import logging
import copy
import sys
import os

# logger = logging.getLogger()
# logging.basicConfig(level=logging.DEBUG)

#step 1  retriver

def call_old_fuction(

        params_string 
    ):
 
        url =os.environ['oldfunction_url']

        headers = {
            'Content-Type': 'application/json;charset=utf-8',
            'MPS-app-name': 'test',
            'MPS-http-version': '1.0'
        }





        if type(params_string) == str:
            params_string = json.loads(params_string)

        body = {
            'features': {
                'query': json.dumps(params_string,ensure_ascii=False)
            }
        }
        r = requests.post(url, json=body, headers=headers)
        #logger(r)
        # logging.info( str((r.json() )) )
        output_1 =  json.loads(r.json()['resultMap']['algorithmResult'])
        # logging.info('============算法的结果是================')
        # logging.info(f'结果是 {output_1}')
        # logging.info('============================================')
        return output_1


if __name__ == '__main__':
    #配置依赖
    pass