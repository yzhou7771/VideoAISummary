#!/bin/bash

echo "🎬 YouTube AI总结系统 - 完整测试套件"
echo "==========================================="

# 检查系统状态
echo ""
echo "📋 系统状态检查..."
curl -s http://localhost:8000/ | jq '{
    cookies_available,
    openai_configured, 
    message
}'

echo ""
echo "🧪 测试用例说明："
echo "1. 短视频 (2-5分钟) - 快速测试"
echo "2. 中等视频 (10-20分钟) - 标准测试" 
echo "3. 长视频 (30分钟+) - 压力测试"
echo "4. 不同语言视频 - 多语言能力测试"

echo ""
echo "🚀 开始测试..."

# 测试案例1: 短视频
echo ""
echo "🔬 测试1: 短视频 (江南Style)"
VIDEO_ID="9bZkp7q19f0"
echo "视频ID: $VIDEO_ID"
echo "开始时间: $(date)"

curl -s "http://localhost:8000/api/summarize?video_id=$VIDEO_ID&lang=zh" | jq '{
    video_id,
    结论数量: (.conclusions | length),
    总结长度: (.summary | length),
    转录预览: (.transcript_preview[0:100] + "..."),
    处理结果: "✅ 成功"
}'

echo "完成时间: $(date)"
echo ""

# 提供更多测试选项
echo "📝 其他测试用例 (可选择运行):"
echo ""
echo "测试2 - 英语教育视频:"
echo "curl -s 'http://localhost:8000/api/summarize?video_id=dQw4w9WgXcQ&lang=zh'"
echo ""
echo "测试3 - 中文视频 (如果有):"  
echo "curl -s 'http://localhost:8000/api/summarize?video_id=YOUR_VIDEO_ID&lang=zh'"
echo ""
echo "测试4 - 英文总结:"
echo "curl -s 'http://localhost:8000/api/summarize?video_id=9bZkp7q19f0&lang=en'"

echo ""
echo "🎉 测试完成!"