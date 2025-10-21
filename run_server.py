#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统信息监控后端服务启动脚本
"""

import subprocess
import sys
import os

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 7):
        print("❌ 需要Python 3.7或更高版本")
        sys.exit(1)

def install_dependencies():
    """安装依赖包"""
    print("📦 安装依赖包...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 依赖包安装完成")
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖包安装失败: {e}")
        sys.exit(1)

def check_dependencies():
    """检查依赖包是否已安装"""
    return True#暂时跳过
    required_packages = ['flask', 'psutil', 'flask_cors']
    missing_packages = []

    for package in required_packages:
        try:
            __import__(package.replace('_', '-').split('==')[0])
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print(f"⚠️ 缺少依赖包: {', '.join(missing_packages)}")
        install = input("是否自动安装依赖包? (y/N): ").lower().strip()
        if install == 'y':
            install_dependencies()
        else:
            print("请手动安装依赖包: pip install -r requirements.txt")
            sys.exit(1)

def main():
    """主函数"""
    print("🚀 系统信息监控后端服务启动器")
    print("=" * 50)

    # 检查Python版本
    check_python_version()

    # 检查依赖包
    check_dependencies()

    # 启动服务
    print("🔧 启动后端服务...")
    try:
        os.execv(sys.executable, [sys.executable, 'app.py'])
    except Exception as e:
        print(f"❌ 启动服务失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
