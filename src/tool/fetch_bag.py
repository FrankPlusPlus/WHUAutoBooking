"""fetch_bag.py
改进版：在本脚本中启动 mitmproxy 代理（DumpMaster），并运行 zhlj 自动化流程以捕获请求/响应。
修复点：
 - 在 mitmproxy 线程中创建并设置 asyncio 事件循环，避免 "no running event loop" 错误
 - 在修改 winhttp 代理前检测管理员权限，避免拒绝访问
 - 使用 capture_output/text/encoding 避免 netsh 输出的编码错误
 - 提供全局引用以便在主线程中优雅关闭 DumpMaster
"""

import threading
import time
import os
import json
import base64
import asyncio
import ctypes
import subprocess
from typing import Optional, Dict, Any
import shutil

# 导入你的自动化函数（确保 PYTHONPATH 包含项目根或使用相对导入）
from zhlj_automation import start_zhlj_automation

PROXY_PORT = 8080
ADDON_SCRIPT = os.path.join(os.path.dirname(__file__), 'fetch_addon.py')
CAPTURE_OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'captures'))

def start_mitmdump(addon_script: str, port: int = PROXY_PORT):
    """以子进程方式启动 mitmdump 并加载指定的 addon 脚本。
    返回 subprocess.Popen 对象。
    要求系统环境中已安装 mitmdump（mitmproxy 套件的一部分）。
    """
    mitmdump_exe = shutil.which('mitmdump') or shutil.which('mitmdump.exe')
    if not mitmdump_exe:
        raise FileNotFoundError('mitmdump not found in PATH. Please install mitmproxy and ensure mitmdump is available.')
    cmd = [mitmdump_exe, '-p', str(port), '-s', addon_script]
    # 使用 text/encoding 避免子线程解码错误；不阻塞 stdout/stderr
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='ignore')
    return proc

def stop_mitmdump(proc: subprocess.Popen, timeout: float = 5.0):
    if proc is None:
        return
    try:
        proc.terminate()
    except Exception:
        pass
    try:
        proc.wait(timeout=timeout)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass


# 旧的 run_mitmproxy 已移除。脚本现在通过 start_mitmdump() 在子进程中运行 mitmdump 并加载
# 单独的 addon 脚本（fetch_addon.py）。这规避了在当前进程中直接创建 DumpMaster 导致的
# asyncio 事件循环兼容问题。


def set_winhttp_proxy(proxy: Optional[str]) -> Optional[str]:
    """
    设置或清除 winhttp 代理。
    返回之前的代理配置信息字符串（用于恢复），如果无法读取返回 None。
    注意：需要管理员权限修改系统代理（部分命令需要）。
    """
    # 读取当前配置（以文本方式，忽略编码错误以避免 UnicodeDecodeError）
    prev = None
    try:
        res = subprocess.run(["netsh", "winhttp", "show", "proxy"], capture_output=True, text=True, encoding="utf-8", errors="ignore")
        prev = res.stdout.strip()
    except Exception:
        prev = None

    # 如果没有管理员权限，尝试设置会失败；先检测权限并在无权限时跳过设置
    is_admin = False
    try:
        is_admin = bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        is_admin = False

    if not is_admin:
        # 返回之前配置并告知调用方，避免抛出异常
        print("警告：当前进程没有管理员权限，无法修改 WinHTTP 代理。请以管理员身份运行脚本或手动设置系统代理。")
        return prev

    try:
        if proxy:
            subprocess.run(["netsh", "winhttp", "set", "proxy", proxy], check=True, capture_output=True, text=True, encoding="utf-8", errors="ignore")
        else:
            subprocess.run(["netsh", "winhttp", "reset", "proxy"], check=True, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    except subprocess.CalledProcessError as e:
        # 捕获并打印错误信息，但不抛出
        print(f"写入代理服务器设置时出错: {e}; 输出: {e.stdout}\n{e.stderr}")

    return prev


def main():
    # 提示：脚本不再自动设置系统代理（因为在某些环境需要管理员权限）。
    print("[*] 请确保目标应用或系统已把代理设置为 127.0.0.1:%d（mitmdump 将在该端口监听）" % PROXY_PORT)
    print("[*] 如果你希望脚本自动设置 WinHTTP 代理，请以管理员身份运行并启用该选项（当前脚本默认不修改系统代理）。")

    # 启动 mitmdump（外部进程）并加载 addon 脚本
    print(f"[*] 启动 mitmdump，加载 addon: {ADDON_SCRIPT}")
    try:
        proc = start_mitmdump(ADDON_SCRIPT, PROXY_PORT)
    except FileNotFoundError as e:
        print(e)
        print("请先安装 mitmproxy 并确保 mitmdump 在 PATH 中，或手动启动 mitmdump 并加载 fetch_addon.py。")
        return

    # 给 mitmdump 一点时间来启动
    time.sleep(1.0)

    try:
        print("[*] 运行 start_zhlj_automation() 开始自动化流程 ...")
        start_zhlj_automation()
        print("[*] 等待 5 秒以便收集剩余流量 ...")
        time.sleep(5)
    finally:
        print("[*] 停止 mitmdump 进程 ...")
        stop_mitmdump(proc)

    # 读取并展示捕获结果目录
    dx_jsonl = os.path.join(CAPTURE_OUT, 'dx_results.jsonl')
    images_dir = os.path.join(CAPTURE_OUT, 'images')

    print("\n---- dxvip results ----")
    if os.path.exists(dx_jsonl):
        with open(dx_jsonl, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    item = json.loads(line)
                    print(json.dumps(item, ensure_ascii=False, indent=2))
                except Exception:
                    pass
    else:
        print("(no dx results captured)")

    print("\n---- saved images ----")
    if os.path.isdir(images_dir):
        for fname in sorted(os.listdir(images_dir)):
            print(os.path.join(images_dir, fname))
    else:
        print("(no images captured)")


if __name__ == "__main__":
    main()