import app
import threading
import webview
import signal
import sys
import os

def signal_handler(sig, frame):
    """处理信号以优雅退出"""
    print('\n正在关闭应用程序...')
    os._exit(0)

if __name__ == '__main__':
    # 设置信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # 启动Flask应用程序的线程
        flask_thread = threading.Thread(target=app.app.run, kwargs={'host':'0.0.0.0', 'port':5000, 'debug':False})
        flask_thread.daemon = True
        flask_thread.start()

        # 创建并显示WebView窗口
        webview.create_window('系统信息查看器', 'http://localhost:5000')
        webview.start(icon='web/favicon.ico')
    except KeyboardInterrupt:
        print('\n接收到中断信号，正在退出...')
        os._exit(0)
    except Exception as e:
        print(f'应用程序错误: {e}')
        os._exit(1)
