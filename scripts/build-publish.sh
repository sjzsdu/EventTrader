#!/bin/bash

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# 获取项目根目录路径
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." &> /dev/null && pwd )"

# 设置变量
IMAGE_NAME="sjzsdu/event_trader"
VERSION=$(grep -m1 version "${PROJECT_ROOT}/pyproject.toml" | cut -d'"' -f2)
IMAGE_TAG="${VERSION}"

# 定义检查状态的函数
check_status() {
    if [ $? -ne 0 ]; then
        echo "错误: $1"
        exit 1
    fi
}

# 检查是否成功获取版本号
if [ -z "$VERSION" ]; then
    echo "错误: 无法从 ${PROJECT_ROOT}/pyproject.toml 文件中获取版本号"
    exit 1
fi

echo "使用版本号: ${VERSION}"

# 构建 Docker 镜像
echo "正在构建 Docker 镜像..."
docker build -t ${IMAGE_NAME}:${IMAGE_TAG} "${PROJECT_ROOT}"
check_status "Docker 镜像构建失败"

# 检查镜像是否成功创建
echo "检查镜像是否创建成功..."
docker image inspect ${IMAGE_NAME}:${IMAGE_TAG} > /dev/null 2>&1
check_status "无法找到刚刚构建的镜像"

# Docker Hub 登录
echo "正在登录到 Docker Hub..."
if [ -n "$DOCKER_USERNAME" ] && [ -n "$DOCKER_PASSWORD" ]; then
    # GitHub Actions 环境
    echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
else
    # 本地环境
    docker login
fi
check_status "Docker Hub 登录失败"

# 推送镜像到 Docker Hub
echo "正在推送镜像到 Docker Hub..."
docker push ${IMAGE_NAME}:${IMAGE_TAG}
check_status "推送镜像到 Docker Hub 失败"

# 标记并推送 latest 标签
echo "正在标记并推送 latest 标签..."
docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest
docker push ${IMAGE_NAME}:latest
check_status "推送 latest 标签失败"

echo "操作完成"
