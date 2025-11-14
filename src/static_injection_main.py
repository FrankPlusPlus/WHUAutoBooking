
from http.cookies import SimpleCookie
import sys
from procedure.booking_step import check_sports_type, check_stadium_area, click_reserve_dxapi_imageInfo, click_reserve_whu_proc
sys.stdout.reconfigure(encoding='utf-8')
from tool.data_fetcher import load_config






cfg = load_config()
token = cfg.get("token", "")
cookie_str = cfg.get("cookie_str", "")

referer = 'https://gym.whu.edu.cn/hsdsqhafive/pages/index/reserve?typeId=22&title=%E4%B9%92%E4%B9%93%E7%90%83%E9%A2%84%E7%BA%A6%E5%88%97%E8%A1%A8'
# _dx_FMrPY6这是从验证方获取的

def get_header_cookies(token: str, referer: str):
    """获取Headers和Cookies"""
    # 从Reqable复制的Headers（替换为你的实际值）
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf2541022) XWEB/16467',
        'Authorization': f'{token}',
        'Content-Type': 'application/json',
        'Referer': f'{referer}',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    return headers

def get_cookies(cookie_str: str):
    """将Cookie字符串转换为字典"""
    cookie = SimpleCookie()
    cookie.load(cookie_str)
    return {key: morsel.value for key, morsel in cookie.items()}

headers = get_header_cookies(token, referer)
cookies = get_cookies(cookie_str)






# test **************************************************************************************************************************************************

# 测试Token是否有效
if check_sports_type(headers, cookies, '2025-10-16', sports_typeId=22):
    print("✅ 可以开始预约操作！")
else:
    print("❌ 需要重新登录获取新Token")

if check_stadium_area(headers, cookies, '2025-10-16', stadiums_areaId=9):
    print("✅ 可以开始预约操作！")
else:
    print("❌ 需要重新登录获取新Token")


click_reserve_whu_proc(cookies, areaId=11, areaNo=2, date='2025-10-17', headers=headers)


# 循环执行click_reserve_dxapi_imageInfo，如果target_point为None，就终止循环

# while target_point is not None:
click_reserve_dxapi_imageInfo(cookies)

