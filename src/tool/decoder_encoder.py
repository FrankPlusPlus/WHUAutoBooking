import random
import time




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
    return dx_url, aid


# 构造ac参数 用到信息很多：目标点坐标、
def construct_ac_param(x: int, y: int, cookies: dict):
    # 静态参数
    ak = '635a429a5f66919cef86083594bdd722'
    