# mitmproxy addon: filter specific responses and print/save them
# Usage:
#   mitmdump -s mitm_filter.py
# It will:
# - For GET https://dxvip.dingxiang-inc.com/api/a2* responses: parse JSON body and pretty-print to stdout
# - For GET https://static4.dingxiang-inc.com/picture* responses: save image to ./captured_images and open it (Pillow)

from mitmproxy import http, ctx
import os
import json
import time
import re
from urllib.parse import urlparse
from queue import Queue
import threading
import uuid
import base64
try:
    import requests
    requests_available = True
except Exception:
    requests_available = False

try:
    from PIL import Image
    from io import BytesIO
    pillow_available = True
except Exception:
    pillow_available = False

DXVIP_PREFIX = "https://dxvip.dingxiang-inc.com/api/a"
STATIC4_PREFIX = "https://static4.dingxiang-inc.com/picture"

OUT_DIR = os.path.join(os.path.dirname(__file__), "captured_images")
if not os.path.isdir(OUT_DIR):
    try:
        os.makedirs(OUT_DIR, exist_ok=True)
    except Exception:
        pass

# optional JSON log file for easier inspection (append-only)
LOG_FILE = os.path.join(os.path.dirname(__file__), "captured_jsons.log")

# send events to local processing service to avoid blocking mitmproxy
PROCESSOR_URL = "http://127.0.0.1:5000/events"
OUT_Q = Queue()

def _sender_thread():
    while True:
        evt = OUT_Q.get()
        if evt is None:
            break
        if not requests_available:
            # fallback: write to log
            try:
                with open(LOG_FILE, 'a', encoding='utf-8') as lf:
                    lf.write(json.dumps(evt, ensure_ascii=False) + "\n")
            except Exception:
                pass
            OUT_Q.task_done()
            continue
        try:
            requests.post(PROCESSOR_URL, json=evt, timeout=1.0)
        except Exception:
            # best-effort: write to local failed file
            try:
                with open(os.path.join(os.path.dirname(__file__), 'failed_events.jsonl'), 'a', encoding='utf-8') as ff:
                    ff.write(json.dumps(evt, ensure_ascii=False) + "\n")
            except Exception:
                pass
        OUT_Q.task_done()

# start sender thread
_t = threading.Thread(target=_sender_thread, daemon=True)
_t.start()

class FilterAddon:
    def response(self, flow: http.HTTPFlow):
        try:
            req = flow.request
            resp = flow.response
            # FAST: 最小化调试信息，减少 I/O
            status = getattr(resp, 'status_code', None)
            # only consider GET
            if req.method.upper() != 'GET':
                return

            url = req.pretty_url

            # dxvip JSON responses
            if url.startswith(DXVIP_PREFIX):
                # try parse JSON
                content_type = resp.headers.get('Content-Type', '')
                data = resp.content
                # FAST: 不写入日志文件，直接尝试解析并发送事件
                text = None
                parsed = None
                try:
                    # prefer decoding as utf-8
                    text = data.decode('utf-8')
                except Exception:
                    try:
                        text = data.decode('latin1')
                    except Exception:
                        text = None
                if text:
                    try:
                        parsed = json.loads(text)
                    except Exception:
                        parsed = None
                if parsed is not None:
                    # FAST: 不打印/不持久化，仅发送事件
                    try:
                        evt = {
                            'id': str(uuid.uuid4()),
                            'ts': time.time(),
                            'url': url,
                            'status': status,
                            'json': parsed,
                        }
                        OUT_Q.put(evt)
                    except Exception:
                        pass
                else:
                    # FAST fallback: 直接发送简化事件
                    if text:
                        try:
                            evt = {'id': str(uuid.uuid4()), 'ts': time.time(), 'url': url, 'raw_text': text[:4000]}
                            OUT_Q.put(evt)
                        except Exception:
                            pass
                    else:
                        try:
                            preview = base64.b64encode(data[:4096]).decode('ascii')
                            evt = {'id': str(uuid.uuid4()), 'ts': time.time(), 'url': url, 'binary_preview_b64': preview}
                            OUT_Q.put(evt)
                        except Exception:
                            pass

            # static4 images
            elif url.startswith(STATIC4_PREFIX):
                data = resp.content
                if not data:
                    return
                # decide file extension from content-type
                ctype = resp.headers.get('Content-Type', '')
                ext = '.img'
                if 'png' in ctype:
                    ext = '.png'
                elif 'jpeg' in ctype or 'jpg' in ctype:
                    ext = '.jpg'
                elif 'webp' in ctype:
                    ext = '.webp'
                elif 'gif' in ctype:
                    ext = '.gif'

                # save to OUT_DIR
                fname = f"{int(time.time()*1000)}_{uuid.uuid4().hex}{ext}"
                fpath = os.path.join(OUT_DIR, fname)
                try:
                    with open(fpath, 'wb') as f:
                        f.write(data)
                except Exception:
                    return

                # FAST: 不进行 Pillow 解析/日志

                # send an image event to local processor
                try:
                    evt = {
                        'id': str(uuid.uuid4()),
                        'ts': time.time(),
                        'url': url,
                        'status': status,
                        'image_path': fpath,
                    }
                    OUT_Q.put(evt)
                except Exception:
                    pass
        except Exception:
            pass

addons = [FilterAddon()]
