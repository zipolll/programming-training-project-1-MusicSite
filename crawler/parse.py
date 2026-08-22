"""解析并聚合歌手与歌曲数据"""

import re
from bs4 import BeautifulSoup

def parse_artist(artist_id: str, info_html: str) -> dict:
    """从歌手资料页中提取姓名、简介和图片。"""
    info_soup = BeautifulSoup(info_html, "html.parser")

    name_tag = info_soup.select_one(".name_out .name")
    introduction_tag = info_soup.select_one(".child_view > p.info")
    basic_info_tag = info_soup.select_one(".child_view > .list_info")
    image_match = re.search(r'pic300:"([^"]+)"', info_html) # 特殊方式解析图片

    name = (
        " ".join(name_tag.get_text(" ", strip=True).split())
        if name_tag
        else ""
    ) # 处理非换行空格
    introduction = (
        " ".join(introduction_tag.get_text(" ", strip=True).split())
        if introduction_tag
        else ""
    )
    if not introduction and basic_info_tag:
        introduction = " ".join(
            basic_info_tag.get_text(" ", strip=True).split()
        ) # 个人简介为空时使用基本信息。
    image_url = (
        image_match.group(1).replace(r"\u002F", "/")
        if image_match
        else ""
    )

    return {
        "external_id": artist_id,
        "name": name,
        "introduction": introduction,
        "image_url": image_url,
        "source_url": (
            "https://www.kuwo.cn/singer_detail/" + artist_id + "/info"
        ),
    }

def parse_song(
    song_item: dict,
    lyric_data: dict,
    comment_data: dict,
    artist_id: str,
    artist_image_url: str, # 歌曲没有图片时默认采用艺术家的
) -> dict:
    """提取歌曲信息，并将逐行歌词合并成普通文本。"""
    song_id = str(song_item["rid"])
    item = song_item
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

    return {
        "external_id": song_id,
        "title": item.get("name") or "",
        "artist_id": artist_id,
        "album": item.get("album") or "",
        "lyrics": "\n".join(lyric_lines),
        "image_url": item.get("pic") or artist_image_url,
        "source_comments": source_comments,
        "source_url": "https://www.kuwo.cn/play_detail/" + song_id,
    }
