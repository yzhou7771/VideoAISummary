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