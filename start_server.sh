#!/bin/bash

# YouTube Video Summarizer 自动启动脚本
LOG_FILE="$HOME/Library/Logs/youtube_summarizer.log"
PID_FILE="$HOME/Library/Logs/youtube_summarizer.pid"
PROJECT_DIR="/Users/amber/Workspace/Projects/YoutubeSummary"

# 记录启动时间
echo "[$(date)] Starting YouTube Video Summarizer Server..." >> "$LOG_FILE"

# 检查是否已经在运行
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "[$(date)] Server already running with PID: $OLD_PID" >> "$LOG_FILE"
        exit 0
    else
        rm "$PID_FILE"
    fi
fi

# 切换到项目目录
cd "$PROJECT_DIR" || {
    echo "[$(date)] ERROR: Cannot access project directory" >> "$LOG_FILE"
    exit 1
}

# 检查Python环境
PYTHON_CMD="python"
if ! command -v python &> /dev/null; then
    PYTHON_CMD="python3"
    if ! command -v python3 &> /dev/null; then
        echo "[$(date)] ERROR: Python not found" >> "$LOG_FILE"
        exit 1
    fi
fi
echo "[$(date)] Using Python command: $PYTHON_CMD" >> "$LOG_FILE"

# 检查依赖
if [ ! -f "server/app.py" ]; then
    echo "[$(date)] ERROR: server/app.py not found" >> "$LOG_FILE"
    exit 1
fi

# 启动服务器
echo "[$(date)] Starting server..." >> "$LOG_FILE"
nohup $PYTHON_CMD server/app.py >> "$LOG_FILE" 2>&1 &
SERVER_PID=$!

# 保存PID
echo $SERVER_PID > "$PID_FILE"

# 等待几秒检查启动状态
sleep 3
if ps -p $SERVER_PID > /dev/null 2>&1; then
    echo "[$(date)] Server started successfully with PID: $SERVER_PID" >> "$LOG_FILE"
    
    # 发送桌面通知
    osascript -e 'display notification "YouTube Video Summarizer 已启动" with title "AI总结服务" sound name "Glass"'
else
    echo "[$(date)] ERROR: Server failed to start" >> "$LOG_FILE"
    rm -f "$PID_FILE"
    exit 1
fi