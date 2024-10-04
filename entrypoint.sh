#!/bin/sh

export BASE_DIR=

CORE_COUNT=$(python -c "import os; print(os.cpu_count())")

WORKERS=$((CORE_COUNT * 2 + 1))

#gunicorn config.asgi:application -w $WORKERS -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --log-level debug --access-logfile -

# 启动 Gunicorn 服务器，使用 --preload 选项以减少内存占用和加快启动时间
exec gunicorn config.asgi:application \
    --preload \  # 预加载应用以减少内存占用
    -w $WORKERS \  # 设置 worker 数量
    -k uvicorn.workers.UvicornWorker \  # 使用 Uvicorn worker 处理 ASGI 请求
    --bind 0.0.0.0:8000 \  # 绑定到 8000 端口
    --log-level debug \  # 设置日志级别为 debug
    --access-logfile -  # 将访问日志输出到控制台