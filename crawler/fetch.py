"""下载器"""

import json
import random
import time
from pathlib import Path

import requests
from fake_useragent import UserAgent

from .config import (
    MAX_REQUEST_INTERVAL_SECONDS,
    MIN_REQUEST_INTERVAL_SECONDS,
    REQUEST_TIMEOUT_SECONDS,
)


def fetch(url: str, cache_path: Path) -> dict | str:
    """ 优先读取缓存，没有缓存时再访问网页。"""
    if cache_path.exists():
        if cache_path.suffix == ".json": # 取得文件扩展名
            with cache_path.open("r", encoding="utf-8") as file:
                return json.load(file) # 将 JSON 文件内容解析为 Python 对象并返回
        return cache_path.read_text(encoding="utf-8") # 以str的形式一次性读取文件的全部内容。

    # 不在缓存中，进入网络请求阶段
    wait_seconds = random.uniform(
        MIN_REQUEST_INTERVAL_SECONDS,
        MAX_REQUEST_INTERVAL_SECONDS,
    )
    time.sleep(wait_seconds)

    headers = {"User-Agent": UserAgent(platforms="desktop").random} # 使用随机 User-Agent 模拟浏览器请求
    response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status() # 如果响应状态码不是 200，则抛出异常

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    if cache_path.suffix == ".json":
        data = response.json() # 将 JSON 响应内容解析为 Python 对象
        with cache_path.open("w", encoding="utf-8") as file: # 以写入模式打开文件，如果文件不存在则创建新文件
            json.dump(data, file, ensure_ascii=False, indent=2) # 将 Python 对象 data 序列化为 JSON 格式，并直接写入刚才打开的 file 中
        return data

    # 不是 JSON 文件（则应该是html），直接保存为文本文件
    response.encoding = "utf-8"
    cache_path.write_text(response.text, encoding="utf-8")
    return response.text
