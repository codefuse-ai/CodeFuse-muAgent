from loguru import logger
from muagent.sandbox.pycodebox import PyCodeBox


# 测试1
pycodebox = PyCodeBox(remote_url="http://localhost:5050", 
               remote_ip="http://localhost", 
            remote_port="5050", 
            token="mytoken",
            do_code_exe=True, 
            do_remote=False,
            do_check_net=False
            )


reuslt = pycodebox.chat("```import os\nos.getcwd()```", do_code_exe=True)
print(reuslt)

# reuslt = pycodebox.chat("```print('hello world!')```", do_code_exe=True)
reuslt = pycodebox.chat("print('hello world!')", do_code_exe=True)
print(reuslt)

    
# # 测试2
# with PyCodeBox(remote_url="http://localhost:5050", 
#                remote_ip="http://localhost", 
#             remote_port="5050", 
#             token="mytoken",
#             do_code_exe=True, 
#             do_remote=False) as codebox:
    
#     result = codebox.run("'hello world!'")
#     print(result)