#!/usr/bin/env python3
"""
简化的服务器启动脚本
"""

import os
import sys
import uvicorn

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入应用
from server.app import app

if __name__ == "__main__":
    print("🚀 启动 YouTube 总结服务...")
    print("📡 服务将运行在: http://localhost:8000")
    print("📖 API 文档: http://localhost:8000/docs")
    print("⏹️  按 Ctrl+C 停止服务")
    print("-" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )