#!/bin/bash

# YouTube Video Summarizer 停止脚本
LOG_FILE="$HOME/Library/Logs/youtube_summarizer.log"
PID_FILE="$HOME/Library/Logs/youtube_summarizer.pid"

echo "[$(date)] Stopping YouTube Video Summarizer Server..." >> "$LOG_FILE"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        # 尝试优雅停止
        kill -TERM "$PID"
        sleep 2
        
        # 检查是否还在运行
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "[$(date)] Force killing process $PID..." >> "$LOG_FILE"
            kill -KILL "$PID"
        fi
        
        echo "[$(date)] Server stopped (PID: $PID)" >> "$LOG_FILE"
        
        # 发送桌面通知
        osascript -e 'display notification "YouTube Video Summarizer 已停止" with title "AI总结服务" sound name "Glass"'
    else
        echo "[$(date)] Server not running" >> "$LOG_FILE"
    fi
    
    rm -f "$PID_FILE"
else
    echo "[$(date)] PID file not found, attempting to find and kill process..." >> "$LOG_FILE"
    
    # 尝试通过端口找到进程
    PID=$(lsof -ti:8000)
    if [ -n "$PID" ]; then
        kill -TERM "$PID"
        echo "[$(date)] Killed process using port 8000 (PID: $PID)" >> "$LOG_FILE"
    else
        echo "[$(date)] No process found using port 8000" >> "$LOG_FILE"
    fi
fi