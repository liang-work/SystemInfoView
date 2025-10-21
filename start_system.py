#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统信息监控系统启动器
一键启动前端和后端服务
"""

import os
import sys
import time
import threading
import webbrowser
import subprocess
from pathlib import Path

def check_requirements():
    """检查依赖包"""
    try:
        import flask
        import psutil
        import flask_cors
        print("✅ 所有依赖包已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖包: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def start_backend():
    """启动后端服务"""
    print("🚀 启动后端服务...")
    try:
        # 使用subprocess启动后端服务
        backend_process = subprocess.Popen([
            sys.executable, 'app.py'
        ], cwd=os.getcwd())

        print("✅ 后端服务启动成功")
        return backend_process
    except Exception as e:
        print(f"❌ 后端服务启动失败: {e}")
        return None

def open_frontend():
    """打开前端界面"""
    print("🌐 打开前端界面...")
    try:
        frontend_path = Path(os.getcwd()) / 'index.html'
        webbrowser.open(f'file://{frontend_path}')
        print("✅ 前端界面已打开")
    except Exception as e:
        print(f"❌ 无法打开前端界面: {e}")

def main():
    """主函数"""
    print("🖥️ 系统信息监控系统启动器")
    print("=" * 50)

    # 检查依赖包
    if not check_requirements():
        return

    # 等待用户确认
    print("\n📋 系统将执行以下操作:")
    print("   1. 启动后端API服务 (端口: 3000)")
    print("   2. 打开前端监控界面")
    print("   3. 自动刷新系统信息")

    confirm = input("\n是否继续? (y/N): ").lower().strip()
    if confirm != 'y':
        print("❌ 操作已取消")
        return

    # 启动后端服务
    backend_process = start_backend()
    if not backend_process:
        return

    # 等待后端服务启动
    print("⏳ 等待后端服务启动...")
    time.sleep(3)

    # 测试后端服务
    try:
        import requests
        response = requests.get('http://localhost:3000/health', timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务连接正常")
        else:
            print("⚠️ 后端服务响应异常")
    except:
        print("⚠️ 无法连接到后端服务，请手动检查")

    # 打开前端界面
    open_frontend()

    print("\n🎉 系统启动完成!")
    print("=" * 50)
    print("📊 监控地址:")
    print("   前端界面: 直接打开 index.html")
    print("   后端API: http://localhost:3000")
    print("   健康检查: http://localhost:3000/health")
    print("\n💡 提示:")
    print("   - 前端会自动连接后端获取数据")
    print("   - 数据每5秒自动刷新")
    print("   - 按 Ctrl+C 停止后端服务")
    print("\n🔗 API接口:")
    print("   GET /api/system/info - 系统信息")
    print("   GET /api/performance/resources - 性能数据")

    try:
        # 保持程序运行
        backend_process.wait()
    except KeyboardInterrupt:
        print("\n\n🛑 正在停止服务...")
        backend_process.terminate()
        backend_process.wait()
        print("✅ 服务已停止")

if __name__ == "__main__":
    main()
