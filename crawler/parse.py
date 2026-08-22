"""解析并聚合歌手与歌曲数据"""

from bs4 import BeautifulSoup


def parse_artist(artist_id: str, detail_html: str, introduction_html: str) -> dict:
    """从歌手主页和资料页中提取歌手信息。"""
    detail_soup = BeautifulSoup(detail_html, "html.parser")
    introduction_soup = BeautifulSoup(introduction_html, "html.parser")

    name_tag = detail_soup.select_one(".ad_name") # 在歌手主页中查找属性为类且名为 ad_name 的第一个元素，确定歌手姓名
    image_tag = detail_soup.select_one(".bannerInfo img")
    introduction_tag = introduction_soup.select_one("#introduce p") # 在歌手介绍页面中，查找 ID 为 introduce 的元素里的第一个 <p> 标签。

    name = name_tag.get_text(strip=True) if name_tag else ""
    image_url = image_tag.get("src", "") if image_tag else "" # 获取src属性的值，如果没有该属性则返回空字符串
    introduction = (
        introduction_tag.get_text(" ", strip=True) if introduction_tag else ""
    )

    return {
        "external_id": artist_id,
        "name": name,
        "introduction": introduction,
        "image_url": image_url,
        "source_url": (
            "https://kuwo.cn/newh5/artist/artistDetail?id=" + artist_id
        ),
    }



def parse_song(
    song_id: str,
    song_info: dict,
    lyric_data: dict,
    comment_data: dict,
    artist_id: str,
    artist_image_url: str, # 歌曲没有图片时默认采用艺术家的
) -> dict:
    """提取歌曲信息，并将逐行歌词合并成普通文本。"""
    item = song_info.get("data") or {}
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
