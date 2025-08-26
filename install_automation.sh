#!/bin/bash

echo "🤖 安装 YouTube Video Summarizer 自动启动服务"
echo "================================================"

PROJECT_DIR="/Users/amber/Workspace/Projects/YoutubeSummary"
LAUNCHD_DIR="$HOME/Library/LaunchAgents"
START_PLIST="com.youtube.summarizer.plist"
STOP_PLIST="com.youtube.summarizer.stop.plist"

# 创建日志目录
mkdir -p "$HOME/Library/Logs"

# 设置脚本执行权限
echo "📝 设置脚本权限..."
chmod +x "$PROJECT_DIR/start_server.sh"
chmod +x "$PROJECT_DIR/stop_server.sh"

# 检查和修复 LaunchAgents 目录权限
echo "🔧 检查 LaunchAgents 目录..."
if [ ! -w "$HOME/Library/LaunchAgents" ]; then
    echo "⚠️  LaunchAgents 目录权限不足，尝试修复..."
    mkdir -p "$HOME/Library/LaunchAgents.user"
    LAUNCHD_DIR="$HOME/Library/LaunchAgents.user"
    echo "📁 使用用户专用目录: $LAUNCHD_DIR"
fi

# 创建 LaunchAgents 目录
mkdir -p "$LAUNCHD_DIR"

# 复制 plist 文件
echo "📋 安装 launchd 配置..."
cp "$PROJECT_DIR/$START_PLIST" "$LAUNCHD_DIR/$START_PLIST"
cp "$PROJECT_DIR/$STOP_PLIST" "$LAUNCHD_DIR/$STOP_PLIST"

# 加载服务
echo "🔄 加载 launchd 服务..."
launchctl load "$LAUNCHD_DIR/$START_PLIST" 2>/dev/null && \
launchctl load "$LAUNCHD_DIR/$STOP_PLIST" 2>/dev/null || {
    echo "⚠️  标准 launchd 加载失败，尝试替代方案..."
    # 使用 cron 作为备选方案
    echo "🔄 设置 crontab 定时任务..."
    
    # 创建cron任务（周二到周六）
    (crontab -l 2>/dev/null || true; echo "0 9 * * 2-6 $PROJECT_DIR/start_server.sh") | sort -u | crontab -
    (crontab -l 2>/dev/null || true; echo "0 16 * * 2-6 $PROJECT_DIR/stop_server.sh") | sort -u | crontab -
    echo "✅ Cron 任务已设置（工作日上午9点启动，下午4点停止）"
}

# 检查服务状态
echo "✅ 检查安装结果..."

# 检查launchd服务
if launchctl list | grep -q "com.youtube.summarizer" && launchctl list | grep -q "com.youtube.summarizer.stop"; then
    echo "✅ LaunchD 服务安装成功（启动+停止）！"
    SERVICE_TYPE="LaunchD"
elif crontab -l 2>/dev/null | grep -q "start_server.sh"; then
    echo "✅ Cron 定时任务安装成功！"
    SERVICE_TYPE="Cron"
else
    echo "❌ 自动化服务安装失败"
    SERVICE_TYPE="None"
fi

if [ "$SERVICE_TYPE" != "None" ]; then
    echo ""
    echo "📅 工作日自动化："
    echo "  🌅 启动时间：周二至周六上午 9:00"
    echo "  🌆 停止时间：周二至周六下午 4:00"
    echo "📊 服务类型：$SERVICE_TYPE"
    echo "📝 日志位置：$HOME/Library/Logs/youtube_summarizer.log"
    echo ""
    echo "🔧 管理命令："
    echo "  手动启动：./start_server.sh"
    echo "  手动停止：./stop_server.sh"
    echo "  卸载服务：./uninstall_automation.sh"
    echo "  查看日志：tail -f ~/Library/Logs/youtube_summarizer.log"
    
    if [ "$SERVICE_TYPE" = "Cron" ]; then
        echo "  查看定时任务：crontab -l"
    fi
else
    echo ""
    echo "🔧 手动设置："
    echo "  可以手动运行 ./start_server.sh 启动服务"
    echo "  或者在系统偏好设置中添加登录项"
fi