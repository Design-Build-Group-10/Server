#!/bin/sh

export BASE_DIR=

CORE_COUNT=$(python -c "import os; print(os.cpu_count())")

WORKERS=$((CORE_COUNT * 2 + 1))

gunicorn config.asgi:application -w $WORKERS -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --log-level debug --access-logfile -