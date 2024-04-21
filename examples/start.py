import docker, sys, os, time, requests, psutil
import subprocess
from docker.types import Mount, DeviceRequest
from loguru import logger

import platform
system_name = platform.system()
USE_TTY = system_name in ["Windows"]

src_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

DEFAULT_BIND_HOST = "127.0.0.1"
os.environ["DEFAULT_BIND_HOST"] = DEFAULT_BIND_HOST
CONTRAINER_NAME = "muagent"
IMAGE_NAME = "devopsgpt:py39"
SANDBOX_CONTRAINER_NAME = "devopsgpt_sandbox"
SANDBOX_IMAGE_NAME = "devopsgpt:py39"
SANDBOX_HOST = os.environ.get("SANDBOX_HOST") or DEFAULT_BIND_HOST # "172.25.0.3"
SANDBOX_SERVER = {
    "host": f"http://{SANDBOX_HOST}",
    "port": 5050,
    "docker_port": 5050,
    "url": f"http://{SANDBOX_HOST}:5050",
    "do_remote": True,
}
# webui.py server
WEBUI_SERVER = {
    "host": DEFAULT_BIND_HOST,
    "port": 8501,
    "docker_port": 8501
}

# api.py server
API_SERVER = {
    "host": DEFAULT_BIND_HOST,
    "port": 7861,
    "docker_port": 7861
}

# sdfile_api.py server
SDFILE_API_SERVER = {
    "host": DEFAULT_BIND_HOST,
    "port": 7862,
    "docker_port": 7862
}
NEBULA_HOST = DEFAULT_BIND_HOST
NEBULA_PORT = 9669
NEBULA_STORAGED_PORT = 9779
NEBULA_USER = 'root'
NEBULA_PASSWORD = ''
NEBULA_GRAPH_SERVER = {
    "host": DEFAULT_BIND_HOST,
    "port": NEBULA_PORT,
    "docker_port": NEBULA_PORT
}



def check_process(content: str, lang: str = None, do_stop=False):
    '''process-not-exist is true, process-exist is false'''
    for process in psutil.process_iter(["pid", "name", "cmdline"]):
        # check process name contains "jupyter" and port=xx

        # if f"port={SANDBOX_SERVER['port']}" in str(process.info["cmdline"]).lower() and \
        #     "jupyter" in process.info['name'].lower():
        if content in str(process.info["cmdline"]).lower():
            logger.info(f"content, {process.info}")
            # 关闭进程
            if do_stop:
                process.terminate()
                return True
            return False
    return True

def check_docker(client, container_name, do_stop=False):
    '''container-not-exist is true, container-exist is false'''
    if client is None: return True
    for i  in client.containers.list(all=True):
        if i.name == container_name:
            if do_stop:
                container = i

                if container_name == CONTRAINER_NAME and i.status == 'running':
                    # wrap up db
                    logger.info(f'inside {container_name}')
                    # cp nebula data
                    res = container.exec_run('''sh chatbot/coagent/utils/nebula_cp.sh''')
                    logger.info(f'cp res={res}')

                    # stop nebula service
                    res = container.exec_run('''/usr/local/nebula/scripts/nebula.service stop all''')
                    logger.info(f'stop res={res}')

                container.stop()
                container.remove()
                return True
            return False
    return True

def start_docker(client, script_shs, ports, image_name, container_name, mounts=None, network=None):
    container = client.containers.run(
        image=image_name,
        command="bash",
        mounts=mounts,
        name=container_name,
        mem_limit="8g",
        # device_requests=[DeviceRequest(count=-1, capabilities=[['gpu']])],
        # network_mode="host",
        ports=ports,
        stdin_open=True,
        detach=True,
        tty=USE_TTY,
        network=network,   
    )

    logger.info(f"docker id: {container.id[:10]}")

    # 启动notebook
    for script_sh in script_shs:
        if False and "llm_api" in script_sh:
            logger.debug(script_sh)
            response = container.exec_run(["sh", "-c", script_sh])
            logger.debug(response)
        elif "llm_api" not in script_sh:
            logger.debug(script_sh)
            response = container.exec_run(["sh", "-c", script_sh])
            logger.debug(response)
    return container

#########################################
############# 开始启动服务 ###############
#########################################
network_name ='my_network'

def start_sandbox_service(network_name ='my_network'):
    mount = Mount(
            type='bind',
            source=os.path.join(src_dir, "jupyter_work"),
            target='/home/user/chatbot/jupyter_work',
            read_only=False  # 如果需要只读访问，将此选项设置为True
        )
    mounts = [mount]
    # 沙盒的启动与服务的启动是独立的
    if SANDBOX_SERVER["do_remote"]:
        client = docker.from_env()
        networks = client.networks.list()
        if any([network_name==i.attrs["Name"] for i in networks]):
            network = client.networks.get(network_name)
        else:
            network = client.networks.create('my_network', driver='bridge')

        # 启动容器
        logger.info("start container sandbox service")
        JUPYTER_WORK_PATH = "/home/user/chatbot/jupyter_work"
        script_shs = [f"cd /home/user/chatbot/jupyter_work && nohup jupyter-notebook --NotebookApp.token=mytoken --port=5050 --allow-root --ip=0.0.0.0 --notebook-dir={JUPYTER_WORK_PATH} --no-browser --ServerApp.disable_check_xsrf=True &"]
        ports = {f"{SANDBOX_SERVER['docker_port']}/tcp": f"{SANDBOX_SERVER['port']}/tcp"}
        if check_docker(client, SANDBOX_CONTRAINER_NAME, do_stop=True, ):
            container = start_docker(client, script_shs, ports, SANDBOX_IMAGE_NAME, SANDBOX_CONTRAINER_NAME, mounts=mounts, network=network_name)
        # 判断notebook是否启动
        time.sleep(5)
        retry_nums = 3
        while retry_nums>0:
            logger.info(f"http://localhost:{SANDBOX_SERVER['port']}")
            response = requests.get(f"http://localhost:{SANDBOX_SERVER['port']}", timeout=270)
            if response.status_code == 200:
                logger.info("container & notebook init success")
                break
            else:
                retry_nums -= 1
                logger.info(client.containers.list())
                logger.info("wait container running ...")
            time.sleep(5)

    else:
        try:
            client = docker.from_env()
        except:
            client = None
        check_docker(client, SANDBOX_CONTRAINER_NAME, do_stop=True, )
        logger.info("start local sandbox service")

def start_api_service(sandbox_host=DEFAULT_BIND_HOST):
    client = docker.from_env()
    logger.info("start container service")
    mount = Mount(
        type='bind',
        source=src_dir,
        target='/home/user/chatbot/',
        read_only=False  # 如果需要只读访问，将此选项设置为True
    )
    ports={
            f"{API_SERVER['docker_port']}/tcp": f"{API_SERVER['port']}/tcp", 
            f"{WEBUI_SERVER['docker_port']}/tcp": f"{WEBUI_SERVER['port']}/tcp",
            f"{SDFILE_API_SERVER['docker_port']}/tcp": f"{SDFILE_API_SERVER['port']}/tcp",
            f"{NEBULA_GRAPH_SERVER['docker_port']}/tcp": f"{NEBULA_GRAPH_SERVER['port']}/tcp"
            }
    # mounts = [mount, mount_database, mount_code_database]
    mounts = [mount]
    script_shs = [
        "mkdir -p /home/user/chatbot/logs",
        '''
        if [ -d "/home/user/chatbot/data/nebula_data/data/meta" ]; then
            cp -r /home/user/chatbot/data/nebula_data/data /usr/local/nebula/
        fi
        ''',
        "/usr/local/nebula/scripts/nebula.service start all",
        "/usr/local/nebula/scripts/nebula.service status all",
        "sleep 2",

        '''curl -X PUT -H "Content-Type: application/json" -d'{"heartbeat_interval_secs":"2"}' -s "http://127.0.0.1:19559/flags"''',
        '''curl -X PUT -H "Content-Type: application/json" -d'{"heartbeat_interval_secs":"2"}' -s "http://127.0.0.1:19669/flags"''',
        '''curl -X PUT -H "Content-Type: application/json" -d'{"heartbeat_interval_secs":"2"}' -s "http://127.0.0.1:19779/flags"''',

        "pip install zdatafront-sdk-python==0.1.2 -i https://artifacts.antgroup-inc.cn/simple",
        "pip install jieba",
        "pip install duckduckgo-search",

        f"export DUCKDUCKGO_PROXY=socks5://host.docker.internal:13659 && export SANDBOX_HOST={sandbox_host}",
        # "cd chatbot && rm -rf build coagent.egg-info muagent.egg-info dist && python setup.py sdist bdist_wheel &&\
        #     pip install dist/muagent-0.0.101-py3-none-any.whl && rm -rf build coagent.egg-info muagent.egg-info dist"
        ]

    if check_docker(client, CONTRAINER_NAME, do_stop=True):
        container = start_docker(client, script_shs, ports, IMAGE_NAME, CONTRAINER_NAME, mounts, network=network_name)




def start_main():
    start_sandbox_service()
    sandbox_host = DEFAULT_BIND_HOST
    if SANDBOX_SERVER["do_remote"]:
        client = docker.from_env()
        containers = client.containers.list(all=True)

        for container in containers:
            container_a_info = client.containers.get(container.id)
            if container_a_info.name == SANDBOX_CONTRAINER_NAME:
                container1_networks = container.attrs['NetworkSettings']['Networks']
                sandbox_host = container1_networks.get(network_name)["IPAddress"]
                break
    start_api_service(sandbox_host)



if __name__ == "__main__":
    start_main()
    # start_sandbox_service()
    # sandbox_host = DEFAULT_BIND_HOST
    # if SANDBOX_SERVER["do_remote"]:
    #     client = docker.from_env()
    #     containers = client.containers.list(all=True)

    #     for container in containers:
    #         container_a_info = client.containers.get(container.id)
    #         if container_a_info.name == SANDBOX_CONTRAINER_NAME:
    #             container1_networks = container.attrs['NetworkSettings']['Networks']
    #             sandbox_host = container1_networks.get(network_name)["IPAddress"]
    #             break
    # start_api_service(sandbox_host)


