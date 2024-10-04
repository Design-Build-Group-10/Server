#!/bin/sh

export BASE_DIR=

CORE_COUNT=$(python -c "import os; print(os.cpu_count())")

WORKERS=$((CORE_COUNT * 2 + 1))

#gunicorn config.asgi:application -w $WORKERS -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --log-level debug --access-logfile -

# 启动 Gunicorn 服务器，使用 --preload 选项以减少内存占用和加快启动时间
gunicorn config.asgi:application --preload -w $WORKERS -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --log-level debug --access-logfile - --timeout 1000