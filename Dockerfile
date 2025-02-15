# 使用官方 Python 运行时作为父镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libv8-dev \
    && rm -rf /var/lib/apt/lists/*

# 安装 poetry
RUN pip install --no-cache-dir poetry

# 复制项目文件
COPY pyproject.toml poetry.lock ./

# 安装依赖，但不安装开发依赖
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-root

# 复制应用代码和入口脚本
COPY . .

# 设置环境变量
ENV PYTHONUNBUFFERED=1

# 声明卷
VOLUME ["/app/params", "/app/market", "/app/cache"]

# 使用 entrypoint.sh 作为容器的入口点
ENTRYPOINT ["bash", "/app/entrypoint.sh"]
