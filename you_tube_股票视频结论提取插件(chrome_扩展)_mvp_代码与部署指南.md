# YouTube 股票视频结论提取插件（Chrome 扩展）— MVP 代码与部署指南

> 目标：在 YouTube 视频页一键获取“结论/要点”（中文为主、无外挂字幕、10–30 分钟）。
>
> 架构：**浏览器扩展（前端 UI + 抓取视频ID） → 后端（下载音频 + Whisper 转录） → LLM 总结 → 返回 3–5 条结论**。

---

## 目录
1. 项目结构
2. Chrome 扩展（前端）代码
3. 后端（FastAPI + yt-dlp + OpenAI Whisper & GPT）代码
4. 运行与配置
5. 可选：成本/性能优化开关
6. 后续增强建议

---

## 1) 项目结构

```
yt-summary-extension/
├─ extension/
│  ├─ manifest.json
│  ├─ popup.html
│  ├─ popup.js
│  ├─ content.js
│  ├─ styles.css
│  └─ icons/
│     └─ icon128.png
└─ server/
   ├─ app.py
   ├─ prompts.py
   ├─ requirements.txt
   └─ .env.example
```

---

## 2) Chrome 扩展（前端）

### `manifest.json` (MV3)
```json
{
  "manifest_version": 3,
  "name": "YT 股票视频结论提取",
  "version": "0.1.0",
  "description": "在 YouTube 视频页一键生成 3–5 条核心结论（中文）。",
  "permissions": ["activeTab", "storage"],
  "host_permissions": [
    "https://www.youtube.com/*",
    "https://m.youtube.com/*"
  ],
  "action": {
    "default_popup": "popup.html",
    "default_title": "提取结论"
  },
  "icons": {"128": "icons/icon128.png"},
  "content_scripts": [
    {
      "matches": ["https://www.youtube.com/*", "https://m.youtube.com/*"],
      "js": ["content.js"],
      "run_at": "document_idle"
    }
  ]
}
```

### `popup.html`
```html
<!doctype html>
<html lang="zh">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link rel="stylesheet" href="styles.css" />
  <title>提取结论</title>
</head>
<body>
  <div class="container">
    <h1>结论提取</h1>
    <div id="videoMeta" class="meta"></div>

    <label class="row">
      后端 API 根地址：
      <input id="apiBase" type="text" placeholder="http://localhost:8000" />
    </label>

    <label class="row">
      输出语言：
      <select id="lang">
        <option value="zh">中文</option>
        <option value="en">English</option>
      </select>
    </label>

    <button id="summarizeBtn">一键提取结论</button>

    <div id="status" class="status"></div>
    <ol id="conclusions" class="list"></ol>

    <details>
      <summary>查看详细总结</summary>
      <div id="summary"></div>
    </details>

    <details>
      <summary>查看转录片段（可选）</summary>
      <pre id="transcript" class="mono"></pre>
    </details>
  </div>
  <script src="popup.js"></script>
</body>
</html>
```

### `styles.css`
```css
body { font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif; margin: 0; }
.container { width: 360px; padding: 16px; }
h1 { font-size: 18px; margin: 0 0 8px; }
.meta { font-size: 12px; color: #666; margin-bottom: 8px; }
.row { display: flex; flex-direction: column; gap: 6px; margin: 8px 0; }
input, select { padding: 8px; border: 1px solid #ddd; border-radius: 8px; }
button { width: 100%; padding: 10px; border: 0; border-radius: 10px; background: #111; color: #fff; cursor: pointer; }
button:disabled { background: #aaa; cursor: not-allowed; }
.status { font-size: 12px; color: #333; margin: 10px 0; }
.list { margin-left: 18px; }
.mono { white-space: pre-wrap; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; background: #fafafa; border: 1px solid #eee; padding: 8px; border-radius: 8px; }
```

### `content.js`
```js
// 从 YouTube 页面提取 videoId、标题和频道名
(function() {
  const getVideoId = () => {
    const url = new URL(location.href);
    if (url.hostname.includes('youtube.com')) {
      return url.searchParams.get('v');
    }
    return null;
  };

  const getTitle = () => document.title.replace(/ - YouTube$/, '');

  const getChannel = () => {
    const el = document.querySelector('ytd-video-owner-renderer a.yt-simple-endpoint');
    return el ? el.textContent.trim() : '';
  };

  const sendMeta = () => {
    const meta = { videoId: getVideoId(), title: getTitle(), channel: getChannel(), url: location.href };
    chrome.runtime?.sendMessage({ type: 'YT_META', payload: meta });
  };

  // 初次 & URL 变化时发送
  sendMeta();
  let last = location.href;
  const mo = new MutationObserver(() => {
    if (location.href !== last) { last = location.href; sendMeta(); }
  });
  mo.observe(document, { childList: true, subtree: true });
})();
```

### `popup.js`
```js
const $ = (id) => document.getElementById(id);
let currentMeta = null;

// 恢复用户设置
chrome.storage.sync.get(['apiBase', 'lang'], (cfg) => {
  if (cfg.apiBase) $("apiBase").value = cfg.apiBase;
  if (cfg.lang) $("lang").value = cfg.lang;
});

// 监听 content script 发送的元信息
chrome.runtime.onMessage.addListener((msg) => {
  if (msg?.type === 'YT_META') {
    currentMeta = msg.payload;
    renderMeta();
  }
});

function renderMeta() {
  const el = $("videoMeta");
  if (!currentMeta || !currentMeta.videoId) {
    el.textContent = '未检测到视频ID，请在 YouTube 视频页打开插件。';
    $("summarizeBtn").disabled = true;
    return;
  }
  $("summarizeBtn").disabled = false;
  el.innerHTML = `视频：<strong>${escapeHtml(currentMeta.title || '')}</strong><br/>频道：${escapeHtml(currentMeta.channel || '')}<br/>ID：${currentMeta.videoId}`;
}

$("summarizeBtn").addEventListener('click', async () => {
  const apiBase = $("apiBase").value.trim() || 'http://localhost:8000';
  const lang = $("lang").value || 'zh';

  chrome.storage.sync.set({ apiBase, lang });

  if (!currentMeta?.videoId) {
    setStatus('未检测到视频ID');
    return;
  }

  setStatus('正在请求后端生成结论…（可能需要数十秒）');
  setConclusions([]); $("summary").textContent = ''; $("transcript").textContent = '';

  try {
    const res = await fetch(`${apiBase}/api/summarize?video_id=${encodeURIComponent(currentMeta.videoId)}&lang=${encodeURIComponent(lang)}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    setConclusions(data?.conclusions || []);
    $("summary").textContent = data?.summary || '';
    $("transcript").textContent = data?.transcript_preview || '';
    setStatus('完成');
  } catch (err) {
    console.error(err);
    setStatus('出错：' + err.message);
  }
});

function setStatus(t) { $("status").textContent = t; }
function setConclusions(items) {
  const el = $("conclusions");
  el.innerHTML = '';
  items.forEach(t => {
    const li = document.createElement('li');
    li.textContent = t;
    el.appendChild(li);
  });
}
function escapeHtml(str) { return str?.replace(/[&<>"']/g, s => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#39;'}[s])) || ''; }

// 获取当前活动 tab 的最新元信息（兼容 popup 打开时）
(async function init() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab?.id) return;
  chrome.tabs.sendMessage(tab.id, { type: 'PING' }, () => {});
})();
```

---

## 3) 后端（FastAPI + yt-dlp + OpenAI）

> 后端职责：根据 `video_id` 下载音频 → Whisper 转录（中文/英文自动识别）→ LLM 提炼“3–5 条结论”→ 返回 JSON。

### `requirements.txt`
```
fastapi==0.111.0
uvicorn[standard]==0.30.1
yt-dlp==2024.08.06
openai==1.37.1
python-dotenv==1.0.1
```

### `.env.example`
```
OPENAI_API_KEY=sk-xxxx
# Whisper 模型（默认 whisper-1）
WHISPER_MODEL=whisper-1
# 摘要模型（建议 gpt-4o-mini 成本低）
SUMMARY_MODEL=gpt-4o-mini
# 临时文件目录
TMP_DIR=./tmp
```

### `prompts.py`
```python
SYSTEM_SUMMARY = (
    "你是资深投研助手。请基于转录文本，提炼【3–5条】‘结论/要点’，偏向可执行或判断性的观点。"
    "要求：\n"
    "1) 用目标语言输出（默认中文）；\n"
    "2) 不复述无关细节，不展开长论述；\n"
    "3) 若视频仅提供中性信息，则给出概要判断；\n"
    "4) 不编造数据，不给具体买卖建议或目标价；\n"
    "5) 仅返回要点列表，必要时可附一行‘整体观点’。"
)

USER_TEMPLATE = (
    "目标语言: {lang}\n\n"
    "以下是转录文本（可能含中英文混合、口语化）：\n\n"
    "{transcript}\n\n"
    "请输出：\n- 3–5 条要点（列表，每条一行）。\n- 末尾可选‘整体观点：…’。"
)
```

### `app.py`
```python
import os
import io
import shutil
import tempfile
from pathlib import Path
from typing import List

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from yt_dlp import YoutubeDL

from openai import OpenAI
from prompts import SYSTEM_SUMMARY, USER_TEMPLATE

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "whisper-1")
SUMMARY_MODEL = os.getenv("SUMMARY_MODEL", "gpt-4o-mini")
TMP_DIR = Path(os.getenv("TMP_DIR", "./tmp"))
TMP_DIR.mkdir(parents=True, exist_ok=True)

client = OpenAI(api_key=OPENAI_API_KEY)

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
    url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(out_dir / f"%(id)s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "cachedir": False,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192"
        }]
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        audio_path = out_dir / f"{info['id']}.mp3"
        if not audio_path.exists():
            # 兜底查找
            for f in out_dir.glob(f"{info['id']}.*"):
                if f.suffix.lower() in {'.m4a', '.mp3', '.webm'}:
                    return f
            raise FileNotFoundError("音频文件未找到")
        return audio_path


def transcribe_whisper(file_path: Path) -> str:
    # 使用 Whisper API 转录
    with open(file_path, "rb") as f:
        transcription = client.audio.transcriptions.create(
            model=WHISPER_MODEL,
            file=f,
            temperature=0,
            response_format="json"
        )
    # SDK 返回对象含 text 字段
    return transcription.text


def summarize_conclusions(transcript: str, lang: str = "zh") -> List[str]:
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
    # 把可能的“整体观点”单独留在 summary 中
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

    work = Path(tempfile.mkdtemp(dir=TMP_DIR))
    audio_file = None
    try:
        audio_file = download_audio_by_video_id(video_id, work)
        transcript = transcribe_whisper(audio_file)
        conclusions, overall = summarize_conclusions(transcript, lang=lang)

        preview = transcript[:1200] + ("…" if len(transcript) > 1200 else "")
        return SummaryResp(
            video_id=video_id,
            conclusions=conclusions or ["未提取到明确结论，请查看详细总结或重试。"],
            summary=overall,
            transcript_preview=preview,
        )
    finally:
        # 清理临时目录
        try:
            shutil.rmtree(work, ignore_errors=True)
        except Exception:
            pass
```

---

## 4) 运行与配置

### 后端
1. 安装依赖
   ```bash
   cd server
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env && nano .env   # 填写 OPENAI_API_KEY
   ```
2. 启动服务
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000 --workers 1
   ```
3. 测试接口
   - 浏览器访问：`http://localhost:8000/api/summarize?video_id=VIDEO_ID&lang=zh`

> 提示：首次转录较慢（需下载音频 + 转录）。后续同一机器会快一些（系统层面缓存依赖）。

### 扩展
1. 打开 Chrome → `chrome://extensions/` → 打开**开发者模式** → **加载已解压的扩展程序** → 选择 `extension/` 目录。
2. 打开任意 YouTube 视频页面 → 点击扩展图标。
3. 在弹窗里把 **后端 API 根地址** 设置为 `http://localhost:8000`，选择语言后点击「一键提取结论」。

---

## 5) 可选：成本 / 性能优化开关

在 `app.py` 中可以加入以下可调参数与策略：
- **分段转录**：对于 25–30 分钟视频，先用 yt-dlp 下载为 `m4a`，再利用 `pydub` 切片为 2–3 分钟并行调用 Whisper（更快，但实现更复杂）。
- **关键词预筛**（来源2 专用）：先用 **便宜模型**（如 `gpt-4o-mini`）对粗转录做 1–2 行关键词判断，若匹配目标股票/行业，再做精细总结。
- **本地 Whisper**：将 `transcribe_whisper` 切换为 `whisper.cpp` 或 `faster-whisper` 本地推理，API 费用近似为 0。

---

## 6) 后续增强建议
- **实时进度**：后端拆分为“任务创建 → 轮询状态”，前端显示进度条（下载、转录、总结）。
- **多来源策略**：在前端根据频道 ID 区分来源 1–4，调用后端不同的 preset（例如来源4启用“深度总结”提示词）。
- **导出/归档**：支持导出结论为 Markdown 或追加到 Notion/Obsidian。
- **多语言统一输出**：无论原视频中英混合，前端设置语言后统一生成中文或英文结论。
- **批量模式**：给定频道或播放列表 URL，后端队列化处理，前端展示“今日概览”。

---

> 这是一个可直接跑起来的 **MVP**。你可以先本地启动后端，再加载扩展测试。如果需要，我可以在此基础上：
> - 加上**分段并行转录**版本；
> - 增加**频道识别 → 自动选择摘要力度**；
> - 或把后端打包成 Docker 一键启动。

