#!/usr/bin/env python3
"""
简单的设置测试脚本
检查后端依赖和基本功能
"""

import sys
import subprocess
import os

def test_python_version():
    """测试Python版本"""
    version = sys.version_info
    print(f"Python 版本: {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ 需要 Python 3.8 或更高版本")
        return False
    print("✅ Python 版本符合要求")
    return True

def test_pip_dependencies():
    """测试依赖安装"""
    try:
        import fastapi
        print(f"✅ FastAPI 已安装: {fastapi.__version__}")
    except ImportError:
        print("❌ FastAPI 未安装")
        return False
    
    try:
        import uvicorn
        print(f"✅ Uvicorn 已安装")
    except ImportError:
        print("❌ Uvicorn 未安装")
        return False
    
    try:
        import yt_dlp
        print(f"✅ yt-dlp 已安装")
    except ImportError:
        print("❌ yt-dlp 未安装")
        return False
    
    try:
        import openai
        print(f"✅ OpenAI 已安装: {openai.__version__}")
    except ImportError:
        print("❌ OpenAI 未安装")
        return False
    
    return True

def test_env_file():
    """测试环境文件"""
    env_path = "server/.env"
    if os.path.exists(env_path):
        print("✅ .env 文件存在")
        with open(env_path, 'r') as f:
            content = f.read()
            if "your_openai_api_key_here" in content:
                print("⚠️  请在 server/.env 文件中设置您的 OpenAI API 密钥")
                return False
            elif "OPENAI_API_KEY=" in content:
                print("✅ OpenAI API 密钥已配置")
                return True
    else:
        print("❌ .env 文件不存在")
        return False

def main():
    print("🔍 开始测试项目设置...")
    print("=" * 50)
    
    all_good = True
    
    # 测试 Python 版本
    if not test_python_version():
        all_good = False
    
    print()
    
    # 测试依赖
    print("📦 检查依赖安装状态:")
    if not test_pip_dependencies():
        print("💡 运行以下命令安装依赖:")
        print("   cd server")
        print("   pip install -r requirements.txt")
        all_good = False
    
    print()
    
    # 测试环境文件
    print("⚙️  检查环境配置:")
    if not test_env_file():
        all_good = False
    
    print()
    print("=" * 50)
    
    if all_good:
        print("🎉 所有检查都通过了！可以开始启动服务器了。")
        print("启动命令: cd server && uvicorn app:app --host 0.0.0.0 --port 8000")
    else:
        print("❌ 还有一些问题需要解决，请查看上面的提示。")
    
    return all_good

if __name__ == "__main__":
    main()