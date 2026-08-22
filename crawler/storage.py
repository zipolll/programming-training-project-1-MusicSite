# 保存和读取爬虫进度

import json
from pathlib import Path


def load_json(input_path: Path) -> dict:
    """读取已经加工过的JSON数据；第一次运行时返回空"""
    if not input_path.exists():
        return {
            "completed_artist_ids": [],
            "artists": [],
            "songs": [],
        }

    with input_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json(data: dict, output_path: Path) -> None:
    """将数据和爬取进度保存为JSON。"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_suffix(".tmp") # 先将数据写入临时文件
    with temporary_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    temporary_path.replace(output_path)
