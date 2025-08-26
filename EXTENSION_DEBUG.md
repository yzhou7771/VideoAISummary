# 🔧 Chrome扩展调试指南

## 问题症状
扩展显示：`❌ 未检测到视频ID - 请刷新YouTube页面重试`

## 🔍 调试步骤

### 1. 检查扩展是否正确加载
1. 打开 `chrome://extensions/`
2. 确认 "Video Summarizer" 扩展已启用
3. 如果显示错误，点击"重新加载"按钮

### 2. 检查Content Script是否运行
1. 在YouTube视频页面上，按 `F12` 打开开发者工具
2. 切换到 `Console` 标签页
3. 查看是否有以下日志：
   ```
   [YT Extension] Content script loaded
   [YT Extension] Current URL: https://www.youtube.com/watch?v=...
   [YT Extension] Extracted video ID: [VIDEO_ID]
   ```

### 3. 手动触发视频信息提取
在YouTube页面的Console中执行：
```javascript
// 检查content script是否加载
console.log('Content script loaded:', typeof getVideoId !== 'undefined');

// 手动提取视频ID
const url = new URL(location.href);
console.log('Video ID:', url.searchParams.get('v'));

// 检查页面元素
console.log('Title element:', document.querySelector('#title h1.ytd-watch-metadata yt-formatted-string'));
```

### 4. 检查消息传递
1. 打开扩展的popup
2. 在Console中查看是否有错误消息
3. 检查消息发送和接收：
   ```
   [YT Extension Popup] Received message: {type: 'YT_META', payload: {...}}
   ```

## 🛠️ 常见问题解决

### 问题1: Content Script未加载
**症状**: Console中没有 `[YT Extension]` 日志  
**解决**: 
- 重新加载扩展
- 检查manifest.json权限
- 确认在正确的YouTube页面 (www.youtube.com/watch)

### 问题2: 视频ID为空
**症状**: 日志显示 `Extracted video ID: null`  
**解决**:
- 确认URL包含 `?v=` 参数
- 检查是否在正确的视频播放页面
- 尝试刷新页面

### 问题3: 消息传递失败
**症状**: Popup显示未检测到视频ID，但Content Script正常
**解决**:
- 检查Chrome扩展权限
- 重新加载扩展
- 确认popup和content script版本匹配

## 🔧 手动测试命令

### 在YouTube页面Console执行：
```javascript
// 测试视频ID提取
const testVideoId = () => {
    const url = new URL(location.href);
    const videoId = url.searchParams.get('v');
    console.log('Current URL:', location.href);
    console.log('Video ID:', videoId);
    return videoId;
};

// 测试标题提取
const testTitle = () => {
    const selectors = [
        '#title h1.ytd-watch-metadata yt-formatted-string',
        'h1.title.style-scope.ytd-video-primary-info-renderer',
        '#container h1'
    ];
    
    for (const selector of selectors) {
        const el = document.querySelector(selector);
        if (el) {
            console.log('Found title with selector:', selector);
            console.log('Title:', el.textContent.trim());
            return el.textContent.trim();
        }
    }
    console.log('No title element found');
    return null;
};

// 运行测试
testVideoId();
testTitle();
```

## 📋 重新加载扩展步骤

1. **完全重新加载扩展**:
   - 打开 `chrome://extensions/`
   - 找到 "Video Summarizer"
   - 点击 "🔄 重新加载" 按钮

2. **重新加载YouTube页面**:
   - 按 `F5` 或 `Ctrl+R` 刷新页面
   - 等待页面完全加载
   - 尝试点击扩展图标

3. **检查权限**:
   - 确认扩展有访问 `*.youtube.com` 的权限
   - 检查是否被浏览器安全设置阻止

## ⚠️ 注意事项

1. **YouTube页面类型**: 扩展只在视频播放页面工作 (`/watch?v=`)
2. **页面加载**: YouTube是单页应用，需要等待内容完全加载
3. **浏览器版本**: 确保使用支持Manifest V3的Chrome版本
4. **网络连接**: 确保能访问后端服务 (localhost:8000)

## 🆘 如果问题仍然存在

1. **重启浏览器**: 完全关闭Chrome并重新打开
2. **清除数据**: 清除YouTube的浏览器缓存和Cookie
3. **检查后端**: 确认后端服务运行在 localhost:8000
4. **尝试其他视频**: 测试不同的YouTube视频
5. **查看完整日志**: 在Console中查看所有错误和警告信息