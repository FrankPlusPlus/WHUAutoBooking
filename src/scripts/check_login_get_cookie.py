# 定期检查是否登录，如果没登录就自动登录
# 定时读取cookie字段（），并保存到本地文件，以供monitor.py使用
import requests
import time
import os
import json
from tool.zhlj_automation import open_appointment_page, enum_windows_by_process_name, calculate_absolute_position, human_move_and_click, _human_sleep, open_zhlj_with_path, culculate_zhlj_position




# 检测是否登录，返回True/False            抓https://zhlj.whu.edu.cn/mobile/api/getUser?enc=， enc为空则表示未登录，返回False，否则返回True


# 如果没登录，进行登录（点击方式、模拟输入账号密码），成功返回True，失败返回False，如果已经登录就直接返回True
def login():
    open_zhijia()
    # 点击“我的”按钮
    zhlj_position = culculate_zhlj_position()
    my_button = calculate_absolute_position(zhlj_position, 360, 760)
    human_move_and_click(my_button[0], my_button[1])
    _human_sleep(1.5, 2)  # 等待“我的”界面加载 
    # 输入账号密码并登录                                                               待测量
    username_field = calculate_absolute_position(zhlj_position, 200, 300)
    password_field = calculate_absolute_position(zhlj_position, 200, 400)
    login_button = calculate_absolute_position(zhlj_position, 360, 550)
    human_move_and_click(username_field[0], username_field[1])
    _human_sleep(0.5, 0.8)
    # 输入用户名
    for char in "2025282110283":
        os.system(f'echo {char.strip()}| clip')
        human_move_and_click(username_field[0], username_field[1])
        _human_sleep(0.1, 0.2)
    _human_sleep(0.5, 0.8)

    human_move_and_click(password_field[0], password_field[1])
    _human_sleep(0.5, 0.8)
    # 输入密码
    for char in "St24005X!":
        os.system(f'echo {char.strip()}| clip')
        human_move_and_click(password_field[0], password_field[1])
        _human_sleep(0.1, 0.2)
    _human_sleep(0.5, 0.8)
    human_move_and_click(login_button[0], login_button[1])
    _human_sleep(3, 4)  # 等待登录完成




# 打开智慧珞珈
def open_zhijia():
    zhlj_exe_path = r"D:\快捷方式\智慧珞珈.lnk"
    open_zhlj_with_path(zhlj_exe_path)
    _human_sleep(2, 3)  # 等待智慧珞珈界面加载, 完成操作

def check_and_login():
    # 开启线程开始抓包 抓https://zhlj.whu.edu.cn/mobile/api/getUser，这种前缀的url， enc为空则表示未登录，返回False，否则返回True


    # 执行操作 打开智慧珞珈


    # 抓包成功，关闭抓包线程，检查url的参数部分，enc字段是否为空若为空，则表示未登录，进行登录操作接受登录结果，若非空返回True
    pass
    

    


# 打开抓包监控，抓指定url的消息，抓到后返回请求体的cookie字段， Authorization字段


# 打开智慧珞珈小程序到羽毛球预订页面,  抓https://gym.whu.edu.cn/api/GSStadiums/GetAppointmentList?Version=2&SportsTypeId=21&AppointmentDate=2025-11-12的请求体cookie， 抓到后关闭智慧珞珈程序