# YouTube Stock Video Conclusion Extraction Plugin - Setup Guide

## 📋 Project Overview

This is a Chrome extension that extracts 3-5 key conclusions from YouTube stock analysis videos with one click.

## 🏗️ Project Structure

```
YoutubeSummary/
├── extension/ # Chrome extension frontend
│ ├── manifest.json # Extension configuration
│ ├── popup.html # Popup UI
│ ├── popup.js # Frontend logic
│ ├── content.js # Content script
│ ├── styles.css # Stylesheet
│ └── icons/ # Icon assets
├── server/ # FastAPI backend
│ ├── app.py # Main application
│ ├── prompts.py # AI prompt template
│ ├── requirements.txt # Python dependencies
│ ├── .env.example # Environment variable template
│ └── .env # Environment variable configuration
├── CLAUDE.md # Claude Code workbook
├── SETUP.md # This setup guide
└── test_setup.py # Set up the test script
```

## ⚙️ Installation Steps

### 1. Backend Setup

1. **Install Python dependencies**
```bash
cd server
pip install -r requirements.txt
```

2. **Configure environment variables**
- Edit the `server/.env` file
- Add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

3. **Start the backend server**
```bash
cd server
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Chrome extension installation

1. **Open the Chrome extension management page**
- Enter `chrome://extensions/` in the address bar

2. **Enable developer mode**
- Click the "Developer Mode" switch in the top right corner.

3. **Load the extension**
- Click "Load unzipped extension"
- Select the `extension/` folder in your project.

4. **Add an extension icon**
- Place a 128x128 PNG icon in the `extension/icons/` directory.
- Name it `icon128.png`

## 🧪 Testing

### Backend Testing
```bash
# Run the setup test script
python test_setup.py

# Manually test the API (requires replacing VIDEO_ID)
curl "http://localhost:8000/api/summarize?video_id=VIDEO_ID&lang=zh"
```

### Extension Testing
1. Open any YouTube video page
2. Click the extension icon in the Chrome toolbar
3. Set the backend API address to: `http://localhost:8000`
4. Click the "One-click Extract Results" button

## 📝 Instructions

1. **Visit the YouTube video page**
2. **Click the extension icon**
3. **Configure settings**:
- Backend API address (default: http://localhost:8000)
- Output language (Chinese/English)
4. **Click "One-click extraction of conclusions"**
5. **Wait for processing** (usually takes 30-60 seconds)
6. **View results**:
- 3-5 core conclusions
- Detailed summary (optional expansion)
- Transcript preview (optional expansion)

## ⚠️ Notes

1. **OpenAI API fees**: Using Whisper and GPT will incur fees.
2. **Network requirements**: A stable internet connection is required to download audio.
3. **Video length**: 10-30 minutes is recommended; longer videos may slow down processing.
4. **Language support**: Optimized for Chinese content, supports a mix of Chinese and English.
5. **Chrome version**: A Chrome version that supports Manifest V3 is required.

## 🔧 Troubleshooting

### Backend Issues
- **Dependencies Not Installed**: Run `pip install -r requirements.txt`
- **API Key Error**: Check the OpenAI key in the `.env` file
- **Port In Use**: Change the port or kill the occupying process

### Extension Issues
- **Unable to Detect Video**: Refresh the YouTube page and try again
- **Network Error**: Check that the backend service is running properly
- **Permission Issue**: Confirm that the extension has the necessary permissions

## 🚀 Development Suggestions

- Use the `--reload` flag to enable hot updates for the backend
- Click "Reload" on the extension management page to update the extension
- Check the browser developer tools to debug frontend issues
- Check the terminal output to debug backend issues

### 🌅 每日使用流程

#### ⚡ 快速启动流程 (自动化后)

1. **工作日上午9点** - 自动收到桌面通知：服务器已启动
2. **打开YouTube** - 访问任何YouTube视频
3. **点击扩展图标** - 浏览器右上角的紫色总结图标
4. **点击"Summarize Video"** - 自动开始处理
5. **等待结果** - 1-3分钟后获得AI总结

#### ⏱️ 预期处理时间
- **短视频** (5分钟内): ~30-60秒
- **中等视频** (10-20分钟): ~2-3分钟
- **长视频** (30分钟+): ~3-5分钟

#### 💡 最佳实践

**🌟 推荐工作流程**
```
工作日9AM → 服务器自动启动 → 使用至4PM → 服务器自动停止
```

**📊 适合的视频类型**
- ✅ **教育视频** - 讲座、教程、分析
- ✅ **新闻解读** - 财经分析、时事讨论  
- ✅ **技术分享** - 编程、技术讲解
- ✅ **商业内容** - 创业、投资、营销

**⚠️ 注意事项**
- 视频需要有清晰的语音内容
- 音乐视频可能总结效果不佳
- 非常短的视频（<1分钟）可能内容不足