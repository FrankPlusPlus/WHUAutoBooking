# ...existing code...
from ultralytics import YOLO
import os
import numpy as np
from PIL import Image

def load_pt_model(model_path: str = "model/best.pt"):
    """加载并返回 Ultralytics YOLO 模型对象（会缓存返回的模型由调用方保存复用）。"""
    return YOLO(model_path)

def _sample_region_color(img_rgb: Image.Image, cx: float, cy: float, radius: int = 1):
    """在 RGB PIL 图上以中心(cx,cy)采样 radius 窗口的平均颜色，返回 (r,g,b) ints."""
    arr = np.array(img_rgb)  # H,W,3
    h, w = arr.shape[:2]
    ix = int(round(cx))
    iy = int(round(cy))
    x0 = max(0, ix - radius)
    x1 = min(w, ix + radius + 1)
    y0 = max(0, iy - radius)
    y1 = min(h, iy + radius + 1)
    patch = arr[y0:y1, x0:x1]
    if patch.size == 0:
        return (0, 0, 0)
    mean = patch.reshape(-1, patch.shape[-1]).mean(axis=0)
    return tuple(int(v) for v in mean)

def detect_from_pil_pt(pil_image: Image.Image,
                       model_or_path = "model/best.pt",
                       conf: float = 0.25,
                       iou: float = 0.45,
                       class_names: list | None = None,
                       color_radius: int = 1):
    """
    使用 Ultralytics .pt 模型对单张 PIL.Image 进行检测。
    参数:
      pil_image: PIL.Image（任意尺寸，例如 300x150），函数内部会转 RGB。
      model_or_path: YOLO 模型路径或已加载的 YOLO 对象（YOLO(...)）。
      conf: 置信度阈值
      iou: NMS iou 阈值
      class_names: 可选 list，把 class id 映射为名称；如果为 None，会使用 model.names（若可用）
      color_radius: 中心颜色采样半径（radius=1 表示 3x3 区域平均）
    返回:
      list of dict, 每个 dict 包含:
        {
          'class_id': int,
          'class_name': str or None,
          'score': float,
          'center': (cx, cy),   # 原图像像素坐标（float）
          'color': (r,g,b)      # 中心区域平均颜色，tuple ints
        }
    """
    # 确保 RGB
    img_rgb = pil_image.convert("RGB")
    orig_w, orig_h = img_rgb.size

    # 加载或复用模型
    if hasattr(model_or_path, "predict") or hasattr(model_or_path, "model"):
        model = model_or_path
    else:
        model = load_pt_model(str(model_or_path))

    # 如果没有传 class_names，尝试从模型读取
    if class_names is None:
        try:
            class_names = getattr(model, "names", None)
        except Exception:
            class_names = None

    # Ultralytics: 使用 model.predict 或 直接 model(img) 运行推理
    # 传入参数 conf、iou 来控制后处理
    results = model(img_rgb, conf=conf, iou=iou)  # 返回 Results 对象列表（对单张图取 results[0]）
    if not results:
        return []

    res = results[0]  # 单张图结果
    boxes = []
    scores = []
    cls_ids = []

    # 兼容不同 ultralytics 版本的属性访问
    try:
        # 新版本：res.boxes.xyxy, res.boxes.conf, res.boxes.cls (可能为 tensor)
        xyxy = res.boxes.xyxy.cpu().numpy() if hasattr(res.boxes.xyxy, "cpu") else np.asarray(res.boxes.xyxy)
        confs = res.boxes.conf.cpu().numpy() if hasattr(res.boxes.conf, "cpu") else np.asarray(res.boxes.conf)
        cls = res.boxes.cls.cpu().numpy() if hasattr(res.boxes.cls, "cpu") else np.asarray(res.boxes.cls)
        boxes = xyxy
        scores = confs
        cls_ids = cls
    except Exception:
        # 备用：部分版本可能用 res.boxes.data 或 res.boxes.numpy()
        try:
            data = res.boxes.data  # shape (N,6) xyxy conf cls
            arr = data.cpu().numpy() if hasattr(data, "cpu") else np.asarray(data)
            if arr.shape[1] >= 6:
                boxes = arr[:, :4]
                scores = arr[:, 4]
                cls_ids = arr[:, 5].astype(np.int32)
            else:
                # 无法解析，返回空
                return []
        except Exception:
            return []

    # 组装返回
    results_out = []
    for (x1, y1, x2, y2), s, cid in zip(boxes, scores, cls_ids):
        cx = float((x1 + x2) / 2.0)
        cy = float((y1 + y2) / 2.0)
        color = _sample_region_color(img_rgb, cx, cy, radius=color_radius)
        name = None
        try:
            cid_int = int(cid)
            if class_names and 0 <= cid_int < len(class_names):
                name = class_names[cid_int]
        except Exception:
            # 如果 cid 本身就是字符串/名字
            name = str(cid)
            cid_int = None
        results_out.append({
            'class_id': int(cid) if isinstance(cid, (int, np.integer, np.floating)) else None,
            'class_name': name,
            'score': float(s),
            'center': (cx, cy),
            'color': color
        })
    return results_out

# 使用示例（在别的模块中）
# from model.pt_infer import load_pt_model, detect_from_pil_pt
# model = load_pt_model("model/best.pt")
# results = detect_from_pil_pt(img, model, conf=0.25)
# for r in results: print(r)