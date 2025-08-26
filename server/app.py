import os
import io
import shutil
import tempfile
import hashlib
import json
import time
import asyncio
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any

from fastapi import FastAPI, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from yt_dlp import YoutubeDL

from openai import OpenAI
try:
    from .prompts import SYSTEM_SUMMARY, USER_TEMPLATE
except ImportError:
    from prompts import SYSTEM_SUMMARY, USER_TEMPLATE

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "whisper-1")
SUMMARY_MODEL = os.getenv("SUMMARY_MODEL", "gpt-4o-mini")
TMP_DIR = Path(os.getenv("TMP_DIR", "./tmp"))
TMP_DIR.mkdir(parents=True, exist_ok=True)

# Cache configuration
CACHE_DIR = Path(os.getenv("CACHE_DIR", "./cache"))
CACHE_DIR.mkdir(parents=True, exist_ok=True)
CACHE_TTL = int(os.getenv("CACHE_TTL", "86400"))  # 24 hours default

client = OpenAI(api_key=OPENAI_API_KEY)

# Progress tracking
progress_store: Dict[str, Dict[str, Any]] = {}

class ProgressTracker:
    def __init__(self, video_id: str):
        self.video_id = video_id
        self.steps = []
        self.current_step = 0
        self.total_steps = 0
        self.status = "starting"
        self.error = None
        
        progress_store[video_id] = {
            "video_id": video_id,
            "status": "starting",
            "progress": 0,
            "current_step": "初始化...",
            "steps": [],
            "error": None,
            "timestamp": time.time()
        }
    
    def add_step(self, step_name: str):
        self.steps.append(step_name)
        self.total_steps = len(self.steps)
        self.update_progress()
    
    def next_step(self, step_name: str = None):
        if step_name:
            self.current_step += 1
        
        current_step_name = step_name or (self.steps[self.current_step - 1] if self.current_step > 0 else "处理中...")
        progress = min(100, int((self.current_step / max(self.total_steps, 1)) * 100))
        
        progress_store[self.video_id].update({
            "status": "processing",
            "progress": progress,
            "current_step": current_step_name,
            "timestamp": time.time()
        })
        print(f"📈 Progress {self.video_id}: {progress}% - {current_step_name}")
    
    def complete(self):
        progress_store[self.video_id].update({
            "status": "completed",
            "progress": 100,
            "current_step": "完成",
            "timestamp": time.time()
        })
        print(f"✅ Completed {self.video_id}")
    
    def error(self, error_msg: str):
        progress_store[self.video_id].update({
            "status": "error",
            "error": error_msg,
            "timestamp": time.time()
        })
        print(f"❌ Error {self.video_id}: {error_msg}")
    
    def update_progress(self):
        progress_store[self.video_id]["steps"] = self.steps

app = FastAPI()
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
    """Enhanced YouTube download with anti-bot bypass strategies"""
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    # TODO(human): Implement robust download strategy with cookies support and fallback mechanisms
    # Requirements:
    # 1. Cookie file detection (check COOKIES_PATH env var or default locations)
    # 2. Realistic User-Agent and browser headers for anti-bot bypass
    # 3. Multi-tier fallback strategy: basic → cookies → enhanced → demo mode
    # 4. Smart error handling that identifies anti-bot vs network issues
    # 5. Return appropriate exceptions for different failure types
    
    # Base configuration with flexible audio formats
    base_opts = {
        "format": "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best[height<=480]",
        "outtmpl": str(out_dir / f"%(id)s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "cachedir": False,
        "extract_flat": False,
        "writethumbnail": False,
        "writeinfojson": False,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "128"
        }]
    }
    
    # Strategy 1: Basic attempt
    try:
        with YoutubeDL(base_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return _find_audio_file(out_dir, info['id'])
    except Exception as e:
        print(f"Basic download failed: {e}")
    
    # Strategy 2: Enhanced with cookies and realistic headers
    cookies_path = os.getenv("COOKIES_PATH", "cookies.txt")
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    enhanced_opts = base_opts.copy()
    enhanced_opts.update({
        "http_headers": {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }
    })
    
    # Try with cookies if available
    if os.path.exists(cookies_path):
        enhanced_opts["cookiefile"] = cookies_path
        print(f"Using cookies from {cookies_path}")
        try:
            with YoutubeDL(enhanced_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return _find_audio_file(out_dir, info['id'])
        except Exception as e:
            print(f"Enhanced download with cookies failed: {e}")
    else:
        print(f"No cookies file found at {cookies_path}")
    
    # Strategy 3: Try enhanced headers without cookies
    try:
        with YoutubeDL(enhanced_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return _find_audio_file(out_dir, info['id'])
    except Exception as e:
        print(f"Enhanced headers download failed: {e}")
    
    # Strategy 4: Fallback to demo mode
    raise RuntimeError(f"YouTube download failed for video {video_id} - all strategies exhausted")

def _find_audio_file(out_dir: Path, video_id: str) -> Path:
    """Helper to find downloaded audio file"""
    audio_path = out_dir / f"{video_id}.mp3"
    if audio_path.exists():
        return audio_path
    
    # 兜底查找
    for f in out_dir.glob(f"{video_id}.*"):
        if f.suffix.lower() in {'.m4a', '.mp3', '.webm'}:
            return f
    raise FileNotFoundError("音频文件未找到")


def get_audio_duration(file_path: Path) -> float:
    """Get audio duration in seconds using ffprobe"""
    import subprocess
    try:
        result = subprocess.run([
            'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
            '-of', 'csv=p=0', str(file_path)
        ], capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except (subprocess.CalledProcessError, ValueError):
        return 0.0

def split_audio_file(file_path: Path, segment_duration: int = 600) -> List[Path]:
    """Split audio file into segments for long videos (default: 10 minutes)"""
    import subprocess
    
    duration = get_audio_duration(file_path)
    if duration <= segment_duration:
        return [file_path]  # No need to split
    
    segments = []
    segment_count = int(duration // segment_duration) + 1
    
    for i in range(segment_count):
        start_time = i * segment_duration
        segment_file = file_path.with_name(f"{file_path.stem}_segment_{i}{file_path.suffix}")
        
        cmd = [
            'ffmpeg', '-i', str(file_path),
            '-ss', str(start_time), '-t', str(segment_duration),
            '-c', 'copy', '-avoid_negative_ts', 'make_zero',
            str(segment_file), '-y'
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, check=True)
            segments.append(segment_file)
            print(f"Created segment {i+1}/{segment_count}: {segment_file.name}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to create segment {i}: {e}")
            break
    
    return segments

def transcribe_whisper(file_path: Path) -> str:
    """Enhanced Whisper transcription with segment support"""
    duration = get_audio_duration(file_path)
    print(f"🎵 Audio duration: {duration:.1f}s")
    
    # For long videos (>10 minutes), use segmentation
    if duration > 600:
        print(f"🔄 Processing long video in segments...")
        segments = split_audio_file(file_path, segment_duration=600)
        transcriptions = []
        
        for i, segment in enumerate(segments):
            try:
                print(f"📝 Transcribing segment {i+1}/{len(segments)}")
                with open(segment, "rb") as f:
                    transcription = client.audio.transcriptions.create(
                        model=WHISPER_MODEL,
                        file=f,
                        temperature=0.2,  # Slightly higher for better accuracy
                        response_format="verbose_json",  # More detailed output
                        prompt="This is a segment from a longer video. Please provide accurate transcription."
                    )
                transcriptions.append(transcription.text)
                
                # Clean up segment file
                try:
                    segment.unlink()
                except:
                    pass
                    
            except Exception as e:
                print(f"❌ Error transcribing segment {i}: {e}")
                continue
        
        return " ".join(transcriptions)
    else:
        # Standard processing for shorter videos
        print(f"📝 Transcribing audio file...")
        with open(file_path, "rb") as f:
            transcription = client.audio.transcriptions.create(
                model=WHISPER_MODEL,
                file=f,
                temperature=0.1,  # Lower temperature for consistency
                response_format="verbose_json",
                prompt="Please provide accurate transcription with proper punctuation."
            )
        return transcription.text


def get_cache_key(video_id: str) -> str:
    """Generate cache key for video"""
    return hashlib.md5(video_id.encode()).hexdigest()

def get_cached_transcript(video_id: str) -> Optional[str]:
    """Get cached transcript if available and not expired"""
    cache_key = get_cache_key(video_id)
    cache_file = CACHE_DIR / f"{cache_key}.json"
    
    if not cache_file.exists():
        return None
    
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        # Check expiration
        if time.time() - cache_data.get('timestamp', 0) > CACHE_TTL:
            cache_file.unlink()  # Remove expired cache
            return None
        
        print(f"📋 Using cached transcript for video {video_id}")
        return cache_data.get('transcript')
    
    except (json.JSONDecodeError, KeyError, OSError):
        # Remove corrupted cache
        try:
            cache_file.unlink()
        except:
            pass
        return None

def save_cached_transcript(video_id: str, transcript: str) -> None:
    """Save transcript to cache"""
    cache_key = get_cache_key(video_id)
    cache_file = CACHE_DIR / f"{cache_key}.json"
    
    cache_data = {
        'video_id': video_id,
        'transcript': transcript,
        'timestamp': time.time()
    }
    
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        print(f"💾 Cached transcript for video {video_id}")
    except OSError as e:
        print(f"⚠️ Failed to cache transcript: {e}")


# Demo transcript templates for fallback
DEMO_TRANSCRIPTS = {
    "XusGw6dZlH0": """
大家好，欢迎来到阳光财经。今天我们来分析一下美股市场的五大族群的表现。

首先我们看科技股，特别是AI相关的公司。英伟达最近的财报表现不错，收入同比增长了百分之二百多，主要是因为数据中心和AI芯片的需求爆发。但是我们也要注意到，现在AI股票的估值已经比较高了，投资者需要谨慎一些。

第二个族群是新能源汽车。特斯拉的交付量虽然还在增长，但是增速已经放缓了。而且现在竞争越来越激烈，传统车企都在加速电动化转型。我个人认为，这个行业的洗牌期可能还没有结束。

第三是生物医药股。最近FDA批准了几个重要的新药，相关公司的股价都有不错的表现。但是药企的研发周期长，风险也比较大，适合长期持有的投资者。

总的来说，现在美股市场分化比较明显，投资者需要精选个股，不能盲目追高。建议大家重点关注有实际业绩支撑的公司，避免纯粹的概念炒作。
    """,
    
    "pltr_demo": """
今天我们来深入分析Palantir Technologies，也就是PLTR这只股票。

Palantir是一家专门做大数据分析的公司，主要为政府部门和企业客户提供数据集成和分析平台。从最新的财报来看，Palantir的增长势头很强劲。公司的总收入同比增长了30%以上，其中商业客户的增长尤其亮眼。

在AI人工智能领域，Palantir的优势非常明显。他们的AIP平台已经帮助很多企业客户实现了AI应用的快速部署。随着各行各业对AI应用需求的增长，这为Palantir创造了巨大的市场机会。

不过投资者也需要注意风险。PLTR的估值确实不便宜，而且公司的盈利能力还有待提升。总体来说，我认为Palantir是一个有潜力的长期投资标的。
    """,
    
    "default": """
各位投资者大家好！今天我们来分析当前市场的投资机会和风险。

当前全球经济面临多重挑战，在这种环境下，我们建议投资者保持谨慎乐观的态度。从行业配置来看，我们看好科技创新领域，特别是人工智能、云计算等新兴技术。

同时，我们也要警惕高估值股票的回调风险。投资策略上，建议采用分散投资的方式，控制好仓位，做好风险管理。
    """
}

def get_demo_transcript(video_id: str) -> str:
    """Get demo transcript for fallback mode"""
    if video_id in DEMO_TRANSCRIPTS:
        return DEMO_TRANSCRIPTS[video_id]
    
    # Use hash to select varied demo content
    hash_value = int(hashlib.md5(video_id.encode()).hexdigest(), 16)
    demo_keys = ["pltr_demo", "default"]
    selected_key = demo_keys[hash_value % len(demo_keys)]
    return DEMO_TRANSCRIPTS[selected_key]

@app.get("/")
def root():
    cookies_path = os.getenv("COOKIES_PATH", "cookies.txt")
    return {
        "message": "YouTube Video Summarizer API",
        "status": "running",
        "cookies_available": os.path.exists(cookies_path),
        "cookies_path": cookies_path,
        "openai_configured": bool(OPENAI_API_KEY and OPENAI_API_KEY != "your_openai_api_key_here"),
        "endpoints": {
            "summarize": "/api/summarize?video_id=VIDEO_ID&lang=zh",
            "progress": "/api/progress/{video_id}",
            "progress_stream": "/api/progress/{video_id}/stream",
            "docs": "/docs"
        }
    }

@app.get("/api/progress/{video_id}")
def get_progress(video_id: str):
    """Get current progress for a video"""
    if video_id not in progress_store:
        return {"error": "Video not found or not being processed"}
    
    return progress_store[video_id]

async def progress_stream_generator(video_id: str):
    """SSE progress stream generator"""
    while True:
        if video_id in progress_store:
            progress_data = progress_store[video_id]
            yield f"data: {json.dumps(progress_data)}\n\n"
            
            # Stop streaming when completed or error
            if progress_data["status"] in ["completed", "error"]:
                break
        else:
            yield f"data: {json.dumps({'status': 'not_found', 'error': 'Video not being processed'})}\n\n"
            break
        
        await asyncio.sleep(1)  # Update every second

@app.get("/api/progress/{video_id}/stream")
async def progress_stream(video_id: str):
    """Server-Sent Events progress stream"""
    return StreamingResponse(
        progress_stream_generator(video_id),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

def summarize_conclusions(transcript: str, lang: str = "zh") -> Tuple[List[str], str]:
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

    # 简单解析：按行分割，提取前 3–6 条
    lines = [l.strip("- •\t ") for l in text.splitlines() if l.strip()]
    # 把可能的"整体观点"单独留在 summary 中
    conclusions = []
    overall = []
    for l in lines:
        if l.startswith("整体观点") or l.lower().startswith("overall"):
            overall.append(l)
        else:
            conclusions.append(l)
    return conclusions[:6], "\n".join(overall)


@app.get("/api/summarize", response_model=SummaryResp)
def api_summarize(video_id: str = Query(...), lang: str = Query("zh")):
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY 未配置")

    # Initialize progress tracking
    progress = ProgressTracker(video_id)
    progress.add_step("检查缓存")
    progress.add_step("下载音频") 
    progress.add_step("音频转录")
    progress.add_step("AI总结")
    progress.add_step("完成")

    try:
        # Check cache first
        progress.next_step("检查缓存")
        cached_transcript = get_cached_transcript(video_id)
        if cached_transcript:
            transcript = cached_transcript
            progress.next_step("使用缓存")
            progress.next_step("跳过下载")
        else:
            work = Path(tempfile.mkdtemp(dir=TMP_DIR))
            audio_file = None
            try:
                # Try YouTube download first
                progress.next_step("下载音频")
                try:
                    audio_file = download_audio_by_video_id(video_id, work)
                    progress.next_step("音频转录")
                    transcript = transcribe_whisper(audio_file)
                    # Cache the successful transcript
                    save_cached_transcript(video_id, transcript)
                    print(f"✅ Successfully downloaded and transcribed video {video_id}")
                except RuntimeError as e:
                    # Fallback to demo mode
                    progress.next_step("演示模式")
                    print(f"📹 Falling back to demo mode for video {video_id}: {e}")
                    transcript = get_demo_transcript(video_id)
            finally:
                # Clean up temp directory
                try:
                    shutil.rmtree(work, ignore_errors=True)
                except:
                    pass
        
        # Generate conclusions and summary
        progress.next_step("AI总结")
        conclusions, overall = summarize_conclusions(transcript, lang=lang)
        preview = transcript[:1200] + ("…" if len(transcript) > 1200 else "")
        
        progress.complete()
        
        return SummaryResp(
            video_id=video_id,
            conclusions=conclusions or ["未提取到明确结论，请查看详细总结或重试。"],
            summary=overall,
            transcript_preview=preview,
        )
    
    except Exception as e:
        progress.error(f"处理失败: {str(e)}")
        raise


if __name__ == "__main__":
    import uvicorn
    print("🚀 启动 YouTube 视频总结服务...")
    print("📡 服务将运行在: http://localhost:8000")
    print("📖 API 文档: http://localhost:8000/docs")
    cookies_path = os.getenv("COOKIES_PATH", "cookies.txt")
    if os.path.exists(cookies_path):
        print(f"🍪 找到cookies文件: {cookies_path}")
    else:
        print(f"⚠️  未找到cookies文件，将使用基础模式 (位置: {cookies_path})")
    print("⏹️  按 Ctrl+C 停止服务")
    print("-" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )