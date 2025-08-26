#!/bin/bash

echo "🧪 YouTube Cookies功能测试脚本"
echo "=================================="

# 检查cookies文件
COOKIES_PATH="/Users/amber/Workspace/Projects/YoutubeSummary/server/cookies.txt"

if [ -f "$COOKIES_PATH" ]; then
    echo "✅ Cookies文件存在: $COOKIES_PATH"
    echo "📁 文件大小: $(ls -lh "$COOKIES_PATH" | awk '{print $5}')"
    echo "📅 修改时间: $(ls -l "$COOKIES_PATH" | awk '{print $6, $7, $8}')"
else
    echo "❌ Cookies文件不存在: $COOKIES_PATH"
    echo "   请按照指南导出并放置cookies.txt文件"
    exit 1
fi

echo ""
echo "🌐 检查服务器状态..."
curl -s http://localhost:8000/ | jq '{
    cookies_available, 
    cookies_path, 
    openai_configured,
    message
}'

echo ""
echo "🎬 测试YouTube视频下载..."
echo "使用真实YouTube视频ID测试："

# 使用一个短视频进行测试
TEST_VIDEO="dQw4w9WgXcQ"  # Rick Roll - 经典测试视频
echo "视频ID: $TEST_VIDEO"

curl -s "http://localhost:8000/api/summarize?video_id=$TEST_VIDEO&lang=zh" | jq '{
    video_id,
    conclusions: .conclusions[0:2],
    summary: .summary[0:100] + "...",
    transcript_preview: .transcript_preview[0:200] + "..."
}'

echo ""
echo "🎉 测试完成！"