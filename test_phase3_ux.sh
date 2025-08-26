#!/bin/bash

echo "🎬 YouTube AI总结系统 - Phase 3 用户体验测试"
echo "=============================================="

# 测试服务器状态检查
echo ""
echo "📋 1. 测试服务器状态检查..."
curl -s http://localhost:8000/ | jq '{
    message,
    status,
    cookies_available,
    openai_configured
}'

echo ""
echo "📋 2. 测试进度跟踪系统..."
echo "开始处理视频（后台）..."

# 启动视频处理（使用一个较长的视频来测试进度）
VIDEO_ID="dQw4w9WgXcQ"
curl -s "http://localhost:8000/api/summarize?video_id=$VIDEO_ID&lang=zh" > /dev/null &
PROCESS_PID=$!

# 等待1秒让处理开始
sleep 1

echo "检查进度状态..."
for i in {1..5}; do
    echo "进度检查 #$i:"
    curl -s "http://localhost:8000/api/progress/$VIDEO_ID" | jq -r '
        if .status == "processing" then
            "🔄 " + .current_step + " (" + (.progress | tostring) + "%)"
        elif .status == "completed" then
            "✅ 处理完成"
        elif .status == "error" then
            "❌ 错误: " + .error
        else
            "📋 状态: " + (.detail // "未找到")
        end
    ' 2>/dev/null || echo "⏳ 进度信息暂不可用"
    
    sleep 2
done

echo ""
echo "📋 3. 测试错误处理..."
echo "测试无效视频ID:"
curl -s "http://localhost:8000/api/summarize?video_id=invalid_video_id&lang=zh" | jq -r '.detail // .error // "处理结果未知"'

echo ""
echo "📋 4. 测试不同语言支持..."
echo "英文总结测试:"
curl -s "http://localhost:8000/api/summarize?video_id=9bZkp7q19f0&lang=en" | jq '{
    video_id,
    conclusions_count: (.conclusions | length),
    summary_preview: (.summary[0:100] + "..."),
    language: "en"
}'

echo ""
echo "🎉 Phase 3 用户体验测试完成!"
echo ""
echo "✨ 新功能总结:"
echo "• 实时进度跟踪 - 用户可以看到处理进度"
echo "• 服务器状态检查 - 启动前验证连接"
echo "• 智能错误处理 - 详细的错误信息和建议"
echo "• Cookies过期提醒 - 主动提示用户更新认证"
echo "• 视觉进度条 - 直观的处理状态显示"
echo "• 自动错误恢复 - 网络错误重试机制"