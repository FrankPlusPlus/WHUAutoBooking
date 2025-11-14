import yaml
from typing import Dict, Any

# 输入ymal路径，读取token、cookie_str、referer等
def load_config(path: str = "config/data_config.yaml") -> Dict[str, Any]:
    with open(path, 'r', encoding='utf-8') as file:
        cfg = yaml.safe_load(file)
    return cfg