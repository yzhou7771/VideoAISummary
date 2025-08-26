#!/bin/bash

# Alfred Workflow 脚本
# 关键词：yt start / yt stop / yt status

case "$1" in
    "start")
        ./start_server.sh
        ;;
    "stop") 
        ./stop_server.sh
        ;;
    "status")
        if pgrep -f "server/app.py" > /dev/null; then
            echo "🟢 YouTube Summarizer is running"
        else
            echo "🔴 YouTube Summarizer is not running"
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|status}"
        ;;
esac