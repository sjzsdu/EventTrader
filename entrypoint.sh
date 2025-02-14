#!/bin/sh

# 检查 LOOP_INTERVAL 是否设置，如果没有设置，默认为 10 分钟
INTERVAL=${LOOP_INTERVAL:-10}

while true; do
    echo "Running main.py with --allindex"
    python main.py --allindex
    echo "Waiting for $INTERVAL minutes before next execution"
    sleep $(( INTERVAL * 60 ))
done
