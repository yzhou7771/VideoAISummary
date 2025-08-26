# YouTube Cookies设置指南

## 快速测试步骤

### 方法1: Chrome浏览器扩展（推荐）

1. **安装扩展**
   - 打开Chrome浏览器
   - 访问: https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc
   - 点击"Add to Chrome"安装"Get cookies.txt LOCALLY"扩展

2. **登录YouTube**
   - 访问 https://www.youtube.com
   - 确保已登录你的Google/YouTube账户

3. **导出Cookies**
   - 在YouTube页面上，点击Chrome工具栏中的扩展图标
   - 选择"Get cookies.txt LOCALLY"
   - 点击扩展图标，选择"Export"
   - 保存文件为 `cookies.txt`

4. **放置文件**
   - 将下载的 `cookies.txt` 文件移动到：
   ```
   /Users/amber/Workspace/Projects/YoutubeSummary/server/cookies.txt
   ```

5. **重启服务器测试**

### 方法2: 手动导出（Firefox等其他浏览器）

如果使用Firefox或其他浏览器：

1. 安装类似的cookies导出扩展
2. 或使用浏览器开发者工具手动导出cookies
3. 格式应该是Netscape cookies.txt格式

## 验证Cookies有效性

导入cookies后，你可以通过以下方式验证：

1. **检查服务器状态**:
   ```bash
   curl -s http://localhost:8000/ | jq .cookies_available
   ```
   应该返回 `true`

2. **测试真实视频下载**:
   使用一个真实的YouTube视频ID进行测试

## 注意事项

- Cookies文件包含敏感的认证信息，请妥善保管
- Cookies通常有效期为几周到几个月
- 如果YouTube更改密码，需要重新导出cookies
- 建议定期更新cookies文件（每月一次）