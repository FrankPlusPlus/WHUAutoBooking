import win32gui
import win32process
import psutil
import os
import subprocess
import sys
import time
from time import sleep
import json
from pathlib import Path
import random

def open_zhlj_with_path(zhlj_path: str):
    """使用指定路径打开智慧珞珈小程序或快捷方式。

    在 Windows 上优先使用 os.startfile 来打开 .lnk 快捷方式（等同于双击），
    避免直接用 CreateProcess 去执行非可执行文件导致的 WinError 193。
    对于可执行文件则使用 subprocess.Popen。
    """
    if not os.path.exists(zhlj_path):
        print(f"路径不存在: {zhlj_path}")
        return

    try:
        # Windows: if it's a shortcut (endswith .lnk) or other file handled by shell,
        # use os.startfile which uses ShellExecute and won't raise the 193 error.
        if sys.platform.startswith('win'):
            lower = zhlj_path.lower()
            if lower.endswith('.lnk') or lower.endswith('.url') or not os.access(zhlj_path, os.X_OK):
                try:
                    os.startfile(zhlj_path)
                    print("智慧珞珈小程序已通过 Shell 打开（startfile）。")
                    return
                except Exception:
                    # 如果 startfile 失败，回退到 subprocess（能够捕获更多错误信息）
                    pass

        # 对于可执行程序或在非 Windows 平台，使用 Popen
        subprocess.Popen([zhlj_path])
        print("智慧珞珈小程序已启动（Popen）。")
    except Exception as e:
        print(f"启动失败: {e}")

# 获取智慧珞珈的左上角坐标
def enum_windows_by_process_name(process_name: str = "WeChatAppEx"):
    """返回第一个匹配进程名的顶层窗口句柄和 rect ((left,top),(right,bottom))"""
    target_pids = {p.pid for p in psutil.process_iter(attrs=['name']) if p.info['name'] and process_name.lower() in p.info['name'].lower()}
    result = []
    def _enum(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
        except Exception:
            return
        if pid in target_pids:
            rect = win32gui.GetWindowRect(hwnd)  # (left, top, right, bottom)
            title = win32gui.GetWindowText(hwnd)
            result.append((hwnd, rect, title, pid))
    win32gui.EnumWindows(_enum, None)
    return result

# 用相对坐标和智慧珞珈左上角坐标计算绝对坐标
def calculate_absolute_position(position: tuple, relative_x: int, relative_y: int):
    if position is None:
        return None
    abs_x = position[0] + relative_x
    abs_y = position[1] + relative_y
    return (abs_x, abs_y)

# 点击屏幕坐标
def click_at_position(x: int, y: int):
    try:
        import pyautogui
    except ImportError:
        print("请先安装 pyautogui 库: pip install pyautogui")
        return

    try:
        pyautogui.click(x, y)
        print(f"已点击坐标: ({x}, {y})")
    except Exception as e:
        print(f"点击失败: {e}")


# 轻量“拟人化”工具函数（控制在较小延迟范围内）
def _human_sleep(min_s: float, max_s: float):
    time.sleep(random.uniform(min_s, max_s))


def _jitter_point(x: int, y: int, px: int = 4) -> tuple[int, int]:
    """在 (x,y) 周围加入 ±px 的抖动。"""
    return x + random.randint(-px, px), y + random.randint(-px, px)


def human_move_and_click(x: int, y: int,
                         move_duration: tuple[float, float] = (0.12, 0.28),
                         jitter_px: int = 1,
                         pre_pause: tuple[float, float] = (0.02, 0.06),
                         post_pause: tuple[float, float] = (0.04, 0.10),
                         speed: float = 1.0):
    """以较小随机抖动与非匀速移动到目标并点击，尽量不拉长整体时长。
    - move_duration: 鼠标移动时长范围（秒）
    - jitter_px: 目标点随机抖动像素
    - pre/post_pause: 点击前后的轻微停顿
    - speed: 速度系数，<1 更快，>1 更慢。如 0.6 表示整体时序约 60%（更快）
    """
    try:
        import pyautogui
        from pyautogui import easeInOutQuad, easeOutQuad, easeInQuad, linear
    except Exception:
        # 回退到直接点击
        jx, jy = _jitter_point(x, y, jitter_px)
        return click_at_position(jx, jy)

    # 选择一个简单的缓动函数（不总是同一个）
    tweens = [easeInOutQuad, easeOutQuad, easeInQuad, linear]
    tween = random.choice(tweens)

    # 目标点加入抖动
    jx, jy = _jitter_point(x, y, jitter_px)

    # 偶尔先小幅移动 1 次到接近点（模拟手的微调），概率很低，避免太“设计感”
    if random.random() < 0.25:
        nx, ny = _jitter_point(jx, jy, max(1, jitter_px // 2))
        micro_dur = max(0.01, random.uniform(0.05, 0.12) * speed)
        pyautogui.moveTo(nx, ny, duration=micro_dur, tween=tween)

    main_dur = max(0.01, random.uniform(*move_duration) * speed)
    pyautogui.moveTo(jx, jy, duration=main_dur, tween=tween)
    _human_sleep(max(0.0, pre_pause[0] * speed), max(0.0, pre_pause[1] * speed))
    pyautogui.click(jx, jy)
    print(f"已点击坐标: ({jx}, {jy}) [humanized]")
    _human_sleep(max(0.0, post_pause[0] * speed), max(0.0, post_pause[1] * speed))




# 场馆预约（155，350）
# 羽毛球（65，300）
# 后一天 （360,80）
# 竹园（350，350）

# 将时段建立字典，值为元组坐标
zhuyuan_no = {
    1: (360, 540),
    2: (360, 585),
    3: (360, 630),
    4: (360, 685),
    5: (360, 730)
}

time_slots = {
    (8, 9): (70, 485),
    (9, 10): (200, 485),
    (10, 11): (340, 485),
    (11, 12): (70, 535),
    (12, 13): (200, 535),
    (13, 14): (340, 535),
    (14, 15): (70, 585),
    (15, 16): (200, 585),
    (16, 17): (340, 585),
    (17, 18): (70, 635),
    (18, 19): (200, 635),
    (19, 20): (340, 635),
    (20, 21): (70, 685)
}
# 
# 确定预约（350，755）
# 图片左上角（60，310）


def culculate_zhlj_position() -> tuple[float, float]:
    """获取智慧珞珈窗口左上角坐标"""
    zhlj_position = None
    wins = enum_windows_by_process_name("WeChatAppEx")  # 或主程序名的一部分
    if wins:
        hwnd, rect, title, pid = wins[0]
        left, top, right, bottom = rect
        zhlj_position = (left, top)
        print("窗口左上角：", left, top)
    return zhlj_position



# 这个函数每天17：59：50定时执行
def open_appointment_page():
    """打开场馆预约页面"""
    zhlj_exe_path = r"D:\快捷方式\智慧珞珈.lnk"                                                     # 五点五十的时候执行
    _human_sleep(0.5, 0.8)  # 等待智慧珞珈界面加载（轻微随机）
    open_zhlj_with_path(zhlj_exe_path)
    zhlj_position = culculate_zhlj_position()
    # 先点击场馆预约
    gym_appo = calculate_absolute_position(zhlj_position, 155, 350)
    human_move_and_click(gym_appo[0], gym_appo[1])
    _human_sleep(1.5, 2)  # 等待场馆预约界面加载（缩短但保留冗余）----必要
    # 点击羽毛球or乒乓球
    pingpang_appo = calculate_absolute_position(zhlj_position, 155, 300)
    human_move_and_click(pingpang_appo[0], pingpang_appo[1])
    # badminton_appo = calculate_absolute_position(zhlj_position, 65, 300)
    # human_move_and_click(badminton_appo[0], badminton_appo[1])
    # sleep(1)  # 等待羽毛球乒乓球界面加载


def start_zhlj_automation():
    # 用法
    zhlj_position = culculate_zhlj_position()
    # 预订后一天
    next_day = calculate_absolute_position(zhlj_position, 360, 80)
    timestamp_before_click = time.time()

    click_at_position(next_day[0], next_day[1])  # 这里刚好到六点整执行
    
    # human_move_and_click(next_day[0], next_day[1], speed=0.5)                                                   
    # sleep(0.5)  # 等待界面加载
    zhuyuan_area = calculate_absolute_position(zhlj_position, 350, 350)
    human_move_and_click(zhuyuan_area[0], zhuyuan_area[1], speed=1)                                # 关键问题弹窗不下拉
    _human_sleep(0.08, 0.16)  # 等待下拉界面加载
    # 预订2号场地
    court_2 = calculate_absolute_position(zhlj_position, 360, 585)
    human_move_and_click(court_2[0], court_2[1], speed=1)
    # _human_sleep(0.35, 0.65)  # 等待预约界面加载
    # 预订15-16点
    time_slot_15_16 = calculate_absolute_position(zhlj_position, 70, 685)
    human_move_and_click(time_slot_15_16[0], time_slot_15_16[1], speed=0.5)
    # _human_sleep(0.35, 0.55)  # 等待点击时间完成
    # 确定预约
    confirm_button = calculate_absolute_position(zhlj_position, 350, 755)
    human_move_and_click(confirm_button[0], confirm_button[1], speed=0.5)
    return zhlj_position, timestamp_before_click


if __name__ == "__main__":
    start_zhlj_automation()
