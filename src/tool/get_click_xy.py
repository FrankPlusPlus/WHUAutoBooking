
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
    'circular': '圆形',
    'triangle': '三角形',
    'square': '正方形',
    'rectangle': '矩形',
    'diamond': '菱形',
    'trapezoid': '梯形',
    'parallelogram': '平行四边形',
    'fillet_rectangle': '圆角矩形',
    'five-pointed_star': '五角星',
    'pentagon': '五边形',
    'hexagon': '六边形',
    'cylinder': '圆柱体',
    'cone': '圆锥',
    'cube': '立方体',
    'sphere': '球',
    'plane': '平面',
    'solid': '立体'
    # 根据实际返回值继续补充
}

COLOR_MAP = {
    'red': '红色',
    'green': '绿色',
    'blue': '蓝色'
}

# 分类字典：平面图形、立体图形、大写字母、小写字母
# 这些字典用于快速判断某个识别标签属于哪一类
PLANE_SHAPES = {
    'circle': IMG_NAME_MAP.get('circular', 'circular'),
    'triangle': IMG_NAME_MAP.get('triangle', 'triangle'),
    'square': IMG_NAME_MAP.get('square', 'square'),
    'rectangle': IMG_NAME_MAP.get('rectangle', 'rectangle'),
    'diamond': IMG_NAME_MAP.get('diamond', 'diamond'),
    'trapezoid': IMG_NAME_MAP.get('trapezoid', 'trapezoid'),
    'parallelogram': IMG_NAME_MAP.get('parallelogram', 'parallelogram'),
    'fillet_rectangle': IMG_NAME_MAP.get('fillet_rectangle', 'fillet_rectangle'),
    'pentagon': IMG_NAME_MAP.get('pentagon', 'pentagon'),
    'hexagon': IMG_NAME_MAP.get('hexagon', 'hexagon'),
    'star': IMG_NAME_MAP.get('five-pointed_star', 'five-pointed_star')
}

SOLID_SHAPES = {
    'sphere': IMG_NAME_MAP.get('sphere', 'sphere'),
    'cylinder': IMG_NAME_MAP.get('cylinder', 'cylinder'),
    'cone': IMG_NAME_MAP.get('cone', 'cone'),
    'cube': IMG_NAME_MAP.get('cube', 'cube')
}

# 大写字母集合（从数据集中出现的单字符大写字母）
UPPERCASE_LETTERS = {
    'A':'A','B':'B','D':'D','E':'E','F':'F','G':'G','H':'H','J':'J','L':'L','M':'M','N':'N','Q':'Q','R':'R','T':'T','Y':'Y'
}

# 小写字母集合（从数据集中出现的单字符小写字母）
LOWERCASE_LETTERS = {
    'a':'a','b':'b','d':'d','e':'e','f':'f','g':'g','h':'h','i':'i','j':'j','m':'m','n':'n','q':'q','r':'r','t':'t','y':'y'
}


def is_plane_shape(token: str) -> bool:
    return token in PLANE_SHAPES


def is_solid_shape(token: str) -> bool:
    return token in SOLID_SHAPES


def is_uppercase_letter(token: str) -> bool:
    return token in UPPERCASE_LETTERS


def is_lowercase_letter(token: str) -> bool:
    return token in LOWERCASE_LETTERS


# 根据三通道如'color': (75, 137, 207)，判断颜色类别
def classify_color(rgb: tuple) -> str:
    r, g, b = rgb
    if r > g and r > b:
        return 'red'
    elif g > r and g > b:
        return 'green'
    elif b > r and b > g:
        return 'blue'
    else:
        return 'unknown'
    
# target_info列表的结构，每个元素是一个字典，格式如下：
# {'class_id': 12, 'class_name': 'N', 'score': 0.9708969593048096, 'center': (251.33108520507812, 86.64856719970703), 'color': (6, 184, 127)}
# {'class_id': 24, 'class_name': 'pentagon', 'score': 0.9681230187416077, 'center': (122.24118041992188, 67.27557373046875), 'color': (214, 77, 64)}
# {'class_id': 25, 'class_name': 'y', 'score': 0.9632507562637329, 'center': (59.89263916015625, 73.8536148071289), 'color': (18, 110, 200)}
# {'class_id': 15, 'class_name': 'parallelogram', 'score': 0.9569453597068787, 'center': (145.49522399902344, 127.75169372558594), 'color': (12, 104, 198)}
# {'class_id': 13, 'class_name': 'cylinder', 'score': 0.9509642720222473, 'center': (62.99717712402344, 122.48347473144531), 'color': (3, 166, 111)}

# 根据验证的id，图像识别的返回标签，返回目标点的对应坐标
def analyze_image_recognition(data, target_info: list) -> tuple:
    """生成验证码图片描述信息"""
    # 从请求tp1_url的响应体中获取关键字段verifyType、childVerifyType、imgName、color、logo等
    verifyType = str(data.get('verifyType', ''))
    childVerifyType = str(data.get('childVerifyType', ''))
    imgName = str(data.get('imgName', ''))
    color = str(data.get('color', ''))
    # 获取字段
    img_ch = IMG_NAME_MAP.get(imgName, imgName)
    color_ch = COLOR_MAP.get(color, color)
    if color_ch == 'None':
        color_ch = ''
    if img_ch == 'None':
        img_ch = ''
    description = ""
    # 根据 verifyType 和 childVerifyType 返回xy
    if verifyType == '0':
        if childVerifyType == '0': # 请点击平面图形---检查哪个图形是属于平面图形，返回其中心坐标OK
#           验证码描述: 请点击绿色的平面图形
#           img_ch=平面不是'plane'或'solid'，无法处理此情况。
            description = f"请点击平面图形"
            print(f"验证码描述: {description}")
            # 逐个检查列表target_info中的'class_name'是否在PLANE_SHAPES中
            for item in target_info:
                if is_plane_shape(item['class_name']):
                    return item['center']

        elif childVerifyType == '1': # 请点击立体图形---检查哪个图形是属于立体图形，返回其中心坐标OK
            description = f"请点击立体图形" 
            print(f"验证码描述: {description}")
            for item in target_info:
                if is_solid_shape(item['class_name']):
                    return item['center']
                
    elif verifyType == '1':
        if childVerifyType == '0': # 请点击指定颜色图形---获取 color_ch 颜色的img_ch类！！图形，返回其中心坐标OK
            description = f"请点击{color_ch}的{img_ch}图形"
            print(f"验证码描述: {description}")
            # 遍历列表target_info，找到符合img_ch且颜色分类为color_ch的图形
            # 这里img_ch特殊，如果img_ch = 'plane'或'solid'，代表它们应属于的类别
            if imgName == 'plane':
                for item in target_info:
                    if is_plane_shape(item['class_name']):
                        col = item.get('color')  # 可能为 None，或 (r,g,b)
                        if col:
                            c = classify_color(col)
                            if c == color:
                                return item['center']
            elif imgName == 'solid':
                for item in target_info:
                    if is_solid_shape(item['class_name']):
                        col = item.get('color')  # 可能为 None，或 (r,g,b)
                        if col:
                            c = classify_color(col)
                            if c == color:
                                return item['center']
            else:
                print(f"img_ch={img_ch}不是'plane'或'solid'，无法处理此情况。")
        elif childVerifyType == '1': # 请点击与指定目标，颜色相同，形状不同的图形（只有两个颜色，）---获取所有 color_ch 的图形，排除 img_ch 图形，返回剩余图形的中心坐标 
            description = f"请点击除{img_ch}外的{color_ch}图形"
            print(f"验证码描述: {description}")
            # 遍历列表target_info，找到所有 color_ch 颜色的图形，排除 img_ch 图形
            for item in target_info:
                if item['class_name'] != imgName: # 这里返回的five-pointed_star其实是
                    col = item.get('color')  # 可能为 None，或 (r,g,b)
                    if col:
                        c = classify_color(col)
                        if c == color:
                            return item['center']
            

    elif verifyType == '2':
        if childVerifyType == '0': # 请点击小写字母OK
            description = f"请点击小写字母"
            print(f"验证码描述: {description}")
            # 逐个检查target_info中的'class_name'是否在LOWERCASE_LETTERS中
            for item in target_info:
                if is_lowercase_letter(item['class_name']):
                    return item['center']

        elif childVerifyType == '1':  # 请点击大写字母OK
            description = f"请点击大写字母"
            print(f"验证码描述: {description}")
            for item in target_info:
                if is_uppercase_letter(item['class_name']):
                    return item['center']

    elif verifyType == '3':
        if childVerifyType == '0': # 请点击离img_ch最近的字母
            description = f"请点击离{img_ch}最近的字母"
            print(f"验证码描述: {description}")
            # 遍历列表target_info，找到img_ch图形的中心坐标
            img_ch_center = None
            for item in target_info:
                if item['class_name'] == imgName:
                    img_ch_center = item['center']
                    break
            if img_ch_center:
                min_distance = float('inf')
                closest_center = None
                for item in target_info:
                    if is_uppercase_letter(item['class_name']) or is_lowercase_letter(item['class_name']):
                        center = item['center']
                        distance = ((center[0] - img_ch_center[0]) ** 2 + (center[1] - img_ch_center[1]) ** 2) ** 0.5
                        if distance < min_distance:
                            min_distance = distance
                            closest_center = center
                if closest_center:
                    return closest_center
        elif childVerifyType == '1': # 请点击img_ch左侧的字母
            description = f"请点击{img_ch}左侧的字母"
            print(f"验证码描述: {description}")
            # 遍历列表target_info，找到img_ch图形的中心坐标
            img_ch_center = None
            for item in target_info:
                if item['class_name'] == imgName:
                    img_ch_center = item['center']
                    break
            # 然后找到所有字母中x坐标小于img_ch_center的，取最右侧的那个
            if img_ch_center:
                candidates = []
                for item in target_info:
                    if is_uppercase_letter(item['class_name']) or is_lowercase_letter(item['class_name']):
                        center = item['center']
                        if center[0] < img_ch_center[0]:
                            candidates.append((center, center[0]))  # (center, x坐标)
                if candidates:
                    # 取x坐标最大的那个
                    closest_center = max(candidates, key=lambda x: x[1])[0]
                    return closest_center
        elif childVerifyType == '2': # 请点击img_ch右侧的字母
            description = f"请点击{img_ch}右侧的字母"
            print(f"验证码描述: {description}")
            # 遍历列表target_info，找到img_ch图形的中心坐标
            img_ch_center = None
            for item in target_info:
                if item['class_name'] == imgName:
                    img_ch_center = item['center']
                    break
            # 然后找到所有字母中x坐标大于img_ch_center的，取最左侧的那个
            if img_ch_center:
                candidates = []
                for item in target_info:
                    if is_uppercase_letter(item['class_name']) or is_lowercase_letter(item['class_name']):
                        center = item['center']
                        if center[0] > img_ch_center[0]:
                            candidates.append((center, center[0]))  # (center, x坐标)
                if candidates:
                    # 取x坐标最小的那个
                    closest_center = min(candidates, key=lambda x: x[1])[0]
                    return closest_center
        elif childVerifyType == '3': # 请点击img_ch上方的字母
            description = f"请点击{img_ch}上方的字母"
            print(f"验证码描述: {description}")
            # 遍历列表target_info，找到img_ch图形的中心坐标
            img_ch_center = None
            for item in target_info:
                if item['class_name'] == imgName:
                    img_ch_center = item['center']
                    break
            # 然后找到所有字母中y坐标小于img_ch_center的，取最下方的那个
            if img_ch_center:
                candidates = []
                for item in target_info:
                    if is_uppercase_letter(item['class_name']) or is_lowercase_letter(item['class_name']):
                        center = item['center']
                        if center[1] < img_ch_center[1]:
                            candidates.append((center, center[1]))  # (center, y坐标)
                if candidates:
                    # 取y坐标最大的那个
                    closest_center = max(candidates, key=lambda x: x[1])[0]
                    return closest_center
        elif childVerifyType == '4': # 请点击img_ch下方的字母
            description = f"请点击{img_ch}下方的字母"
            print(f"验证码描述: {description}")
            # 遍历列表target_info，找到img_ch图形的中心坐标
            img_ch_center = None
            for item in target_info:
                if item['class_name'] == imgName:
                    img_ch_center = item['center']
                    break
            # 然后找到所有字母中y坐标大于img_ch_center的，取最上方的那个
            if img_ch_center:
                candidates = []
                for item in target_info:
                    if is_uppercase_letter(item['class_name']) or is_lowercase_letter(item['class_name']):
                        center = item['center']
                        if center[1] > img_ch_center[1]:
                            candidates.append((center, center[1]))  # (center, y坐标)
                if candidates:
                    # 取y坐标最小的那个
                    closest_center = min(candidates, key=lambda x: x[1])[0]
                    return closest_center

    return None