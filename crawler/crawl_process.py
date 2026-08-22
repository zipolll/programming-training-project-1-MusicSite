# 酷我音乐具体爬取过程

from urllib.parse import quote, urlencode

from .config import (
    ARTISTS_PER_PAGE,
    COMMENTS_PER_SONG,
    KUWO_ARTIST_DETAIL_URL,
    KUWO_ARTIST_INTRO_URL,
    KUWO_ARTIST_LIST_URL,
    KUWO_COMMENT_URL,
    KUWO_LYRIC_URL,
    KUWO_RAW_DATA_DIR,
    KUWO_SONG_INFO_URL,
    KUWO_SONG_LIST_URL,
    LETTERS,
    SONGS_PER_ARTIST,
    SONGS_PER_PAGE,
)
from .fetch import fetch
from .parse import parse_artist, parse_song

def get_artist_queue(artist_page: int) -> list[tuple[str, str]]:
    """取得当前页 A-Z 的歌手 ID。"""
    artist_queue = []

    for letter in LETTERS:
        parameters = urlencode(
            {
                "category": 0,
                "prefix": letter,
                "pn": artist_page,
                "rn": ARTISTS_PER_PAGE,
            }
        )
        list_url = KUWO_ARTIST_LIST_URL + "?" + parameters
        list_cache = (
            KUWO_RAW_DATA_DIR
            / "artist_lists"
            / f"{letter}_{artist_page}.json"
        ) # 构造用于存放artist列表的缓存文件路径，同一首字母且同一页的歌手列表会存放在同一个缓存文件中
        list_data = fetch(list_url, list_cache)

        artist_items = list_data["data"]["artistList"] or []
        for item in artist_items:
            artist_queue.append((letter, str(item["id"])))

    return artist_queue


def crawl_song(
    song_id: str,
    artist_id: str,
    artist_image_url: str,
) -> dict:
    """取得一首歌曲的资料、歌词和热门评论。"""
    info_url = KUWO_SONG_INFO_URL + "?" + urlencode({"mid": song_id})
    info_cache = KUWO_RAW_DATA_DIR / "songs" / f"{song_id}_info.json"
    song_info = fetch(info_url, info_cache)

    lyric_url = KUWO_LYRIC_URL + "?" + urlencode({"musicId": song_id})
    lyric_cache = KUWO_RAW_DATA_DIR / "songs" / f"{song_id}_lyrics.json"
    lyric_data = fetch(lyric_url, lyric_cache)

    comment_url = KUWO_COMMENT_URL.format(
    rows=COMMENTS_PER_SONG,
    song_id=song_id,
)
    comment_cache = KUWO_RAW_DATA_DIR / "comments" / f"{song_id}.json"
    comment_data = fetch(comment_url, comment_cache)

    return parse_song(
        song_id,
        song_info,
        lyric_data,
        comment_data,
        artist_id,
        artist_image_url,
    )


def crawl_artist_info(artist_id: str, prefix: str) -> dict:
    """取得一位歌手的基本资料。"""
    detail_url = KUWO_ARTIST_DETAIL_URL.format(artist_id=artist_id)
    detail_cache = KUWO_RAW_DATA_DIR / "artists" / f"{artist_id}_detail.html"
    detail_html = fetch(detail_url, detail_cache)

    # 先获得歌手名字
    basic_artist = parse_artist(artist_id, detail_html, "")
    artist_name = basic_artist["name"]
    # 利用歌手名字获得个人主页url
    introduction_url = KUWO_ARTIST_INTRO_URL.format(
        artist_name=quote(artist_name, safe="")
    )
    introduction_cache = (
        KUWO_RAW_DATA_DIR / "artists" / f"{artist_id}_introduction.html"
    )
    introduction_html = fetch(introduction_url, introduction_cache)

    artist = parse_artist(artist_id, detail_html, introduction_html)
    artist["prefix"] = prefix
    return artist


def crawl_artist_songs(
    artist_id: str,
    artist_image_url: str,
    saved_song_ids: set[str],
) -> list[dict]:
    """取得一位歌手最多十首有效歌曲。"""
    artist_songs = []
    temporary_song_ids = set() # 防止在同一轮中爬取到重复歌曲
    song_page = 1

    while len(artist_songs) < SONGS_PER_ARTIST:
        parameters = urlencode(
            {
                "id": artist_id,
                "pn": song_page,
                "rn": SONGS_PER_PAGE,
            }
        )
        song_list_url = KUWO_SONG_LIST_URL + "?" + parameters
        song_list_cache = (
            KUWO_RAW_DATA_DIR
            / "song_lists"
            / f"{artist_id}_{song_page}.json"
        )
        song_list_data = fetch(song_list_url, song_list_cache)

        song_items = song_list_data["data"]["musicList"] or []
        if not song_items:
            break
        for item in song_items:
            song_id = str(item["id"])
            if song_id in saved_song_ids or song_id in temporary_song_ids:
                continue
            song = crawl_song(song_id, artist_id, artist_image_url)
            if song["title"] and song["lyrics"] and song["image_url"]:
                artist_songs.append(song)
                temporary_song_ids.add(song_id)
            if len(artist_songs) == SONGS_PER_ARTIST:
                break

        if len(song_items) < SONGS_PER_PAGE:
            break # 歌曲数量已不足
        song_page += 1

    return artist_songs
