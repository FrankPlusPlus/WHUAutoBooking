# 我想使用mitmproxy实时获取
# https://dxvip.dingxiang-inc.com/api/a2?
# https://static4.dingxiang-inc.com/picture
# 上述url片段开头的GET方法的响应体并打印
from mitmproxy import http
from mitmproxy import ctx
import re
import json
import os
import datetime
import random
from pathlib import Path
from typing import Any, Dict, Optional
import sys


# Output directory for saved artifacts (images / raw responses)
OUT_DIR = Path.home() / "mitm_captures"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def _safe_name(prefix: str, ext: str = "") -> Path:
    ts = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
    rnd = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=6))
    name = f"{ts}_{prefix}_{rnd}{ext}"
    return OUT_DIR / name


def _find_value_recursive(obj: Any, key: str) -> Optional[Any]:
    """Recursively search for key in nested dict/list and return first value found."""
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for v in obj.values():
            res = _find_value_recursive(v, key)
            if res is not None:
                return res
    elif isinstance(obj, list):
        for item in obj:
            res = _find_value_recursive(item, key)
            if res is not None:
                return res
    return None


class CatchResponses:
    """mitmproxy addon: capture specific JSON fields and open images.

    - For requests matching dxvip.../api/a2? extract verifyType and childVerifyType from JSON response
    - For requests matching static4.../picture save the image and open it with the OS default image viewer
    """

    def __init__(self):
        # use simple prefix regexes
        self.api_pattern = re.compile(r"https?://dxvip\.dingxiang-inc\.com/api/a2")
        self.img_pattern = re.compile(r"https?://static4\.dingxiang-inc\.com/picture")

    def response(self, flow: http.HTTPFlow) -> None:
        url = flow.request.url
        url = flow.request.url
        try:
            # API JSON case
            if self.api_pattern.search(url):
                content_bytes = flow.response.get_content()
                # try decode as text
                try:
                    text = content_bytes.decode(flow.response.charset or 'utf-8', errors='replace')
                except Exception:
                    text = content_bytes.decode('utf-8', errors='replace')

                try:
                    obj = json.loads(text)
                except Exception:
                    ctx.log.warn(f"Failed to parse JSON from {url}")
                    ctx.log.info(text[:1000])
                    return

                vt = _find_value_recursive(obj, 'verifyType')
                cvt = _find_value_recursive(obj, 'childVerifyType')
                ctx.log.info(f"Captured JSON from: {url} | verifyType={vt} childVerifyType={cvt}")
                # Print the token string as requested
                print("夸克")
                return

            # Image case
            if self.img_pattern.search(url):
                content_bytes = flow.response.get_content()
                # Try to open image directly from memory using PIL if available
                try:
                    import io
                    from PIL import Image

                    img = Image.open(io.BytesIO(content_bytes))
                    # show uses a temporary file / viewer under the hood but we don't persist explicitly
                    img.show()
                    # Print the requested token
                    print("夸克")
                    ctx.log.info(f"Displayed image from: {url} (in-memory)")
                except ImportError:
                    # PIL not available: fallback to temporary file open (still tries not to keep permanent file)
                    try:
                        import tempfile
                        import subprocess
                        suffix = ''
                        ctype = flow.response.headers.get('content-type', '')
                        if 'jpeg' in ctype:
                            suffix = '.jpg'
                        elif 'png' in ctype:
                            suffix = '.png'
                        elif 'gif' in ctype:
                            suffix = '.gif'
                        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tf:
                            tf.write(content_bytes)
                            tmp_path = tf.name
                        ctx.log.info(f"Wrote temp image to: {tmp_path}")
                        # open with default viewer
                        if os.name == 'nt':
                            os.startfile(tmp_path)
                        else:
                            opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
                            subprocess.Popen([opener, tmp_path])
                        print("夸克")
                    except Exception as e:
                        ctx.log.error(f"Failed to display image from {url}: {e}")
                except Exception as e:
                    ctx.log.error(f"Error opening image in-memory: {e}")
                return

        except Exception as e:
            ctx.log.error(f"Error in addon response handler: {e}")


addons = [CatchResponses()]

# To run this script, save it as mitmproxy_catch.py and execute mitmproxy with:
# mitmproxy -s mitmproxy_catch.py
# Make sure to configure your system or application to use mitmproxy as the HTTP proxy.
# The captured responses will be printed in the mitmproxy console.
# Note: Ensure that you have mitmproxy installed in your Python environment.
# You can install it via pip if you haven't done so:
# pip install mitmproxy
# Also, remember to trust the mitmproxy CA certificate in your system or application
# to intercept HTTPS traffic properly.
# For more details, refer to the mitmproxy documentation: https://docs.mitmproxy.org/
# Enjoy capturing your desired responses!
