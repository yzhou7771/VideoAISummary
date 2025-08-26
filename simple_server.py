#!/usr/bin/env python3
"""
简化测试服务器 - 不使用OpenAI客户端，用于测试基本功能
"""

import os
import sys
from pathlib import Path
from typing import List

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv("server/.env")

app = FastAPI(title="YouTube Video Summarizer", description="Extract conclusions from YouTube videos")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SummaryResp(BaseModel):
    video_id: str
    conclusions: List[str]
    summary: str
    transcript_preview: str

@app.get("/")
async def root():
    """根路径 - 服务状态检查"""
    return {
        "message": "YouTube Video Summarizer API",
        "status": "running",
        "endpoints": {
            "summarize": "/api/summarize?video_id=VIDEO_ID&lang=zh",
            "docs": "/docs"
        }
    }

@app.get("/api/summarize", response_model=SummaryResp)
async def api_summarize_test(video_id: str = Query(...), lang: str = Query("zh")):
    """
    测试版本的总结API - 返回模拟数据
    实际使用时需要配置OpenAI API密钥
    """
    
    # 检查环境变量
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key or openai_key == "your_openai_api_key_here":
        return SummaryResp(
            video_id=video_id,
            conclusions=[
                "⚠️ 请配置 OpenAI API 密钥",
                "📝 编辑 server/.env 文件",
                "🔑 添加您的真实 API 密钥",
                "🚀 重启服务以使用完整功能"
            ],
            summary="当前为测试模式，需要配置API密钥才能使用完整功能",
            transcript_preview="这是一个测试响应..."
        )
    
    # 模拟成功响应
    if lang == "zh":
        conclusions = [
            f"📊 检测到视频ID: {video_id}",
            "🔗 后端API连接正常",
            "⚙️ 环境配置已完成",
            "✅ 准备处理真实视频内容"
        ]
        summary = "整体观点：API测试成功，系统准备就绪"
    else:
        conclusions = [
            f"📊 Detected video ID: {video_id}",
            "🔗 Backend API connection successful", 
            "⚙️ Environment configuration completed",
            "✅ Ready to process real video content"
        ]
        summary = "Overall: API test successful, system ready"
    
    return SummaryResp(
        video_id=video_id,
        conclusions=conclusions,
        summary=summary,
        transcript_preview=f"Test response for video {video_id}. In production, this would show the first 1200 characters of the transcript..."
    )

if __name__ == "__main__":
    import uvicorn
    
    print("🧪 启动测试版 YouTube 总结服务...")
    print("📡 服务运行在: http://localhost:8000")
    print("📖 API 文档: http://localhost:8000/docs")
    print("🔍 测试端点: http://localhost:8000/api/summarize?video_id=test123&lang=zh")
    print("⏹️  按 Ctrl+C 停止服务")
    print("-" * 60)
    
    uvicorn.run(
        "simple_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )