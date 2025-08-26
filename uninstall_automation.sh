#!/bin/bash

echo "🗑️  卸载 YouTube Video Summarizer 自动启动服务"
echo "================================================"

LAUNCHD_DIR="$HOME/Library/LaunchAgents"
START_PLIST="com.youtube.summarizer.plist"
STOP_PLIST="com.youtube.summarizer.stop.plist"
USER_LAUNCHD_DIR="$HOME/Library/LaunchAgents.user"

# 停止服务器
echo "🛑 停止服务器..."
./stop_server.sh

# 卸载 launchd 服务
echo "📋 卸载 launchd 服务..."
launchctl unload "$LAUNCHD_DIR/$START_PLIST" 2>/dev/null || true
launchctl unload "$LAUNCHD_DIR/$STOP_PLIST" 2>/dev/null || true
launchctl unload "$USER_LAUNCHD_DIR/$START_PLIST" 2>/dev/null || true
launchctl unload "$USER_LAUNCHD_DIR/$STOP_PLIST" 2>/dev/null || true

# 删除 plist 文件
for dir in "$LAUNCHD_DIR" "$USER_LAUNCHD_DIR"; do
    for plist in "$START_PLIST" "$STOP_PLIST"; do
        if [ -f "$dir/$plist" ]; then
            rm "$dir/$plist"
            echo "✅ 删除 launchd 配置文件: $dir/$plist"
        fi
    done
done

# 卸载 cron 任务
echo "📋 检查并移除 cron 任务..."
if crontab -l 2>/dev/null | grep -q "start_server.sh\|stop_server.sh"; then
    # 移除包含 start_server.sh 和 stop_server.sh 的 cron 任务
    crontab -l 2>/dev/null | grep -v "start_server.sh\|stop_server.sh" | crontab - 2>/dev/null || true
    echo "✅ 删除 cron 定时任务"
fi

# 检查服务状态
REMOVED_SOMETHING=false

if launchctl list | grep -q "com.youtube.summarizer"; then
    echo "⚠️  LaunchD 服务可能仍在运行，请手动检查"
else
    REMOVED_SOMETHING=true
fi

if crontab -l 2>/dev/null | grep -q "start_server.sh\|stop_server.sh"; then
    echo "⚠️  Cron 任务可能仍存在，请手动检查"
else
    REMOVED_SOMETHING=true
fi

if [ "$REMOVED_SOMETHING" = true ]; then
    echo "✅ 自动化服务卸载成功！"
fi

echo ""
echo "📝 注意："
echo "  - 脚本文件仍保留在项目目录"
echo "  - 日志文件保留在 ~/Library/Logs/"
echo "  - 可以随时重新安装：./install_automation.sh"