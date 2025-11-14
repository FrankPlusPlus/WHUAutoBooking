"""
Coordinator: receive events from mitm_filter.py and drive a clicker worker.

Usage: python coordinator.py

What it does:
- starts a small HTTP server on 127.0.0.1:5000 to receive POST /events (JSON)
- events are queued and a worker thread processes them: calls compute_coordinate(event)
  (you can provide compute_coordinate in a separate module named coord_calc.py),
  then triggers a click via pyautogui (if available) or prints the coords.
- launches mitmdump as a subprocess (so mitmproxy runs and its addon posts events)

Note: this is a minimal example for local development. Use local-only binding and
careful security controls if running on a network.
"""

import http.server
import socketserver
import threading
import json
import queue
import time
import subprocess
import os
import sys
import base64

from time import sleep

# --- 动态修正 sys.path 使得以 `python src/scripts/coordinator.py` 方式运行时可导入兄弟包 ---
# 当前文件路径: <repo_root>/src/scripts/coordinator.py
# 我们希望把 <repo_root>/src 加入 sys.path，便于 `from tool...` / `from infer...` 正常解析。
_THIS_DIR = os.path.dirname(__file__)
_SRC_ROOT = os.path.abspath(os.path.join(_THIS_DIR, '..'))
if _SRC_ROOT not in sys.path:
    sys.path.insert(0, _SRC_ROOT)



from tool.zhlj_automation import start_zhlj_automation, human_move_and_click
from PIL import Image
from infer.pt_infer import detect_from_pil_pt, load_pt_model
from tool.get_click_xy import analyze_image_recognition

PORT = 5000
ADDR = '127.0.0.1'
EVENT_PATH = '/events'

EVENT_Q = queue.Queue()

# HTTP 请求处理器，把收到的事件放到 EVENT_Q 队列里
class EventHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != EVENT_PATH:
            self.send_response(404)
            self.end_headers()
            return
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        try:
            data = json.loads(body.decode('utf-8'))
        except Exception:
            data = {'raw': body.decode('latin1')}
        # enqueue and respond quickly
        EVENT_Q.put(data)
        self.send_response(202)
        self.end_headers()

    def log_message(self, format, *args):
        # suppress default logging
        return

# 开启一个守护线程的 HTTP 服务器，会把收到的事件放到 EVENT_Q 队列里
def start_http_server():
    server = socketserver.ThreadingTCPServer((ADDR, PORT), EventHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server









def handle_json_and_image(json_event, image_event) -> tuple:
    """占位处理函数（用户自行实现）
    参数:
        json_event: 第一个捕获到的 JSON 类事件（含 json/raw_text/binary_preview_b64 中至少一个）
        image_event: 第一个捕获到的图片事件（含 image_path 字段）
    期望: 用户在此函数中完成坐标计算、日志记录、点击操作等业务逻辑。
    返回: 可返回任意对象；当前调用方不依赖返回值。
    """

    # 1) 取出 JSON 数据（优先使用已解析的 json 字段；否则尝试从 raw_text / binary_preview_b64 解析）
    parsed_json = None
    try:
        if isinstance(json_event.get('json'), (dict, list)):
            parsed_json = json_event.get('json')
        elif isinstance(json_event.get('raw_text'), str):
            try:
                parsed_json = json.loads(json_event['raw_text'])
            except Exception:
                parsed_json = None
        elif isinstance(json_event.get('binary_preview_b64'), str):
            try:
                raw = base64.b64decode(json_event['binary_preview_b64'])
                # 尝试按 utf-8 解码成文本，再尝试 JSON 解析
                text = raw.decode('utf-8', errors='ignore')
                parsed_json = json.loads(text)
            except Exception:
                parsed_json = None
    except Exception:
        parsed_json = None

    # 2) 取出图片并打开为 PIL.Image
    pil_img = None
    image_path = image_event.get('image_path')
    try:
        if image_path and os.path.exists(image_path):
            pil_img = Image.open(image_path).convert('RGB')
    except Exception as e:
        print('[handle] open image failed:', e)


    # FAST: 不打印调试信息，降低 I/O

    # 4) 留出后续实现的占位示例（按需解除注释并实现细节）
    # 示例：模型推理（改为基于仓库结构的绝对路径，避免工作目录导致找不到模型）
    det_results = []
    if pil_img is not None and LOADED_MODEL is not None:
        try:
            det_results = detect_from_pil_pt(pil_img, LOADED_MODEL, conf=0.25)
        except Exception:
            pass

    # 示例：根据 json/pil_img 计算点击坐标
    try:
        x, y = analyze_image_recognition(parsed_json, det_results)
        if x is not None and y is not None:
            return (x + 60, y + 310)
    except Exception:
        pass




def clicker_worker():
    """等待并获取一个 JSON 事件 + 一个图片事件，然后调用用户定义的处理函数，之后退出。
    若在 5 秒内未同时获得两类事件，将自动超时退出。"""
    # 先调用点击操作（只执行一次）
    zhlj_position, timestamp_before_click = start_zhlj_automation()
    spend_before_click = timestamp_before_click - start_time
    print(f"点击前花费时间: {spend_before_click}")
    # FAST: 不打印提示

    json_event = None
    image_event = None
    deadline = time.monotonic() + 5.0  # 5 秒超时

    while True:
        # 计算剩余等待时间
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            # FAST: 静默超时退出
            return
        try:
            evt = EVENT_Q.get(timeout=min(0.5, max(0.05, remaining)))
        except queue.Empty:
            continue
        try:
            if evt is None:
                return

            if image_event is None and 'image_path' in evt:
                image_event = evt
            elif json_event is None and ( 'json' in evt or 'raw_text' in evt or 'binary_preview_b64' in evt ):
                json_event = evt
            else:
                pass

            if json_event and image_event:
                try:
                    icon_position = handle_json_and_image(json_event, image_event)
                    # zhilj_position + icon_position 可用于后续点击操作
                    if icon_position is not None and zhlj_position is not None:
                        abs_x = zhlj_position[0] + icon_position[0]
                        abs_y = zhlj_position[1] + icon_position[1]
                        # human_move_and_click(abs_x, abs_y, speed=0.6)
                        # 计算时间打印时间
                        elapsed = time.time() - start_time
                        print(f"点击操作耗时: {elapsed:.2f} 秒")
                except Exception:
                    pass
                return
        finally:
            EVENT_Q.task_done()









# 启动 mitmdump 子进程，运行指定的脚本
def launch_mitmdump(script_path):
    # Launch mitmdump as a subprocess. Ensure mitmdump is on PATH.
    cmd = ['mitmdump', '-q', '-s', script_path]
    p = subprocess.Popen(cmd)
    return p


def main():

    # FAST: 记录开始时间，减少不必要的开销
    global start_time
    start_time = time.time()
    # 找到这个脚本，用这个脚本启动 mitmdump
    script_path = os.path.join(os.path.dirname(__file__), 'mitm_filter.py')

    # 启动 HTTP 服务器并且维护一个事件队列
    server = start_http_server()

    # 开始点击操作，非阻塞，但是到某一步会等待队列中的数据
    worker_t = threading.Thread(target=clicker_worker, daemon=True)
    worker_t.start()

    # 同步开启 mitmdump 子进程，监听并把数据发到指定端口，由http服务器接收并维护成本地队列
    mitm_proc = launch_mitmdump(script_path)

    # 等待聚合 worker 完成后再清理退出；支持 Ctrl+C 中断
    try:
        worker_t.join()
    except KeyboardInterrupt:
        pass
    finally:
        # 先停止 mitmdump，避免继续产生新事件
        try:
            mitm_proc.terminate()
        except Exception:
            pass
        # 关闭 HTTP 服务，停止接受新请求
        try:
            server.shutdown()
        except Exception:
            pass



if __name__ == '__main__':
    # 预加载模型（若存在），避免在事件到达时再读取磁盘
    LOADED_MODEL = None
    try:
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        _model_path = os.path.join(repo_root, 'model', 'best_renamed.pt')
        if os.path.exists(_model_path):
            LOADED_MODEL = load_pt_model(_model_path)
    except Exception:
        LOADED_MODEL = None

    main()
