import requests
import json
from http.cookies import SimpleCookie
import time
import random
import sys
sys.stdout.reconfigure(encoding='utf-8')


token = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9uYW1lIjoiMjAyNTI4MjExMDI4MyIsImp0aSI6IjIxMzI4NyIsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvZXhwaXJhdGlvbiI6IjEwLzE5LzIwMjUgNzoyNzozMiBBTSIsImh0dHA6Ly9zY2hlbWFzLnhtbHNvYXAub3JnL3dzLzIwMDUvMDUvaWRlbnRpdHkvY2xhaW1zL3N5c3RlbSI6Img1IiwiaHR0cDovL3NjaGVtYXMubWljcm9zb2Z0LmNvbS93cy8yMDA4LzA2L2lkZW50aXR5L2NsYWltcy9yb2xlIjoiQ2xpZW50IiwibmJmIjoxNzYwNzg2ODUyLCJleHAiOjE3NjA4MzAwNTIsImlzcyI6Ikd5bVJlc2VydmF0aW9uIiwiYXVkIjoid3IifQ.HkeHuIZhpR5suX6aEOK3nF8bskZK4Ueihsg_euBZckM'
# 智慧珞珈url
# https://gym.whu.edu.cn/hsdsqhafive/pages/index/reserve?typeId=22&title=%E4%B9%92%E4%B9%93%E7%90%83%E9%A2%84%E7%BA%A6%E5%88%97%E8%A1%A8
# https://gym.whu.edu.cn/hsdsqhafive/pages/index/reserve?typeId=22&title=%E4%B9%92%E4%B9%93%E7%90%83%E9%A2%84%E7%BA%A6%E5%88%97%E8%A1%A8



referer = 'https://gym.whu.edu.cn/hsdsqhafive/pages/index/reserve?typeId=22&title=%E4%B9%92%E4%B9%93%E7%90%83%E9%A2%84%E7%BA%A6%E5%88%97%E8%A1%A8'
# _dx_FMrPY6这是从验证方获取的
cookie_str = 'SF_cookie_1=22201493; iPlanetDirectoryPro=hfSj54LJNbIb6nfjwg7HpR; _dx_uzZo5y=ed74f8edda6ac6779de92840b0fbfb69aa12445cbf17600c8c688ded11479760a7bd3162; _dx_FMrPY6=68ecfd26gwngvJHkZYIE52tli421yB1bubu40Yv1; _dx_app_635a429a5f66919cef86083594bdd722=68ecfd26gwngvJHkZYIE52tli421yB1bubu40Yv1'



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


# SportsTypeId运动类型
# 22 乒乓球
# 21 羽毛球
# StadiumsAreaId  场馆Id
# 2  风雨羽毛球体育馆
# 3  卓尔羽毛球体育馆
# 4  星湖羽毛球体育馆
# 5  竹园羽毛球体育馆
# 6  松园羽毛球体育馆

# 9  风雨乒乓球体育馆
# 10 竹园乒乓球体育馆
# 11 松园乒乓球体育馆

# https://gym.whu.edu.cn/api/GSStadiums/GetAppointmentAreaList?Version=2&StadiumsAreaId=11&AppointmentDate=2025-10-16

def check_sports_type(headers: dict, cookies: dict, date_str: str, sports_typeId: int):
    """检查可预约场地"""
    url = f'https://gym.whu.edu.cn/api/GSStadiums/GetAppointmentList?Version=2&SportsTypeId={sports_typeId}&AppointmentDate={date_str}'
    
    # print status code and response
    response = requests.get(url, headers=headers, cookies=cookies, verify=False)
    if response.status_code == 200:
        print("Token有效，可以开始预约")
        data = response.json()
        print("可用场地:", json.dumps(data, ensure_ascii=False, indent=2))
        return True
    else:
        print(f"Token可能已过期，状态码: {response.status_code}")
        return False


def check_stadium_area(headers: dict, cookies: dict, date_str: str, stadiums_areaId: int):
    """检查可预约场地"""
    url = f'https://gym.whu.edu.cn/api/GSStadiums/GetAppointmentAreaList?Version=2&StadiumsAreaId={stadiums_areaId}&AppointmentDate={date_str}'
    
    # print status code and response
    response = requests.get(url, headers=headers, cookies=cookies, verify=False)
    if response.status_code == 200:
        print("Token有效，可以开始预约")
        data = response.json()
        print("可用场地:", json.dumps(data, ensure_ascii=False, indent=2))
        return True
    else:
        print(f"Token可能已过期，状态码: {response.status_code}")
        return False




# 请求referer：https://gym.whu.edu.cn/hsdsqhafive/pages/index/detail?areaId=11&areaNo=2&date=2025-10-16     这里设定areaId、areaNo、date参数
# https://gym.whu.edu.cn/api/GSUser/GetSecurityAuthent?Version=1
# https://gym.whu.edu.cn/api/GSUser/PersonalCenter
# https://gym.whu.edu.cn/api/GSStadiums/GetAppointmentDetail?Version=3&StadiumsAreaId=11&StadiumsAreaNo=1&AppointmentDate=2025-10-16
# https://gym.whu.edu.cn/api/GSConfig/GetAppointmentRules?Version=1



# 请求referer：https://gym.whu.edu.cn/
# https://dxvip.dingxiang-inc.com/api/a?w=300&h=150&s=50&ak=635a429a5f66919cef86083594bdd722&c=68ecfd26gwngvJHkZYIE52tli421yB1bubu40Yv1&jsv=1.5.46.2&aid=dx-1760614921462-39948080-11&wp=1&de=0&lf=0&t=82C6F47324553713DBEDB6442112CD6E5884699D2364DD724FAB0CBA9F6EB1CBE27BF2AD28B071197472E46276521AE4006D3C4365FEF1828D0ABDFCC0DF02F35B8D4ABAF02793563B739E5F3B349103&cid=25842058&_r=0.5421135328921443
# https://static4.dingxiang-inc.com/picture/dx/azzJUeVOSh/sem2lub/ed248f8cbad54474b99bceccd17e8f7c.webp   （来自响应体的tp1字段）
# "logo": "/captcha-custom-image/bb66f2ef16294b329f79c205ccd60500.png"






# areaId = 11 # 场馆ID      
# areaNo = 2  # 场地编号
# date = '2025-10-16'  # 预约日期
# 点击预约，武汉大学的处理流程,获取必要的信息，返回WDToken ***************************************************************
def click_reserve_whu_proc(cookies: dict, areaId: int, areaNo: int, date: str):
    """点击预约，武汉大学的处理流程,获取必要的信息，返回WDToken"""
    referer_base_url = 'https://gym.whu.edu.cn/hsdsqhafive/pages/index/detail'
    # 预约参数 areaId、areaNo、date
    referer_url = f'{referer_base_url}?areaId={areaId}&areaNo={areaNo}&date={date}'
    # 1. 获取安全验证
    auth_url = 'https://gym.whu.edu.cn/api/GSUser/GetSecurityAuthent?Version=1'
    # 2. 获取个人信息  
    personal_url = 'https://gym.whu.edu.cn/api/GSUser/PersonalCenter'
    # 3. 获取预约详情
    detail_url = f'https://gym.whu.edu.cn/api/GSStadiums/GetAppointmentDetail?Version=3&StadiumsAreaId={areaId}&StadiumsAreaNo={areaNo}&AppointmentDate={date}'
    # 4. 获取预约规则
    rules_url = 'https://gym.whu.edu.cn/api/GSConfig/GetAppointmentRules?Version=1'
    # 发送请求并处理响应
    with requests.Session() as session:
        session.headers.update({
            'User-Agent': headers['User-Agent'],
            'Authorization': headers['Authorization'],
            'Referer': referer_url,
            'Content-Type': 'application/json',
            'Accept-Language': 'zh-CN,zh;q=0.9'
        })
        # 静态注入cookies
        session.cookies.update(cookies)

        # 1. 获取安全验证
        auth_response = session.get(auth_url, verify=False)
        print("安全验证响应:", auth_response.json())

        # 2. 获取个人信息
        personal_response = session.get(personal_url, verify=False)
        print("个人信息响应:", personal_response.json())

        # 3. 获取预约详情
        detail_response = session.get(detail_url, verify=False)
        print("预约详情响应:", detail_response.json())
        # 提取detail_response中响应体"WDToken"字段内容
        detail_data = detail_response.json()
        wd_token = detail_data.get('WDToken', '')
        print("提取的WDToken:", wd_token)

        # 4. 获取预约规则
        rules_response = session.get(rules_url, verify=False)
        print("预约规则响应:", rules_response.json())

    return wd_token




# 给dxvip_url函数传入cookies字典(待用) 被dxvip_url调用
def analyze_dxurl(dx_url: str):    
    """解析dxvip验证URL，提取参数"""
    from urllib.parse import urlparse, parse_qs

    parsed_url = urlparse(dx_url)
    query_params = parse_qs(parsed_url.query)

    # 提取参数并转换为单值
    dx_params = {key: value[0] for key, value in query_params.items()}
    return dx_params


# 生成dxvip验证URL，定期静态注入******被多个函数调用
def dxvip_url(cookies: dict):
    # 静态参数，一次验证固定不变
    w, h, s = 300, 150, 50
    ak = '635a429a5f66919cef86083594bdd722'
    jsv = '1.5.46.2'
    wp, de, lf = 1, 0, 0
    # 待确认参数
    cid = '25842058'  # 页面或接口获取
    t = '82C6F47324553713DBEDB6442112CD6E5884699D2364DD724FAB0CBA9F6EB1CBE27BF2AD28B071197472E46276521AE4006D3C4365FEF1828D0ABDFCC0DF02F35B8D4ABAF02793563B739E5F3B349103'  # 页面JS生成
    # 动态参数
    # 从cookie或页面获取c
    c = cookies.get('_dx_FMrPY6', '')
    aid = f'dx-{int(time.time()*1000)}-{random.randint(10000000,99999999)}-1'
    _r = random.random()
    # 组装URL
    dx_url = f'https://dxvip.dingxiang-inc.com/api/a?w={w}&h={h}&s={s}&ak={ak}&c={c}&jsv={jsv}&aid={aid}&wp={wp}&de={de}&lf={lf}&t={t}&cid={cid}&_r={_r}'
    return dx_url



# 生成验证码图片描述信息, 被 combine_ultimate_dx_image, info 调用
def generate_dx_image_description(data, tp1_url: str):
    """生成验证码图片描述信息"""
    # 从请求tp1_url的响应体中获取关键字段verifyType、childVerifyType、imgName、color、logo等
    verifyType = str(data.get('verifyType', ''))
    childVerifyType = str(data.get('childVerifyType', ''))
    imgName = str(data.get('imgName', ''))
    color = str(data.get('color', ''))
    # 把imgName和color翻译成中文
    logo = data.get('logo', '')
    # 对于verifyType-childVerifyType各种情况的验证码描述
    # 0-0：请点击图形-平面的
    # 0-1：请点击图形-立体的
    # 1-0：请点击图形（带颜色）（带立体or平面）=字段（imgName立体还是平面、color颜色）
    # 1-1：请点击颜色与xx一致的图形=字段（imgName图形名、color颜色）
    # 2-0：请点击字母-小写的
    # 2-1：请点击字母-大写的
    # 下面都带=字段（imgName图形名）
    # 3-0：请点击离xx最近的字母
    # 3-1：请点击xx左侧的字母
    # 3-2：请点击xx右侧的字母
    # 3-3：请点击xx上方的字母
    # 3-4：请点击xx下方的字母
    IMG_NAME_MAP = {
        'circle': '圆形',
        'triangle': '三角形',
        'square': '正方形',
        'rectangle': '矩形',
        'diamond': '菱形',
        'trapezoid': '梯形',
        'parallelogram': '平行四边形',
        'fillet_rectangle': '圆角矩形',
        'star': '星形',
        'pentagon': '五边形',
        'hexagon': '六边形',
        'cylinder': '圆柱体',
        'cone': '圆锥',
        'cube': '立方体',
        'sphere': '球',
        'solid': '立体',
        'plane': '平面'
        # 根据实际返回值继续补充
    }
    COLOR_MAP = {
        'red': '红色',
        'green': '绿色',
        'blue': '蓝色'
    }
    img_ch = IMG_NAME_MAP.get(imgName, imgName)
    color_ch = COLOR_MAP.get(color, color)
    if color_ch == 'None':
        color_ch = ''
    if img_ch == 'None':
        img_ch = ''
    description = ""
    if verifyType == '0':
        if childVerifyType == '0':
            description = f"请点击{color_ch}平面图形"
        elif childVerifyType == '1':
            description = f"请点击{color_ch}立体图形" 
    elif verifyType == '1':
        if childVerifyType == '0':
            description = f"请点击{color_ch}的{img_ch}图形"
        elif childVerifyType == '1':
            description = f"请点击除{img_ch}外的{color_ch}图形"
    elif verifyType == '2':
        if childVerifyType == '0':
            description = f"请点击小写{color_ch}字母"
        elif childVerifyType == '1':   # 只有图形却跑到这个大写字母
            description = f"请点击大写{color_ch}字母"
    elif verifyType == '3':
        directions = {
            '0': '最近的',
            '1': '左侧的',
            '2': '右侧的',
            '3': '上方的',
            '4': '下方的'
        }
        direction_desc = directions.get(childVerifyType, '')
        description = f"请点击{img_ch}{direction_desc}字母"
    print("验证码图片描述信息:", description)
    return description, verifyType, childVerifyType




# 组合最终验证码图片，添加描述信息，被 click_reserve_dxapi_imageInfo 调用
def combine_ultimate_dx_image(data, tp1_url: str, image):
    """组合终极验证码图片，添加描述信息
        输入参数：
            cookies: dict - 用于生成描述信息的Cookies
            tp1_url: str - 验证码图片URL
            image: PIL.Image - 原始验证码图片
    """
    description, verifyType, childVerifyType = generate_dx_image_description(data, tp1_url)
    if description:
        from PIL import Image, ImageDraw, ImageFont
        
        print(f"原图尺寸: {image.size}, 模式: {image.mode}")
        
        # 保持原图模式（RGBA），不转换为RGB
        # 这样你可以获取目标图像的准确坐标
        
        try:
            font = ImageFont.truetype("simhei.ttf", 15)
        except:
            try:
                font = ImageFont.truetype("/Library/Fonts/Arial Unicode.ttf", 15)
            except:
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf", 15)
                except:
                    print("未找到中文字体，无法显示中文")
                    font = ImageFont.load_default()
        
        # 创建临时画布准确计算文字高度
        temp_draw = ImageDraw.Draw(Image.new('RGB', (1, 1)))
        bbox = temp_draw.textbbox((0, 0), description, font=font)
        text_height = bbox[3] - bbox[1]
        text_width = bbox[2] - bbox[0]
        
        print(f"文字尺寸: {text_width} x {text_height}")
        
        # 计算新画布尺寸 - 文字放在下方
        margin = 15
        new_width = max(image.width, text_width + margin * 2)
        new_height = image.height + text_height + margin * 2
        
        print(f"新画布尺寸: {new_width} x {new_height}")
        
        # 创建新画布，保持与原图相同的模式
        # 注意：不对原图进行缩放或压缩，仅在下方额外增加用于显示文字的画布高度
        # 背景颜色需要与 image.mode 匹配：RGBA -> 4 元素，RGB -> 3 元素，其他模式使用单个灰度值
        if image.mode == 'RGBA':
            # 使用不透明白色背景，这样下方新增区域为白色，同时保留原图视觉不变
            bg_color = (255, 255, 255, 255)  # 白色不透明背景
        elif image.mode == 'RGB':
            bg_color = (255, 255, 255)  # 白色背景
        else:
            # 对于灰度图等其他模式，使用单值填充（白色）
            bg_color = 255

        new_image = Image.new(image.mode, (new_width, new_height), bg_color)
        
        # 将原图粘贴到新画布顶部（RGBA 需要使用 mask 保留 alpha）
        x_offset = (new_width - image.width) // 2
        if image.mode == 'RGBA':
            new_image.paste(image, (x_offset, 0), mask=image)
        else:
            new_image.paste(image, (x_offset, 0))
        
        # 添加文字到图片下方
        draw = ImageDraw.Draw(new_image)
        text_x = (new_width - text_width) // 2
        text_y = image.height + margin
        
        # 在文字下方添加一个白色背景矩形以提高可读性
        # 填充颜色需要与画布模式一致
        bg_margin = 5
        if image.mode == 'RGBA':
            rect_fill = (255, 255, 255, 255)
        elif image.mode == 'RGB':
            rect_fill = (255, 255, 255)
        else:
            rect_fill = 255

        draw.rectangle(
            [text_x - bg_margin, text_y - bg_margin, 
             text_x + text_width + bg_margin, text_y + text_height + bg_margin],
            fill=rect_fill
        )
        
        draw.text((text_x, text_y), description, fill='black', font=font)
        
        return new_image
    else:
        return image



# 用于获取获取验证码信息***************************************
def click_reserve_dxapi_imageInfo(cookies: dict, no: int, proc: bool):
    """点击预约, 获取验证码图片,并展示"""
    url = dxvip_url(cookies)
    response = requests.get(url, cookies=cookies, verify=False)
    if response.status_code == 200:
        data = response.json()
        tp1_relative_url = data.get('tp1', '')
        print("验证码图片URL:", tp1_relative_url)
    else:
        print(f"获取验证码图片相对url失败，状态码: {response.status_code}")   
    
    # 根据tp1_url访问图片，并使用PIL展示
    if tp1_relative_url:
        tp1_base_url = 'https://static4.dingxiang-inc.com/picture'  # 或用从 dx 接口/响应中推断出的 base
        tp1_url = f'{tp1_base_url}{tp1_relative_url}'
        print("完整验证码图片URL:", tp1_url)
        image_response = requests.get(tp1_url, verify=False)
        if image_response.status_code == 200:
            from PIL import Image
            from io import BytesIO
            image = Image.open(BytesIO(image_response.content))
            # 直接调用组合函数处理加入文字描述
            ultimateImage = combine_ultimate_dx_image(data, tp1_url, image)
            # ultimateImage.show()

            # 获取图片的类别
            description, verifyType, childVerifyType = generate_dx_image_description(data, tp1_url)
            path_1 = f'proc_image/test{no}.jpg'
            path_21 = f'raw_image/basic/test{no}.jpg'
            path_22 = f'raw_image/letter/test{no}.jpg'
            # 如果verifyType = 1，2，3，4保存到不同的路径
            if verifyType in ['0', '1']:
                if proc:
                    ultimateImage.save(path_1, format='JPEG')
                else:
                    image.save(path_21, format='JPEG')
            elif verifyType in ['2', '3']:
                if proc:
                    ultimateImage.save(path_1, format='JPEG')
                else:
                    image.save(path_22, format='JPEG')
        else:
            print(f"获取验证码图片内容失败，状态码: {image_response.status_code}")


# test

# 测试Token是否有效
if check_sports_type(headers, cookies, '2025-10-16', sports_typeId=22):
    print("✅ 可以开始预约操作！")
else:
    print("❌ 需要重新登录获取新Token")

if check_stadium_area(headers, cookies, '2025-10-16', stadiums_areaId=9):
    print("✅ 可以开始预约操作！")
else:
    print("❌ 需要重新登录获取新Token")


click_reserve_whu_proc(cookies, areaId=11, areaNo=2, date='2025-10-17')


for no in range(1, 500):
    click_reserve_dxapi_imageInfo(cookies, no, False)
    # 睡眠1秒
    time.sleep(1)

