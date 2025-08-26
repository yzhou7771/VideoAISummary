#!/usr/bin/env python3
"""
完整功能服务器启动脚本 - 包含真实AI功能
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import List

# 添加server目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'server'))

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from yt_dlp import YoutubeDL

# 加载环境变量
load_dotenv("server/.env")

# 检查OpenAI配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "whisper-1")
SUMMARY_MODEL = os.getenv("SUMMARY_MODEL", "gpt-4o-mini")
TMP_DIR = Path(os.getenv("TMP_DIR", "./tmp"))
TMP_DIR.mkdir(parents=True, exist_ok=True)

print(f"🔑 OpenAI API Key: {'✅ 已配置' if OPENAI_API_KEY and OPENAI_API_KEY != 'your_openai_api_key_here' else '❌ 未配置'}")
print(f"🎤 Whisper Model: {WHISPER_MODEL}")  
print(f"🧠 Summary Model: {SUMMARY_MODEL}")
print(f"📁 临时目录: {TMP_DIR}")

# 尝试导入和初始化OpenAI客户端
try:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    print("✅ OpenAI 客户端初始化成功")
except Exception as e:
    print(f"❌ OpenAI 客户端初始化失败: {e}")
    client = None

# 导入提示词模板
try:
    from prompts import SYSTEM_SUMMARY, USER_TEMPLATE
    print("✅ 提示词模板加载成功")
except ImportError as e:
    print(f"❌ 提示词模板加载失败: {e}")
    # 内嵌提示词作为后备
    SYSTEM_SUMMARY = "你是资深投研助手。请基于转录文本，提炼【3–5条】'结论/要点'。"
    USER_TEMPLATE = "目标语言: {lang}\n\n以下是转录文本：\n\n{transcript}\n\n请输出3–5条要点。"

app = FastAPI(title="YouTube Video Summarizer - Full Version", description="Complete AI-powered video analysis")

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

def download_audio_by_video_id(video_id: str, out_dir: Path) -> Path:
    """下载YouTube视频音频"""
    url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(out_dir / f"%(id)s.%(ext)s"),
        "noplaylist": True,
        "quiet": False,  # 显示详细输出以便调试
        "no_warnings": False,
        "cachedir": False,
        # 反机器人检测设置
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        },
        "extractor_retries": 3,
        "fragment_retries": 10,
        "retry_sleep_functions": {"http": lambda n: min(4 * n, 60)},
        # 使用cookies（如果有的话）
        "cookiefile": None,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192"
        }]
    }
    
    print(f"🎵 开始下载音频: {url}")
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        audio_path = out_dir / f"{info['id']}.mp3"
        if not audio_path.exists():
            # 兜底查找
            for f in out_dir.glob(f"{info['id']}.*"):
                if f.suffix.lower() in {'.m4a', '.mp3', '.webm'}:
                    print(f"✅ 音频下载成功: {f}")
                    return f
            raise FileNotFoundError("音频文件未找到")
        print(f"✅ 音频下载成功: {audio_path}")
        return audio_path

def transcribe_whisper(file_path: Path) -> str:
    """使用Whisper API转录音频"""
    if not client:
        raise HTTPException(status_code=500, detail="OpenAI客户端未初始化")
    
    print(f"🎤 开始转录音频: {file_path}")
    with open(file_path, "rb") as f:
        transcription = client.audio.transcriptions.create(
            model=WHISPER_MODEL,
            file=f,
            temperature=0,
            response_format="json"
        )
    
    transcript = transcription.text
    print(f"✅ 转录完成，长度: {len(transcript)} 字符")
    return transcript

def summarize_conclusions(transcript: str, lang: str = "zh") -> tuple[List[str], str]:
    """使用GPT生成结论总结"""
    if not client:
        raise HTTPException(status_code=500, detail="OpenAI客户端未初始化")
    
    print(f"🧠 开始AI总结，输入长度: {len(transcript)} 字符")
    
    sys_prompt = SYSTEM_SUMMARY
    user_prompt = USER_TEMPLATE.format(lang=lang, transcript=transcript[:18000])  # 防止超长

    resp = client.chat.completions.create(
        model=SUMMARY_MODEL,
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2,
    )
    text = resp.choices[0].message.content.strip()
    print(f"✅ AI总结完成")

    # 简单解析：按行分割，提取前3–6条
    lines = [l.strip("- •\t ") for l in text.splitlines() if l.strip()]
    conclusions = []
    overall = []
    for l in lines:
        if l.startswith("整体观点") or l.lower().startswith("overall"):
            overall.append(l)
        else:
            conclusions.append(l)
    return conclusions[:6], "\n".join(overall)

@app.get("/")
async def root():
    """根路径 - 服务状态检查"""
    return {
        "message": "YouTube Video Summarizer API - Full Version",
        "status": "running",
        "openai_configured": bool(client),
        "endpoints": {
            "summarize": "/api/summarize?video_id=VIDEO_ID&lang=zh",
            "docs": "/docs"
        }
    }

@app.get("/api/summarize", response_model=SummaryResp)
async def api_summarize(video_id: str = Query(...), lang: str = Query("zh")):
    """完整版总结API - 真实AI处理"""
    
    if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
        raise HTTPException(
            status_code=400, 
            detail="请配置有效的OpenAI API密钥"
        )
    
    if not client:
        raise HTTPException(
            status_code=500, 
            detail="OpenAI客户端未初始化"
        )

    print(f"📹 开始处理视频: {video_id}")
    work = Path(tempfile.mkdtemp(dir=TMP_DIR))
    
    try:
        # 1. 下载音频
        audio_file = download_audio_by_video_id(video_id, work)
        
        # 2. 转录音频
        transcript = transcribe_whisper(audio_file)
        
        # 3. AI总结
        conclusions, overall = summarize_conclusions(transcript, lang=lang)

        # 4. 生成预览
        preview = transcript[:1200] + ("…" if len(transcript) > 1200 else "")
        
        result = SummaryResp(
            video_id=video_id,
            conclusions=conclusions or ["未提取到明确结论，请查看详细总结或重试。"],
            summary=overall,
            transcript_preview=preview,
        )
        
        print(f"🎉 处理完成: {len(conclusions)} 条结论")
        return result
        
    except Exception as e:
        print(f"❌ 处理出错: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # 清理临时目录
        try:
            shutil.rmtree(work, ignore_errors=True)
        except Exception:
            pass

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 启动完整版 YouTube 总结服务...")
    print("📡 服务将运行在: http://localhost:8000")
    print("📖 API 文档: http://localhost:8000/docs")
    print("⚠️  请确保已配置有效的OpenAI API密钥")
    print("⏹️  按 Ctrl+C 停止服务")
    print("-" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )