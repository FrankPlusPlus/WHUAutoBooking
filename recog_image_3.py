import base64
import json
import requests
from PIL import Image, ImageDraw
from dotenv import load_dotenv
import os
from getpass import getpass

load_dotenv()  # 会把 .env 中的键值加载到环境变量
user = os.environ.get('MY_APP_USER') or input('用户名: ')
pwd = os.environ.get('MY_APP_PASS') or getpass('密码（不会回显）: ')

# 复制以下代码，只需填入自己的账号密码、待识别的图片路径即可。
# 关于ID：选做识别的模型ID。


def b64_api(username, password, img_path, ID):
    with open(img_path, 'rb') as f:
        b64_data = base64.b64encode(f.read())
    b64 = b64_data.decode()
    data = {"username": username, "password": password, "ID": ID, "b64": b64, "version": "3.1.1"}
    data_json = json.dumps(data)
    result = json.loads(requests.post("http://www.tulingcloud.com/tuling/predict", data=data_json).text)
    return result

def mark_and_show_png(png_path: str, x: int, y: int, radius: int = 5, color=(255, 0, 0)):
    """在不改变图片其他模式的前提下，在 (x,y) 位置画一个红点并显示。

    - png_path: 原图路径（PNG）
    - x,y: 像素坐标
    - radius: 点半径（像素）
    - color: RGB 颜色元组
    该函数会在内存中创建一份副本进行绘制，原文件不改动。
    """
    img = Image.open(png_path)
    # 保持原模式，使用 RGBA 临时画布合成以支持透明
    base_mode = img.mode
    if base_mode in ('RGBA', 'LA'):
        canvas = img.copy()
        draw = ImageDraw.Draw(canvas)
    else:
        # 如果不是带 alpha 的模式，创建 RGBA 画布用于绘制，再转换回原模式
        canvas = img.convert('RGBA')
        draw = ImageDraw.Draw(canvas)

    # 画点（使用填充圆）
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)

    # 显示：如果原始不是 RGBA，则转换回原始模式以保持外观
    if base_mode in ('RGBA', 'LA'):
        canvas.show()
    else:
        canvas.convert(base_mode).show()


def get_xy_from_result(result):
    # 支持 dict 或 JSON 字符串
    if isinstance(result, str):
        result = json.loads(result)
    try:
        inner = result['data']['result']
        x = inner['X坐标值']
        y = inner['Y坐标值']
        return int(x), int(y)
    except Exception as e:
        # 如果键不存在或类型错误，会抛出并返回 None
        print('提取坐标失败：', e)
        return None
    
if __name__ == "__main__":
    img_path = 'proc_image/test3.png'  # 待识别的图片路径
    result = b64_api(username=user, password=pwd, img_path=img_path, ID="52021448")
    print(result)
    x, y = get_xy_from_result(result)
    print(f"提取的坐标：X={x}, Y={y}")
    if x is not None and y is not None:
        mark_and_show_png(img_path, x, y)