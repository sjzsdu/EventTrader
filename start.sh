#!/bin/sh

VENV_PATH="./venv"

# 检查并获取合适的 Python 命令
get_python_cmd() {
    if command -v python3 >/dev/null 2>&1; then
        python_cmd="python3"
    elif command -v python >/dev/null 2>&1; then
        python_cmd="python"
    else
        echo "Error: Python not found" >&2
        exit 1
    fi

    version=$($python_cmd -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
    if [ "$(echo "$version >= 3.10" | bc)" -eq 1 ]; then
        echo $python_cmd
    else
        echo "Error: Python 3.10 or higher is required. Found version: $version" >&2
        exit 1
    fi
}

# 获取合适的 Python 命令
PYTHON_CMD=$(get_python_cmd)

# 激活虚拟环境
echo "Activating virtual environment..."
. $VENV_PATH/bin/activate
if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment." >&2
    exit 1
fi

# 运行 main.py
echo "Running main.py with --allindex"
$PYTHON_CMD main.py start --allindex