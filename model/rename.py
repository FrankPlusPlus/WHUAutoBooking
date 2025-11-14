from ultralytics import YOLO

# 加载训练好的模型
model = YOLO(r"model\best.pt")

# 修改标签名（注意：顺序必须和原始一致）
model.model.names = ['E', 'e', 'sphere', 'circular', 'A', 'cone', 'diamond', 'square', 'q', 'five-pointed_star', 'd', 'J', 'N', 'cylinder', 'rectangle', 'parallelogram', 'j', 'B', 'fillet_rectangle', 'D', 'n', 'triangle', 'H', 'cube', 'pentagon', 'y', 'f', 'hexagon', 'F', 'R', 'h', 'M', 'trapezoid', 'g', 'Y', 'b', 'Q', 'r', 'T', 'm', 'i', 'a', 't', 'G', 'L']

# 保存为新的权重文件
model.save("best_renamed.pt")