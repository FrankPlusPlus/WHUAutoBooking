import threading
import time
import subprocess
import signal
import os
from zhlj_automation import start_zhlj_automation  # 导入你的自动化函数

class TrafficCaptureManager:
    def __init__(self):
        self.mitm_process = None
        self.capture_script = "capture_traffic.py"
        
    def start_mitmproxy(self):
        """启动mitmproxy"""
        try:
            # 使用mitmdump启动代理
            self.mitm_process = subprocess.Popen(
                ["mitmdump", "-s", self.capture_script, "-p", "8080"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            time.sleep(3)  # 等待代理启动
            print("mitmproxy代理已启动在端口8080")
        except Exception as e:
            print(f"启动mitmproxy失败: {e}")
            
    def stop_mitmproxy(self):
        """停止mitmproxy"""
        if self.mitm_process:
            self.mitm_process.terminate()
            self.mitm_process.wait()
            print("mitmproxy代理已停止")
    
    def run_automation_with_capture(self):
        """运行自动化函数并捕获流量"""
        try:
            # 启动代理
            self.start_mitmproxy()
            
            # 在这里运行你的自动化函数
            print("开始执行自动化函数...")
            start_zhlj_automation()  # 调用你的函数
            print("自动化函数执行完成")
            
        finally:
            # 停止代理
            self.stop_mitmproxy()

# 使用示例
if __name__ == "__main__":
    manager = TrafficCaptureManager()
    manager.run_automation_with_capture()