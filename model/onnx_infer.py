#!/usr/bin/env python3
"""
ONNX runtime inference (no ultralytics). 
- 适用于 Ultralytics 导出的标准 YOLO ONNX（如果导出未包含 NMS，则需要本脚本的 NMS）
- 需要你确认 model.onnx 的输出含义（本脚本假设输出为 boxes+scores+cls 或一个 detections 格式）
"""

import onnxruntime as ort
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def letterbox(im, new_size=320, color=(114,114,114)):
    # 等比缩放并 pad 到 new_size x new_size
    w, h = im.size
    scale = min(new_size / w, new_size / h)
    nw, nh = int(round(w * scale)), int(round(h * scale))
    im_resized = im.resize((nw, nh), Image.BILINEAR)
    new_im = Image.new('RGB', (new_size, new_size), color)
    pad_x = (new_size - nw) // 2
    pad_y = (new_size - nh) // 2
    new_im.paste(im_resized, (pad_x, pad_y))
    return new_im, scale, pad_x, pad_y

def preprocess_image(img_path, input_size=320):
    im = Image.open(img_path).convert('RGB')
    orig_w, orig_h = im.size
    img_letter, scale, pad_x, pad_y = letterbox(im, new_size=input_size)
    arr = np.array(img_letter).astype('float32') / 255.0
    # HWC -> NCHW
    arr = arr.transpose(2,0,1)[None, ...]
    return arr, (orig_w, orig_h, scale, pad_x, pad_y), im

def nms(boxes, scores, iou_threshold=0.45):
    # boxes: (N,4) xyxy, scores: (N,)
    idxs = scores.argsort()[::-1]
    keep = []
    while idxs.size:
        i = idxs[0]
        keep.append(i)
        if idxs.size == 1:
            break
        rest = idxs[1:]
        xx1 = np.maximum(boxes[i,0], boxes[rest,0])
        yy1 = np.maximum(boxes[i,1], boxes[rest,1])
        xx2 = np.minimum(boxes[i,2], boxes[rest,2])
        yy2 = np.minimum(boxes[i,3], boxes[rest,3])
        w = np.maximum(0.0, xx2 - xx1)
        h = np.maximum(0.0, yy2 - yy1)
        inter = w * h
        area_i = (boxes[i,2]-boxes[i,0])*(boxes[i,3]-boxes[i,1])
        area_rest = (boxes[rest,2]-boxes[rest,0])*(boxes[rest,3]-boxes[rest,1])
        union = area_i + area_rest - inter
        iou = inter / (union + 1e-6)
        idxs = idxs[1:][iou <= iou_threshold]
    return keep

def postprocess_raw(outputs, conf_thres=0.25, iou_thres=0.45):
    # 这个函数要根据 ONNX 的实际输出适当修改
    # 假设 outputs[0] 返回 (1, num_preds, 6) => [x1,y1,x2,y2,score,class]
    out = outputs[0]
    if out.ndim == 3 and out.shape[0] == 1:
        det = out[0]  # (num, 6)
    elif out.ndim == 2 and out.shape[1] >= 6:
        det = out
    else:
        # 不同导出可能需要不同解析：先打印形状检查
        print('Unexpected output shape:', out.shape)
        raise RuntimeError('Cannot parse ONNX output; inspect output names/shapes')
    if det.shape[1] < 6:
        raise RuntimeError('Expected detections with at least 6 values per row')
    boxes = det[:, :4]
    scores = det[:, 4]
    classes = det[:, 5].astype(np.int32)
    mask = scores >= conf_thres
    boxes = boxes[mask]
    scores = scores[mask]
    classes = classes[mask]
    keep = nms(boxes, scores, iou_threshold=iou_thres)
    return boxes[keep], scores[keep], classes[keep]

def map_back_boxes(boxes, orig_w, orig_h, scale, pad_x, pad_y, input_size=320):
    # 把输入坐标（基于 input_size）映回原图坐标
    mapped = []
    for b in boxes:
        x1, y1, x2, y2 = b
        x1 = (x1 - pad_x) / scale
        y1 = (y1 - pad_y) / scale
        x2 = (x2 - pad_x) / scale
        y2 = (y2 - pad_y) / scale
        x1 = max(0, min(orig_w, x1)); y1 = max(0, min(orig_h, y1))
        x2 = max(0, min(orig_w, x2)); y2 = max(0, min(orig_h, y2))
        mapped.append([x1,y1,x2,y2])
    return np.array(mapped)

def draw_and_save(orig_image, boxes, classes, scores, out_path):
    im = orig_image.copy()
    draw = ImageDraw.Draw(im)
    try:
        font = ImageFont.load_default()
    except:
        font = None
    for (x1,y1,x2,y2), c, s in zip(boxes, classes, scores):
        draw.rectangle([x1,y1,x2,y2], outline='red', width=2)
        label = f'{c}:{s:.2f}'
        if font:
            draw.text((x1, y1-10), label, fill='red', font=font)
        else:
            draw.text((x1, y1-10), label, fill='red')
    im.save(out_path)
    print('Saved annotated to', out_path)


def create_ort_session(model_path_or_sess):
        """如果传入已经是 InferenceSession 则直接返回，否则用 model path 创建一个 session。"""
        if hasattr(model_path_or_sess, 'run'):
                return model_path_or_sess
        return ort.InferenceSession(str(model_path_or_sess), providers=['CUDAExecutionProvider','CPUExecutionProvider'])


def detect_from_pil(pil_image, model_or_sess, input_size=320, conf=0.25, iou_thres=0.45, class_names=None):
        """在一个 PIL Image 上运行 ONNX 模型并返回检测结果。

        参数:
            pil_image: PIL.Image (任意尺寸，示例中为 300x150)
            model_or_sess: 路径字符串或已创建的 onnxruntime.InferenceSession
            input_size: 送入模型的短边/方形尺寸（letterbox 中使用）
            conf: 置信度阈值
            iou_thres: NMS IoU 阈值
            class_names: 可选 list，将 class id 映射为名称

        返回值: list of dict，每项包含:
            {
                'class_id': int,
                'class_name': str or None,
                'score': float,
                'center': (cx, cy),  # 原图坐标，float
                'color': (r,g,b)      # 原图中心点像素颜色（tuple）
            }
        """
        # 保证是 RGB
        img = pil_image.convert('RGB')
        orig_w, orig_h = img.size

        # 使用 repository 中的 letterbox/preprocess pattern
        # 复用 letterbox: 它返回 pad 和 scale
        img_letter, scale, pad_x, pad_y = letterbox(img, new_size=input_size)
        arr = np.array(img_letter).astype('float32') / 255.0
        arr = arr.transpose(2,0,1)[None, ...]

        sess = create_ort_session(model_or_sess)
        input_name = sess.get_inputs()[0].name
        outputs = sess.run(None, {input_name: arr})

        # 复用 postprocess_raw/map_back_boxes
        boxes, scores, classes = postprocess_raw(outputs, conf_thres=conf, iou_thres=iou_thres)
        if boxes.size == 0:
                return []

        boxes_orig = map_back_boxes(boxes, orig_w, orig_h, scale, pad_x, pad_y, input_size=input_size)

        results = []
        for b, c, s in zip(boxes_orig, classes, scores):
                x1, y1, x2, y2 = b
                cx = (x1 + x2) / 2.0
                cy = (y1 + y2) / 2.0
                # 保证坐标在图像范围内，用 int 索引像素
                ix = int(max(0, min(orig_w - 1, round(cx))))
                iy = int(max(0, min(orig_h - 1, round(cy))))
                color = img.getpixel((ix, iy))  # returns (R,G,B)
                entry = {
                        'class_id': int(c),
                        'class_name': (class_names[int(c)] if class_names and int(c) < len(class_names) else None),
                        'score': float(s),
                        'center': (float(cx), float(cy)),
                        'color': color
                }
                results.append(entry)
        return results

# def main():
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--model', type=str, required=True)
#     parser.add_argument('--image', type=str, required=True)
#     parser.add_argument('--imgsz', type=int, default=320)
#     parser.add_argument('--conf', type=float, default=0.25)
#     parser.add_argument('--out', type=str, default='runs/detect/onnx_ort_predict')
#     args = parser.parse_args()

#     sess = ort.InferenceSession(args.model, providers=['CUDAExecutionProvider','CPUExecutionProvider'])
#     print('ONNX inputs:', [i.name + str(i.shape) for i in sess.get_inputs()])
#     print('ONNX outputs:', [o.name + str(o.shape) for o in sess.get_outputs()])

#     inp, meta, orig_img = preprocess_image(args.image, input_size=args.imgsz)
#     orig_w, orig_h, scale, pad_x, pad_y = meta
#     input_name = sess.get_inputs()[0].name
#     outputs = sess.run(None, {input_name: inp})
#     # inspect shapes
#     print('Raw outputs shapes:', [o.shape for o in outputs])

#     boxes, scores, classes = postprocess_raw(outputs, conf_thres=args.conf)
#     boxes_orig = map_back_boxes(boxes, orig_w, orig_h, scale, pad_x, pad_y, input_size=args.imgsz)

#     print('Detections (original coords):')
#     for i, (b, c, s) in enumerate(zip(boxes_orig, classes, scores)):
#         x1,y1,x2,y2 = b
#         cx = (x1+x2)/2; cy = (y1+y2)/2
#         print(f'#{i} class={c} score={s:.2f} box=({x1:.1f},{y1:.1f},{x2:.1f},{y2:.1f}) center=({cx:.1f},{cy:.1f})')

#     out_dir = Path(args.out); out_dir.mkdir(parents=True, exist_ok=True)
#     out_path = out_dir / Path(args.image).name
#     draw_and_save(orig_img, boxes_orig, classes, scores, out_path)

