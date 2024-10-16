import docker, sys, os
from loguru import logger

src_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

DEFAULT_BIND_HOST = "127.0.0.1"
os.environ["DEFAULT_BIND_HOST"] = DEFAULT_BIND_HOST
CONTRAINER_NAME = "muagent"

OLLAMA_CONTRAINER_NAME = "local_ollama"
OLLAMA_IMAGE_NAME = "ollama/ollama"
OLLAMA_HOST = os.environ.get("OLLAMA_HOST") or DEFAULT_BIND_HOST 
OLLAMA_SERVER = {
    "host": f"http://{OLLAMA_HOST}",
    "port": 5050,
    "docker_port": 5050,
    "url": f"http://{OLLAMA_HOST}:11434",
    "do_remote": True,
}

SANDBOX_CONTRAINER_NAME = "devopsgpt_sandbox"
SANDBOX_IMAGE_NAME = "kuafuai/devopsgpt"
SANDBOX_HOST = os.environ.get("SANDBOX_HOST") or DEFAULT_BIND_HOST # "172.25.0.3"
SANDBOX_SERVER = {
    "host": f"http://{SANDBOX_HOST}",
    "port": 5050,
    "docker_port": 5050,
    "url": f"http://{SANDBOX_HOST}:5050",
    "do_remote": True,
}

from start import check_docker, check_process

try:
    client = docker.from_env()
except:
    client = None


def stop_main():
    #
    check_docker(client, OLLAMA_CONTRAINER_NAME, do_stop=True, )
    # 
    check_docker(client, SANDBOX_CONTRAINER_NAME, do_stop=True, )
    # 
    check_docker(client, CONTRAINER_NAME, do_stop=True, )


if __name__ == "__main__":
    stop_main()