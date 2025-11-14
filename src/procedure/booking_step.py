




# 构造请求
import json
import requests
from urllib.parse import urlencode
from infer.pt_infer import detect_from_pil_pt, load_pt_model
from tool import get_click_xy
from tool.decoder_encoder import dxvip_url




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



# 请求referer：https://gym.whu.edu.cn/hsdsqhafive/pages/index/detail?areaId=11&areaNo=2&date=2025-10-16     这里设定areaId、areaNo、date参数
# https://gym.whu.edu.cn/api/GSUser/GetSecurityAuthent?Version=1
# https://gym.whu.edu.cn/api/GSUser/PersonalCenter
# https://gym.whu.edu.cn/api/GSStadiums/GetAppointmentDetail?Version=3&StadiumsAreaId=11&StadiumsAreaNo=1&AppointmentDate=2025-10-16
# https://gym.whu.edu.cn/api/GSConfig/GetAppointmentRules?Version=1



# 请求referer：https://gym.whu.edu.cn/
# https://dxvip.dingxiang-inc.com/api/a?w=300&h=150&s=50&ak=635a429a5f66919cef86083594bdd722&c=68ecfd26gwngvJHkZYIE52tli421yB1bubu40Yv1&jsv=1.5.46.2&aid=dx-1760614921462-39948080-11&wp=1&de=0&lf=0&t=82C6F47324553713DBEDB6442112CD6E5884699D2364DD724FAB0CBA9F6EB1CBE27BF2AD28B071197472E46276521AE4006D3C4365FEF1828D0ABDFCC0DF02F35B8D4ABAF02793563B739E5F3B349103&cid=25842058&_r=0.5421135328921443
# https://static4.dingxiang-inc.com/picture/dx/azzJUeVOSh/sem2lub/ed248f8cbad54474b99bceccd17e8f7c.webp   （来自响应体的tp1字段）
# "logo": "/captcha-custom-image/bb66f2ef16294b329f79c205ccd60500.png"

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



# areaId = 11 # 场馆ID      
# areaNo = 2  # 场地编号
# date = '2025-10-16'  # 预约日期
# 点击预约，武汉大学的处理流程,获取必要的信息，返回WDToken ***************************************************************
def click_reserve_whu_proc(cookies: dict, areaId: int, areaNo: int, date: str, headers: dict):
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




# 用于获取获取验证码信息，判断坐标***************************************
def click_reserve_dxapi_imageInfo(cookies: dict):
    """点击预约, 获取验证码图片,并展示"""
    url,aid = dxvip_url(cookies)
    response = requests.get(url, cookies=cookies, verify=False)
    if response.status_code == 200:
        data = response.json()
        tp1_relative_url = data.get('tp1', '')
        sid = data.get('sid', '')
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
            image.show()
            # 输出image的尺寸
            print(f"验证码图片尺寸: {image.size}, 模式: {image.mode}")
            model = load_pt_model("model\\best_renamed.pt")
            results = detect_from_pil_pt(image, model, conf=0.25)
            for r in results: print(r)
            # 获取目标点坐标
            target_point = get_click_xy.analyze_image_recognition(data, results)
            # 如果不是None打印目标点坐标
            if target_point is not None:
                print("目标点坐标:", target_point)
            else :
                return False

        else:
            print(f"获取验证码图片内容失败，状态码: {image_response.status_code}")
    return sid, aid

# 向https://dxvip.dingxiang-inc.com/api/v2发送请求并接受返回
# 请求头示例
# Host: dxvip.dingxiang-inc.com
# Connection: keep-alive
# Content-Length: 1523
# User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf2541211) XWEB/16815
# Content-type: application/x-www-form-urlencoded
# Accept: */*
# Origin: https://gym.whu.edu.cn
# Sec-Fetch-Site: cross-site
# Sec-Fetch-Mode: cors
# Sec-Fetch-Dest: empty
# Referer: https://gym.whu.edu.cn/
# Accept-Encoding: gzip, deflate, br
# Accept-Language: zh-CN,zh;q=0.9
# 请求体示例（sid要得到之前dxvip的字段返回）
# ac是需要解码
# ac=5288%23jrXnRcINtaCDlr5TXX%2Fn%2BXXnp83XDXuPapK3e2zmVbmMrSDTODFmW8pBukuv9WZDZagewllq20kSH0g0pMt7juyhxCoD5GpGltgC4pf3eWdjNzukPNl9UOBx9k7VcnPUgvBvEGWATAgWGrNpNx%2BJYrfG3XXsVJjT9lUVx%2BhL0ByIXXuj3rX3I5yhe8IXmUPYOT3sXYndutI%2BsV5oRDcnsCWpudviiVgouPm1W%2FT2hho4im5QRt9nYrX%2FXPSnx2mqYn3n5rMWjvSFwXtxjCrnXXe1SkPyoZJwHs1CYXXiMl15VG1AovlMS8rXvW%2BC0962pGXrokeaNJGYVZPu2QzXGos4tZsiMoGjMJGvNZDYBSXnXYD1Sa42oDY2XG1q94zp2QjTMWsO2UGYdWLhtokU2gDpt4La20qXYXXcMlum6su7oZJMpQDOGos8VWDYNWjp2QdnVoe1woFuGozf9WsKrXrXvW%2BrQL%2BM4GXUokeaNJGYVZPu2QzXGos4tZsiMoGjMJGvNZDYBSXZXYfmXm4tXW2XeX3m1AT5DNZCWPTL%2B1uHfNMxfNQdkdvyDNCx4PZHIX2XX%2FI1XXCGQAdUJdcq1XWmGBX4Oy826h9mvXfgPLQKTNnL3R8IUm9fkVSnh62Q1w7G8Nfzf%2F8uIMORO%2Fm5hN76fVuQRwc8Z%2FntDhbkJ%2FZCTPO1iVnoThC4Im9pR1mYn3ge%2FC7GuDn1kyMN8zm1Hy9C8tQUsVoPfrMePd4ak97e6AMak3mE1ASsHMW9jtVY%2BC7wPwmhFayrjNoY4YgJ8N2O4M5w%2FEvhH8CAjtvhI98MPAouk33M%2Fj4hH2Cq1NokHr2LaLCTHXMQYAbYn3ge%2FzVnOrgEaj9fs2m91dvHi%2FXc%2FryGOyTShLn8iCo0uLSff%2FZ7hPMsOV%2FoD2Q7jPgskrSS3Af%2Ff88SYA2JHMC93P5iimn2uhay8Dunka54JTmA8dumi3Mx6C5GYRQ%2BicxBRDb%2B%2BurgDhcnOTIKDtbHJyyZimSSjRgZimQJJVrsHCm7ajauZTXE3z34HXbg66SpYwyssC2pYwCb61oSDRZ%2B424AX6TmWVIzTLvRHr70Y19nJwg%2BimxlYN2vJcbQiVnohY9aW3n3fXaM3PyaIXn2uhWDfMxljtSODDCiJu90DDCsjEof6dxDJc4qDN2xjjbgY6WUn9ItaRX4%2BCC7YDyWkyQ5FTre%2Bm9w1L4Pvy3yY6o3fmygjL7%2BUVgpXdafk8256AVv%2B2yoP9QKRP7k%2BaQKR8rla2%3D%3D
# ak=635a429a5f66919cef86083594bdd722 ak固定 之前dxvip请求构造的请求参数直接用
# c=68f771b3T1EiyYPFHEkZERIgK83WSl3l7RUPMnB1 # 从cookie直接返回
# jsv=1.5.46.2 固定
# sid=495aba41f999e8adc8d67549b6563bbe dxvip请求的响应体直接返回
# aid=dx-1761312159347-51725084-1 之前dxvip请求构造的请求参数直接用
# uid=   固定没有
# type=4 固定
# 发送点击信息到dx

def send_click_info_to_dx(ac, cookies: dict):
    url = "https://dxvip.dingxiang-inc.com/api/v2"
    # 这里一直无需更改
    headers = {
        "Host": "dxvip.dingxiang-inc.com",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf2541211) XWEB/16815",
        "Content-type": "application/x-www-form-urlencoded",
        "Accept": "*/*",
        "Origin": "https://gym.whu.edu.cn",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://gym.whu.edu.cn/",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }
    sid, aid = click_reserve_dxapi_imageInfo(cookies)
    
    data = {
        "ac": ac,
        "ak": "635a429a5f66919cef86083594bdd722", # 咋来的忘了 固定的，但是每个设备不一样！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！
        "c": cookies.get("c", ""),
        "jsv": "1.5.46.2",
        "sid": sid, # 响应体的字段
        "aid": aid, # 时间戳...
        "uid": "",
        "type": 4
    }
    response = requests.post(url, headers=headers, data=urlencode(data), cookies=cookies)
    return response.json()

# https://gym.whu.edu.cn/api/GSOrder/SaveToken
# Host: gym.whu.edu.cn
# Connection: keep-alive
# Content-Length: 225
# Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9uYW1lIjoiMjAyNTI4MjExMDI4MyIsImp0aSI6IjIxMzI4NyIsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvZXhwaXJhdGlvbiI6IjEwLzI1LzIwMjUgMTo1ODoxOSBBTSIsImh0dHA6Ly9zY2hlbWFzLnhtbHNvYXAub3JnL3dzLzIwMDUvMDUvaWRlbnRpdHkvY2xhaW1zL3N5c3RlbSI6Img1IiwiaHR0cDovL3NjaGVtYXMubWljcm9zb2Z0LmNvbS93cy8yMDA4LzA2L2lkZW50aXR5L2NsYWltcy9yb2xlIjoiQ2xpZW50IiwibmJmIjoxNzYxMjg1NDk5LCJleHAiOjE3NjEzMjg2OTksImlzcyI6Ikd5bVJlc2VydmF0aW9uIiwiYXVkIjoid3IifQ.cKBBYubcqA3wtCbLy6NIIOoVSL5MoiEz-Wyw-DgT8vc
# Attestation: CZbor/sWxLEjHjdpscpgOTt+RDKuGrOe9gfH9wczQpSBI8bmlY8Z46Cp65k/HzrvUmPF1pdWk1rF4SN1cxxejipJVUSUB0BIlpKrZHmOSUbG21O7e5MIdoAMQDe3lzMYxCm2FYlTm7LtyoohHDVPmv50qvdf1Ik9Pm7bM3R6MOfoaea4nzFe8bKu/Bz0p8eYagES0NiGa+j7iikbRhUFKWb/KLe36Xne6q0ldfdnHF5NW2mx7FZj0WNhszsY6KLS8m2FwPOhwD21v9NJivAjjg7L7s9ixscgcCnoL+95XEuT8nBDqIy+mtLDK8rPsVz2a+Dj23HjO2+v7acV7ssjOA==
# User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf2541211) XWEB/16815
# Content-Type: application/json
# Accept: */*
# Origin: https://gym.whu.edu.cn
# Sec-Fetch-Site: same-origin
# Sec-Fetch-Mode: cors
# Sec-Fetch-Dest: empty
# Referer: https://gym.whu.edu.cn/hsdsqhafive/pages/index/detail?areaId=11&areaNo=1&date=2025-10-25
# Accept-Encoding: gzip, deflate, br
# Accept-Language: zh-CN,zh;q=0.9
# Cookie: SF_cookie_1=21601193; _dx_uzZo5y=ed74f8edda6ac6779de92840b0fbfb69aa12445cbf17600c8c688ded11479760a7bd3162; _dx_FMrPY6=68f771b3T1EiyYPFHEkZERIgK83WSl3l7RUPMnB1; _dx_app_635a429a5f66919cef86083594bdd722=68f771b3T1EiyYPFHEkZERIgK83WSl3l7RUPMnB1; _dx_captcha_vid=92145188281CE86718842236D27887B77DE5213B546813A46332DF4781F11884F6D9430287C3FF9DB476770488A3BCAE0710B4F5DAC1BEB87F22C7531C8AB23F7B057F028E62E593A924A4992AFA5DEC
# 请求体:
# {
#   "version": 1,
#   "token": "92145188281CE86718842236D27887B77DE5213B546813A46332DF4781F11884F6D9430287C3FF9DB476770488A3BCAE0710B4F5DAC1BEB87F22C7531C8AB23F7B057F028E62E593A924A4992AFA5DEC:68f771b3T1EiyYPFHEkZERIgK83WSl3l7RUPMnB1"
# }

def send_wd_token(headers: dict, cookies: dict, wd_token: str):
    """发送WDToken以完成预约流程"""
    url = 'https://gym.whu.edu.cn/api/GSOrder/SaveToken'
    payload = {
        "version": 1,
        "token": wd_token
    }
    response = requests.post(url, headers=headers, cookies=cookies, json=payload, verify=False)
    if response.status_code == 200:
        print("发送WDToken响应:", response.json())
    else:
        print(f"发送WDToken失败，状态码: {response.status_code}")



# 订单创建
# https://gym.whu.edu.cn/api/GSOrder/Create
# Host: gym.whu.edu.cn
# Connection: keep-alive
# Content-Length: 498
# Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9uYW1lIjoiMjAyNTI4MjExMDI4MyIsImp0aSI6IjIxMzI4NyIsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvZXhwaXJhdGlvbiI6IjEwLzI1LzIwMjUgMTo1ODoxOSBBTSIsImh0dHA6Ly9zY2hlbWFzLnhtbHNvYXAub3JnL3dzLzIwMDUvMDUvaWRlbnRpdHkvY2xhaW1zL3N5c3RlbSI6Img1IiwiaHR0cDovL3NjaGVtYXMubWljcm9zb2Z0LmNvbS93cy8yMDA4LzA2L2lkZW50aXR5L2NsYWltcy9yb2xlIjoiQ2xpZW50IiwibmJmIjoxNzYxMjg1NDk5LCJleHAiOjE3NjEzMjg2OTksImlzcyI6Ikd5bVJlc2VydmF0aW9uIiwiYXVkIjoid3IifQ.cKBBYubcqA3wtCbLy6NIIOoVSL5MoiEz-Wyw-DgT8vc
# Attestation: JclJrU6hGVizzZ939hrZA79PvQn+6YljjoxWWCdb0xw8v4RIuHVNxQ41/8lkskRbh72mrxE53pw3PBGCJL0GFsbjr+sgp9zuJZzadCF0b4EZPNEpldaCixGAgXkVdYWrkbfWK9TlnFbktohlDTja7AMeY6Ff4AnqVha/+A6WNpt2KsCZ37F/mxqtlyH6ey0oLsJbk59R/5O6lEu5lcP1b8u/mAnJoVe5dGP4IOvKb/226eRfnX8grUG87qlY+bb6snX/3qps4tc0QsRBN6k+nPR0xUCDojXtiDEVVv09bTueM/80niTXghSW/hHcECJoaFDYDbWOEZoZ1twbGBnqqw==
# User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf2541211) XWEB/16815
# Content-Type: application/json
# Accept: */*
# Origin: https://gym.whu.edu.cn
# Sec-Fetch-Site: same-origin
# Sec-Fetch-Mode: cors
# Sec-Fetch-Dest: empty
# Referer: https://gym.whu.edu.cn/hsdsqhafive/pages/index/detail?areaId=11&areaNo=1&date=2025-10-25
# Accept-Encoding: gzip, deflate, br
# Accept-Language: zh-CN,zh;q=0.9
# Cookie: SF_cookie_1=21601193; _dx_uzZo5y=ed74f8edda6ac6779de92840b0fbfb69aa12445cbf17600c8c688ded11479760a7bd3162; _dx_FMrPY6=68f771b3T1EiyYPFHEkZERIgK83WSl3l7RUPMnB1; _dx_app_635a429a5f66919cef86083594bdd722=68f771b3T1EiyYPFHEkZERIgK83WSl3l7RUPMnB1; _dx_captcha_vid=92145188281CE86718842236D27887B77DE5213B546813A46332DF4781F11884F6D9430287C3FF9DB476770488A3BCAE0710B4F5DAC1BEB87F22C7531C8AB23F7B057F028E62E593A924A4992AFA5DEC
# 请求体:
# {
#   "version": 4,
#   "stadiumsAreaId": "11",
#   "stadiumsAreaNo": "1",
#   "appointmentStartDate": "2025-10-25 19:00",
#   "appointmentEndDate": "2025-10-25 20:00",
#   "source": 20,
#   "VerifyToken": "92145188281CE86718842236D27887B77DE5213B546813A46332DF4781F11884F6D9430287C3FF9DB476770488A3BCAE0710B4F5DAC1BEB87F22C7531C8AB23F7B057F028E62E593A924A4992AFA5DEC:68f771b3T1EiyYPFHEkZERIgK83WSl3l7RUPMnB1",
#   "f_notify": "https://gym.whu.edu.cn/hsdsqhafive/pages/order/success?type=3",
#   "WDVerifyToken": "4e85fcc8-1788-40ab-8b3b-840e47db8ceb"
# }

def create_order(headers: dict, cookies: dict, areaId: int, areaNo: int, date: str, verify_token: str, wd_verify_token: str, start_hour: int =19, end_hour: int =20):
    """创建预约订单"""
    url = 'https://gym.whu.edu.cn/api/GSOrder/Create'
    appointment_start = f"{date} {start_hour}:00"
    appointment_end = f"{date} {end_hour}:00"
    payload = {
        "version": 4,
        "stadiumsAreaId": str(areaId),
        "stadiumsAreaNo": str(areaNo),
        "appointmentStartDate": appointment_start,
        "appointmentEndDate": appointment_end,
        "source": 20,
        "VerifyToken": verify_token,
        "f_notify": "https://gym.whu.edu.cn/hsdsqhafive/pages/order/success?type=3",
        "WDVerifyToken": wd_verify_token
    }
    response = requests.post(url, headers=headers, cookies=cookies, json=payload, verify=False)
    if response.status_code == 200:
        print("创建订单响应:", response.json())
    else:
        print(f"创建订单失败，状态码: {response.status_code}")