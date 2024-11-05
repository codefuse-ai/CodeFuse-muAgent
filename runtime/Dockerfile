# 使用官方的OpenJDK 17镜像作为基础镜像
##  docker pull maven:3.8-openjdk-17-slim
FROM openjdk:17

## 创建工作目录
WORKDIR /app

## 将源代码复制到工作目录
COPY ./bootstrap/muagent-runtime.jar /app/


# 指定容器启动时运行的命令
CMD ["java", "-jar", "/app/muagent-runtime.jar"]