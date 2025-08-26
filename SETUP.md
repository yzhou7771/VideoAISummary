# YouTube 股票视频结论提取插件 - 设置指南

## 📋 项目概述

这是一个Chrome扩展项目，可以一键从YouTube股票分析视频中提取3-5条核心结论。

## 🏗️ 项目结构

```
YoutubeSummary/
├── extension/              # Chrome 扩展前端
│   ├── manifest.json      # 扩展配置
│   ├── popup.html         # 弹出窗口界面
│   ├── popup.js           # 前端逻辑
│   ├── content.js         # 内容脚本
│   ├── styles.css         # 样式文件
│   └── icons/             # 图标资源
├── server/                # FastAPI 后端
│   ├── app.py            # 主应用
│   ├── prompts.py        # AI提示词模板
│   ├── requirements.txt  # Python依赖
│   ├── .env.example      # 环境变量模板
│   └── .env             # 环境变量配置
├── CLAUDE.md            # Claude Code 工作指南
├── SETUP.md             # 本设置指南
└── test_setup.py        # 设置测试脚本
```

## ⚙️ 安装步骤

### 1. 后端设置

1. **安装Python依赖**
   ```bash
   cd server
   pip install -r requirements.txt
   ```

2. **配置环境变量**
   - 编辑 `server/.env` 文件
   - 添加您的 OpenAI API 密钥：
     ```
     OPENAI_API_KEY=sk-your-actual-api-key-here
     ```

3. **启动后端服务**
   ```bash
   cd server
   uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   ```

### 2. Chrome 扩展安装

1. **打开Chrome扩展管理页面**
   - 在地址栏输入：`chrome://extensions/`

2. **启用开发者模式**
   - 点击右上角的"开发者模式"开关

3. **加载扩展**
   - 点击"加载已解压的扩展程序"
   - 选择项目中的 `extension/` 文件夹

4. **添加扩展图标**
   - 在 `extension/icons/` 目录下放置一个128x128的PNG图标
   - 命名为 `icon128.png`

## 🧪 测试

### 后端测试
```bash
# 运行设置测试脚本
python test_setup.py

# 手动测试API（需要替换VIDEO_ID）
curl "http://localhost:8000/api/summarize?video_id=VIDEO_ID&lang=zh"
```

### 扩展测试
1. 打开任意YouTube视频页面
2. 点击Chrome工具栏中的扩展图标
3. 设置后端API地址为：`http://localhost:8000`
4. 点击"一键提取结论"按钮

## 📝 使用说明

1. **访问YouTube视频页面**
2. **点击扩展图标**
3. **配置设置**：
   - 后端API地址（默认：http://localhost:8000）
   - 输出语言（中文/英文）
4. **点击"一键提取结论"**
5. **等待处理**（通常需要30-60秒）
6. **查看结果**：
   - 3-5条核心结论
   - 详细总结（可选展开）
   - 转录片段预览（可选展开）

## ⚠️ 注意事项

1. **OpenAI API费用**：使用Whisper和GPT会产生费用
2. **网络要求**：需要稳定的网络连接下载音频
3. **视频长度**：建议10-30分钟的视频，过长可能影响处理速度
4. **语言支持**：主要针对中文内容优化，支持中英混合
5. **Chrome版本**：需要支持Manifest V3的Chrome版本

## 🔧 故障排除

### 后端问题
- **依赖未安装**：运行 `pip install -r requirements.txt`
- **API密钥错误**：检查 `.env` 文件中的OpenAI密钥
- **端口被占用**：更换其他端口或关闭占用进程

### 扩展问题
- **无法检测视频**：刷新YouTube页面后重试
- **网络错误**：检查后端服务是否正常运行
- **权限问题**：确认扩展已获得必要权限

## 🚀 开发建议

- 使用 `--reload` 参数启动后端以支持热更新
- 在扩展管理页面点击"重新加载"来更新扩展
- 查看浏览器开发者工具调试前端问题
- 查看终端输出调试后端问题

## 📞 支持

如遇问题，请检查：
1. Python和依赖版本
2. OpenAI API密钥配置
3. 网络连接状态
4. Chrome扩展权限设置

---

## 🤖 macOS 自动化启动 (推荐)

为了提升使用体验，可以设置服务器自动启动，无需每次手动启动。

### ⭐ 推荐：launchd 自动化

```bash
# 一键安装自动化服务
cd /Users/amber/Workspace/Projects/YoutubeSummary
./install_automation.sh
```

**效果**：
- 🕘 工作日（周二-周六）上午9点自动启动服务器
- 🌆 工作日（周二-周六）下午4点自动停止服务器
- 🔔 桌面通知提醒启动/停止状态  
- 📝 详细日志记录
- 🛡️ 重复启动保护

### 📱 日常管理命令

```bash
# 手动启动
./start_server.sh

# 手动停止  
./stop_server.sh

# 查看运行状态
ps aux | grep "server/app.py"

# 查看日志
tail -f ~/Library/Logs/youtube_summarizer.log

# 卸载自动化
./uninstall_automation.sh
```

### 🎯 最终使用体验

**安装后的工作日流程**：
```
工作日9AM → 自动启动通知 → 使用扩展 → 4PM自动停止
```

**不需要手动操作**：
- ✅ 服务器自动启动
- ✅ 桌面通知确认  
- ✅ 错误自动重试
- ✅ 日志自动记录

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

这样设置后，你就可以每天无缝使用AI视频总结功能了！🎬✨