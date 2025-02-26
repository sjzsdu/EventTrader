#!/bin/sh

# 检查 LOOP_INTERVAL 是否设置，如果没有设置，默认为 10 分钟
INTERVAL=${LOOP_INTERVAL:-10}
VENV_PATH="./venv"

# 定义一个函数来检查 Python 版本
check_python_version() {
    if command -v python3 >/dev/null 2>&1; then
        python3 -c "import sys; exit(0 if sys.version_info >= (3,10) else 1)" >/dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo "python3"
            return
        fi
    fi
    if command -v python >/dev/null 2>&1; then
        python -c "import sys; exit(0 if sys.version_info >= (3,10) else 1)" >/dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo "python"
            return
        fi
    fi
    echo "No suitable Python version found (3.10+ required)" >&2
    exit 1
}

# 创建并激活虚拟环境
create_and_activate_venv() {
    echo "Creating virtual environment..."
    $PYTHON_CMD -m venv $VENV_PATH
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment." >&2
        exit 1
    fi
    
    echo "Activating virtual environment..."
    . $VENV_PATH/bin/activate
    if [ $? -ne 0 ]; then
        echo "Failed to activate virtual environment." >&2
        exit 1
    fi
}

# 检查并安装 Poetry
check_and_install_poetry() {
    if ! command -v poetry >/dev/null 2>&1; then
        echo "Poetry not found. Installing Poetry..."
        curl -sSL https://install.python-poetry.org | python -
    fi
    
    if ! command -v poetry >/dev/null 2>&1; then
        echo "Failed to install Poetry. Please install it manually." >&2
        exit 1
    fi
}

# 安装项目依赖
install_dependencies() {
    echo "Installing project dependencies..."
    poetry install
    if [ $? -ne 0 ]; then
        echo "Failed to install dependencies. Please check your pyproject.toml file and try again." >&2
        exit 1
    fi
}

# 获取合适的 Python 命令
PYTHON_CMD=$(check_python_version)

# 创建并激活虚拟环境
create_and_activate_venv

# 检查并安装 Poetry
check_and_install_poetry

# 安装项目依赖
install_dependencies

while true; do
    echo "Running main.py with --allindex"
    poetry run python main.py start --allindex
    echo "Waiting for $INTERVAL minutes before next execution"
    sleep $(( INTERVAL * 60 ))
done