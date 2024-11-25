#!/bin/bash


# while network is error, `docker-compose up -d` might error
# so we add a script for pulling dependent images befort `docker-compose up -d`

# 国内镜像源，根据需要自行配置，不一定完全生效
# 搜索引擎搜 ”DockerHub国内镜像源列表“ 即可
#   "registry-mirrors": []


# pull images from dockerhub docker.io
docker pull vesoft/nebula-metad:v3.8.0
docker pull vesoft/nebula-storaged:v3.8.0
docker pull vesoft/nebula-graphd:v3.8.0
docker pull redis/redis-stack:7.4.0-v0
docker pull ollama/ollama:0.3.6

# pull images from github ghcr.io by nju
docker pull ghcr.nju.edu.cn/runtime:0.1.0
docker pull ghcr.nju.edu.cn/muagent:0.1.0
docker pull ghcr.nju.edu.cn/ekgfrontend:0.1.0

# # pull images from github ghcr.io
# docker pull ghcr.io/runtime:0.1.0
# docker pull ghcr.io/muagent:0.1.0
# docker pull ghcr.io/ekgfrontend:0.1.0
