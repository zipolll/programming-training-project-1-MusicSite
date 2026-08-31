"""解析并聚合歌手与歌曲数据。"""

import re
from typing import Any

from bs4 import BeautifulSoup

from .config import KUWO_ARTIST_PAGE_URL


def parse_artist(artist_id: str, info_html: str) -> dict[str, Any]:
    """从歌手资料页中提取姓名、简介和图片。"""
    info_soup = BeautifulSoup(info_html, "html.parser")

    name_tag = info_soup.select_one(".name_out .name")  # 寻找类name_out下的name 类
    # 寻找类child_view下的直接子代p.info标签
    introduction_tag = info_soup.select_one(".child_view > p.info")
    basic_info_tag = info_soup.select_one(".child_view > .list_info")
    # 图片返回格式不够规则，用正则表达式匹配（直接使用img标签会得到默认占位图）
    image_match = re.search(r'pic300:"([^"]+)"', info_html)

    name = (
        " ".join(name_tag.get_text(" ", strip=True).split())
        if name_tag
        else ""
    )  # 处理非换行空格

    introduction = (
        introduction_tag.get_text("\n", strip=True)
        if introduction_tag
        else ""
    )
    if not introduction and basic_info_tag:
        introduction = basic_info_tag.get_text(
            "\n", strip=True
        )  # 个人简介为空时使用基本信息。

    image_url = (
        # 把正则表达式捕获的转义斜杠修复为普通斜杠
        image_match.group(1).replace(r"\u002F", "/")
        if image_match
        else ""
    )
    if image_url.endswith("/"):
        image_url = ""
    return {
        "external_id": artist_id,
        "name": name,
        "introduction": introduction,
        "image_url": image_url,
        "source_url": KUWO_ARTIST_PAGE_URL.format(artist_id=artist_id),
    }


def parse_song(
    song_item: dict[str, Any],
    lyric_data: dict[str, Any],
    comment_data: dict[str, Any],
    artist_id: str,
) -> dict[str, Any]:
    """提取歌曲信息，并将逐行歌词合并成普通文本。"""
    song_id = str(song_item["rid"])
    lyric_items = (lyric_data.get("data") or {}).get("lrclist") or []

    lyric_lines = []
    for line in lyric_items:
        text = (line.get("lineLyric") or "").strip()
        if text:
            lyric_lines.append(text)

    source_comments = []
    for comment in (comment_data.get("rows") or [])[:3]:
        source_comments.append(
            {
                "content": comment.get("msg") or "",
                "created_at": comment.get("time") or "",
            }
        )

    image_url = song_item.get("pic") or ""
    if image_url.endswith("/"):
        image_url = ""  # 图片路径无效时置空
    return {
        "external_id": song_id,
        "title": song_item.get("name") or "",
        "artist_id": artist_id,
        "lyrics": "\n".join(lyric_lines),
        "image_url": image_url,
        "source_comments": source_comments,
        "source_url": "https://www.kuwo.cn/play_detail/" + song_id,
    }
