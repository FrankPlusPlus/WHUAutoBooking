import requests
import time
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from datetime import date, timedelta


# 失效快
COOKIE = "SF_cookie_1=22201493; _dx_uzZo5y=ed74f8edda6ac6779de92840b0fbfb69aa12445cbf17600c8c688ded11479760a7bd3162; _dx_FMrPY6=6910904dFluWiCl1ZJBzwww1vy2N1VZS1BG1HK21; _dx_app_635a429a5f66919cef86083594bdd722=6910904dFluWiCl1ZJBzwww1vy2N1VZS1BG1HK21; _dx_captcha_vid=2AA015484FB1513EA773438EFE3B81AEE9A455B03D4ACDCBD290C7B7A93711EC4DCD59FD9CB9818099828D8BD91CF8D0AC5DF33484524EFD7B8A59DF74268E1F2154E7B887FCAA2379C4E268099527DC; iPlanetDirectoryPro=XsGKst2jYcpVjOSSNFoDxa"
# 失效慢一点
TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9uYW1lIjoiMjAyNTI4MjExMDI4MyIsImp0aSI6IjIxMzI4NyIsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvZXhwaXJhdGlvbiI6IjExLzE0LzIwMjUgMzowODoyNCBBTSIsImh0dHA6Ly9zY2hlbWFzLnhtbHNvYXAub3JnL3dzLzIwMDUvMDUvaWRlbnRpdHkvY2xhaW1zL3N5c3RlbSI6Img1IiwiaHR0cDovL3NjaGVtYXMubWljcm9zb2Z0LmNvbS93cy8yMDA4LzA2L2lkZW50aXR5L2NsYWltcy9yb2xlIjoiQ2xpZW50IiwibmJmIjoxNzYzMDE3NzA0LCJleHAiOjE3NjMwNjA5MDQsImlzcyI6Ikd5bVJlc2VydmF0aW9uIiwiYXVkIjoid3IifQ.2mW0dCg_RCx0fNjJBvKqBFxldxpSO4xTxep4iAZSnxs"


def parse_all_string(cookie_string):
    items = {}
    for item in cookie_string.split(';'):
        key, value = item.strip().split('=', 1)
        items[key] = value
    return items


# 七六五四三、松竹星卓风
# 系统时间是18：00到0点，则查今天和明天
# 系统时间是0点到18点，则仅查今天

def get_appointment_list():
    # 自动获取日期为 YYYY-MM-DD 格式（如需改为明天，将 days 改为 1）
    APPOINTMENT_DATE = (date.today() + timedelta(days=0)).strftime("%Y-%m-%d")
    url_g = "https://gym.whu.edu.cn/api/GSStadiums/GetAppointmentList"
    url_a = "https://gym.whu.edu.cn/api/GSStadiums/GetAppointmentAreaList"
    params_g = {
        "Version": "2",
        "SportsTypeId": "21",
        "AppointmentDate": APPOINTMENT_DATE
    }
    params_as = {
        "Version": "2",
        "StadiumsAreaId": "7",
        "AppointmentDate": APPOINTMENT_DATE
    }
    params_az = {
        "Version": "2",
        "StadiumsAreaId": "6",
        "AppointmentDate": APPOINTMENT_DATE
    }
    params_ax = {
        "Version": "2",
        "StadiumsAreaId": "5",
        "AppointmentDate": APPOINTMENT_DATE
    }
    params_ar = {
        "Version": "2",
        "StadiumsAreaId": "4",
        "AppointmentDate": APPOINTMENT_DATE
    }
    params_af = {
        "Version": "2",
        "StadiumsAreaId": "3",
        "AppointmentDate": APPOINTMENT_DATE
    }

    # 都一样
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf2541211) XWEB/16815',
        'Content-Type': 'application/json',
        'Authorization': TOKEN,
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://gym.whu.edu.cn/hsdsqhafive/pages/index/reserve?typeId=21&title=%E7%BE%BD%E6%AF%9B%E7%90%83%E9%A2%84%E7%BA%A6%E5%88%97%E8%A1%A8',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }

    cookies = parse_all_string(COOKIE)

    try:
        response_g = requests.get(
            url=url_g,
            params=params_g,
            headers=headers,
            cookies=cookies,
            verify=False   # 这一行关闭了证书校验
        )
        
        # 检查请求是否成功
        response_g.raise_for_status()
        
        # 返回JSON数据
        return response_g.json()
        
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None
    except ValueError as e:
        print(f"JSON解析失败: {e}")
        print(f"响应内容: {response_g.text}")
        return None

# "IsCanAppointment": 0 表示 不可预约（无场）
# "IsCanAppointment": 1 表示 可以预约（有场）
# 检查json字段是否存在 "IsCanAppointment": 1， 有则表示有场，返回体育馆、场号、时间段信息

def check_availability(json_data):
    available_slots = []
    stadiums = json_data.get("response", {}).get("data", [])
    # 过滤所有包含“杏林”的场馆（括号/后缀/空格等变体都剔除）
    def _is_xinglin(title: str) -> bool:
        if not isinstance(title, str):
            return False
        t = title.replace('（', '(').replace('）', ')').replace(' ', '')
        return '杏林' in t
    stadiums = [s for s in stadiums if not _is_xinglin(s.get("Title", ""))]
    
    for stadium in stadiums:
        stadium_name = stadium.get("Title", "未知体育馆")
        for time_slot in stadium.get("AppointmentTimes", []):
            if time_slot.get("IsCanAppointment", 0) == 1:
                available_slots.append({
                    "stadium": stadium_name,
                    "time": f"{time_slot['Title']} ({time_slot['StartTime']}-{time_slot['EndTime']})",
                })
    # 双保险：再次过滤（理论上前面已过滤掉）
    available_slots = [slot for slot in available_slots if not _is_xinglin(slot.get("stadium", ""))]
    # 如果有可预约的
    
    return available_slots if available_slots else None



def simple_email_send(to_email, subject, content):
    """最简单的邮件发送函数"""
    from_email = "17712423592@163.com"
    auth_code = "UTxdpey4gT89MeAW"
    
    try:
        # 直接硬编码163邮箱设置
        with smtplib.SMTP_SSL('smtp.163.com', 465, timeout=30) as server:
            server.login(from_email, auth_code)
            
            msg = MIMEText(content, 'plain', 'utf-8')
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = Header(subject, 'utf-8')
            
            server.sendmail(from_email, [to_email], msg.as_string())
        print("✅ 邮件发送成功！")
        return True
    except Exception as e:
        print(f"❌ 发送失败: {e}")
        return False


def send_to_all(subject, content):
    simple_email_send(
        to_email = "171024830@qq.com",
        subject = subject,
        content = content
    )
    simple_email_send(
        to_email = "lxin419@qq.com",
        subject = subject,
        content = content
    )
    simple_email_send(
        to_email = "1577395418@qq.com",
        subject = subject,
        content = content
    )

def send_to_admin(subject, content):
    simple_email_send(
        to_email = "171024830@qq.com",
        subject = subject,
        content = content
    )

last_available_slots = None



def main():
    result = get_appointment_list()
    if result:
        print("json请求成功")
        available_slots = check_availability(result)
        # 维护一个队列，保存上一个状态的available_slots
        # 对比两个状态是否相同，如果不同则发送通知
        global last_available_slots

        # 如果有变化则更新缓存, 发通知
        if available_slots != last_available_slots:
            last_available_slots = available_slots
            print("状态有变化，准备发送通知...")
            if available_slots:
                print("可预约的场次:")
                for slot in available_slots:
                    print(f"体育馆: {slot['stadium']}, 时间: {slot['time']}")
                # 发送邮件通知
                content_lines = [f"体育馆: {slot['stadium']}, 时间: {slot['time']}" for slot in available_slots]
                content = "有可预约的羽毛球场地！\n\n" + "\n".join(content_lines)
                send_to_all(
                    subject = "今天羽毛球有场地啦！快去抢吧！！",
                    content = content
                )

                return True
            else:
                # 没有可预约的场次了，发送邮件通知
                content = "今天羽毛球场地已被抢光！"
                send_to_all(
                    subject = "今天羽毛球场地已被抢光！",
                    content = content
                )

                print("场被抢光了，已发送通知。")
                return True
        else:
            print("状态无变化，不发送通知。")
            return True
    else:
        print("请求失败")
        return None


# 使用函数
if __name__ == "__main__":
    # 每五秒钟检查一次
    # 统计程序开始到结束的运行时间
    # start_time = time.time()
    send_to_admin(
        subject = "羽毛球场地监控程序启动",
        content = "监控程序已启动。"
    )
    while True:
        main()
        time.sleep(5)

    # end_time = time.time()  
    # # 计算时间换算成分钟
    # duration_minutes = (end_time - start_time) / 60
    # send_to_admin(
    #     subject = "羽毛球场地监控程序结束",
    #     content = f"程序运行时间: {duration_minutes:.2f} 分钟"
    # )
    # print(f"程序运行时间: {duration_minutes:.2f} 分钟")