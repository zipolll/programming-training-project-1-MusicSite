"""酷我音乐具体爬取过程"""

from urllib.parse import urlencode
from pypinyin import lazy_pinyin
from .config import (
    ARTISTS_PER_PAGE,
    COMMENTS_PER_SONG,
    KUWO_ARTIST_INFO_URL,
    KUWO_ARTIST_LIST_URL,
    KUWO_COMMENT_URL,
    KUWO_LYRIC_URL,
    KUWO_RAW_DATA_DIR,
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
    song_item: dict,
    artist_id: str,
) -> dict:
    """取得一首歌曲的歌词和热门评论。"""
    song_id = str(song_item["rid"])

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
        song_item,
        lyric_data,
        comment_data,
        artist_id,
    )

def crawl_artist_info(artist_id: str, prefix: str) -> dict:
    """使用歌手 ID 取得基本资料。"""
    info_url = KUWO_ARTIST_INFO_URL.format(artist_id=artist_id)
    info_cache = KUWO_RAW_DATA_DIR / "artists" / f"{artist_id}_info.html"
    info_html = fetch(info_url, info_cache)

    artist = parse_artist(artist_id, info_html)

    if not prefix and artist["name"]:
        prefix = lazy_pinyin(artist["name"])[0][0].upper() # 便于指定url爬取模式下更新首字母
    artist["prefix"] = prefix
    return artist

def crawl_artist_songs(
    artist_id: str,
    saved_song_ids: set[str],
) -> list[dict]:
    """取得一位歌手最多十首有效歌曲。"""
    artist_songs = []
    song_page = 1

    while len(artist_songs) < SONGS_PER_ARTIST:
        # 获取歌手的歌曲清单
        parameters = urlencode(
            {
                "artistid": artist_id,
                "pn": song_page,
                "rn": SONGS_PER_PAGE,
                "httpsStatus": 1,
            }
        )
        song_list_url = KUWO_SONG_LIST_URL + "?" + parameters
        song_list_cache = (
            KUWO_RAW_DATA_DIR
            / "song_lists"
            / f"{artist_id}_{song_page}_artist_music.json"
        )
        song_list_data = fetch(song_list_url, song_list_cache)

        # 爬取每首歌曲
        song_items = song_list_data["data"]["list"] or []
        if not song_items:
            break
        for item in song_items:
            song_id = str(item["rid"])
            if song_id in saved_song_ids:
                continue
            song = crawl_song(item, artist_id)
            if song["title"] and song["lyrics"]:
                artist_songs.append(song)
            if len(artist_songs) == SONGS_PER_ARTIST:
                break
    
        if len(song_items) < SONGS_PER_PAGE:
            break # 歌曲数量已不足
        song_page += 1
    return artist_songs
