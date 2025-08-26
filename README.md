# YouTube Stock Video Conclusion Extraction Plugin - Setup Guide

## 📋 Project Overview

This is a Chrome extension that extracts 3-5 key conclusions from YouTube stock analysis videos with one click.


## ⚠️ Notes

1. **OpenAI API fees**: Using Whisper and GPT will incur fees.
2. **Network requirements**: A stable internet connection is required to download audio.
3. **Video length**: 10-30 minutes is recommended; longer videos may slow down processing.
4. **Language support**: Optimized for Chinese content, supports a mix of Chinese and English.
5. **Chrome version**: A Chrome version that supports Manifest V3 is required.



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


```
🧪 测试相关文件

  | 文件名                     | 用途        | 说明                      |
  |-------------------------|-----------|-------------------------|
  | test_setup.py           | 环境测试      | 测试Python依赖和OpenAI API连接 |
  | test_cookies.sh         | Cookies测试 | 测试YouTube cookies有效性    |
  | test_complete_system.sh | 系统集成测试    | 完整的端到端系统测试              |
  | test_phase3_ux.sh       | UX功能测试    | Phase 3用户体验功能测试         |
  | simple_server.py        | 简单测试服务器   | 用于基础功能测试的简化服务器          |
  | run_demo_server.py      | 演示服务器     | 用于演示的服务器启动脚本            |
  | run_full_server.py      | 完整测试服务器   | 完整功能的测试服务器              |
  | run_server.py           | 通用测试启动器   | 通用的服务器测试启动脚本            |

  🚫 与Extension无关的文件

  📄 文档类文件 (开发/说明用途)

  | 文件名                                           | 类型     | 用途              |
  |-----------------------------------------------|--------|-----------------|
  | README.md                                     | 项目说明   | 项目基础介绍          |
  | CLAUDE.md                                     | 开发指南   | Claude Code开发说明 |
  | SETUP.md                                      | 安装指南   | 完整的安装和配置说明      |
  | CHROME_EXTENSION_GUIDE.md                     | 安装指南   | 扩展安装专门说明        |
  | COOKIES_SETUP.md                              | 配置指南   | Cookies配置说明     |
  | EXTENSION_DEBUG.md                            | 调试指南   | 扩展调试帮助文档        |
  | PROJECT_STATUS.md                             | 项目状态   | 项目完成状态和功能说明     |
  | solution.md                                   | 解决方案文档 | 技术解决方案说明        |
  | you_tube_股票视频结论提取插件(chrome_扩展)_mvp_代码与部署指南.md | 早期文档   | 早期的MVP指南文档      |

  🤖 自动化脚本 (服务器管理用途)

  | 文件名                               | 用途        | 说明              |
  |-----------------------------------|-----------|-----------------|
  | install_automation.sh             | 自动化安装     | 安装定时任务服务        |
  | uninstall_automation.sh           | 自动化卸载     | 卸载定时任务服务        |
  | start_server.sh                   | 服务器启动     | 自动启动后端服务器       |
  | stop_server.sh                    | 服务器停止     | 自动停止后端服务器       |
  | startup_helper.sh                 | 启动辅助      | 系统启动时的辅助脚本      |
  | alfred_workflow.sh                | Alfred集成  | Alfred工作流脚本     |
  | com.youtube.summarizer.plist      | LaunchD配置 | macOS定时任务配置(启动) |
  | com.youtube.summarizer.stop.plist | LaunchD配置 | macOS定时任务配置(停止) |

  🛠️ 工具脚本

  | 文件名            | 用途   | 说明              |
  |----------------|------|-----------------|
  | create_icon.py | 图标生成 | 生成扩展图标的Python脚本 |

  🗂️ 缓存和临时文件

  | 路径                  | 用途      | 说明            |
  |---------------------|---------|---------------|
  | server/cache/*.json | 转录缓存    | 存储视频转录结果的缓存文件 |
  | server/tmp/         | 临时文件夹   | 音频处理临时文件存储    |
  | tmp/                | 项目临时文件夹 | 项目级别的临时文件     |
  | cache/              | 项目缓存文件夹 | 项目级别的缓存文件     |

  ⚙️ 配置文件

  | 文件名                            | 用途        | 说明                  |
  |--------------------------------|-----------|---------------------|
  | server/cookies.txt             | YouTube认证 | YouTube访问的cookies文件 |
  | extension/manifest_simple.json | 备用配置      | 简化版的扩展清单文件          |

  ✅ 核心Extension相关文件 (必需保留)

  | 文件名                         | 用途       | 重要性     |
  |-----------------------------|----------|---------|
  | extension/manifest.json     | 扩展配置     | 🔴 核心必需 |
  | extension/popup.html        | 扩展界面     | 🔴 核心必需 |
  | extension/popup.js          | 前端逻辑     | 🔴 核心必需 |
  | extension/content.js        | 内容脚本     | 🔴 核心必需 |
  | extension/styles.css        | 界面样式     | 🔴 核心必需 |
  | extension/icons/icon128.png | 扩展图标     | 🔴 核心必需 |
  | server/app.py               | 后端API    | 🔴 核心必需 |
  | server/prompts.py           | AI提示词    | 🔴 核心必需 |
  | server/requirements.txt     | Python依赖 | 🔴 核心必需 |

  📊 文件统计摘要

  - 🧪 测试文件: 8个
  - 📄 文档文件: 9个
  - 🤖 自动化脚本: 8个
  - 🛠️ 工具/配置: 4个
  - 🗂️ 缓存/临时: 7个文件/文件夹
  - ✅ 核心扩展文件: 9个

  💡 清理建议

  如果要精简项目，可以考虑移除或归档：
  1. 测试文件 - 可移至 tests/ 目录
  2. 文档文件 - 可移至 docs/ 目录
  3. 自动化脚本 - 可移至 automation/ 目录
  4. 缓存文件 - 可安全删除（会自动重新生成）
```