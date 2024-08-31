
import docker, sys, os, time, requests, psutil
import subprocess
from docker.types import Mount, DeviceRequest

import platform
system_name = platform.system()
USE_TTY = system_name in ["Windows"]


client = docker.from_env()

mount = Mount(
        type='bind',
        source="/d/project/gitlab/ant_code/muagent",
        target='/home/user/muagent',
        read_only=False  # 如果需要只读访问，将此选项设置为True
    )

ports={
    f"8080/tcp": f"8888/tcp", 
    f"3737/tcp": f"3737/tcp",
}


print( client.networks.list())

network_name ='my_network'
networks = client.networks.list()
if any([network_name==i.attrs["Name"] for i in networks]):
    network = client.networks.get(network_name)
else:
    network = client.networks.create('my_network', driver='bridge')
container = client.containers.run(
        image="muagent:test",
        command="bash",
        mounts=[mount],
        name="test",
        mem_limit="8g",
        # device_requests=[DeviceRequest(count=-1, capabilities=[['gpu']])],
        # network_mode="host",
        ports=ports,
        stdin_open=True,
        detach=True,
        tty=USE_TTY,
        network='my_network',   
    )

