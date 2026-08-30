"""控制酷我音乐爬取流程。"""

import re
from urllib.parse import parse_qs, urlparse

from catalog.models import Artist, Song
from crawler.config import TARGET_ARTIST_COUNT, TARGET_SONG_COUNT
from crawler.crawl_process import (
    crawl_artist_info,
    crawl_artist_songs,
    crawl_artist_queue,
)
from crawler.storage import get_saved_ids, save_artist


def get_single_artist_id(artist_url: str) -> str:
    """从酷我歌手主页 URL 中提取歌手 ID。"""
    parsed_url = urlparse(artist_url) # 用于拆分解析 URL
    query_id = parse_qs(parsed_url.query).get("id", [""])[0]
    path_match = re.search(r"/(\d+)/?$", parsed_url.path)

    if query_id.isdigit():
        return query_id
    if path_match:
        return path_match.group(1)
    return ""


def main() -> None:
    """根据用户输入运行单个歌手或完整断点续爬流程。"""
    completed_artist_ids, saved_song_ids = get_saved_ids()
    artist_count = Artist.objects.count()
    song_count = Song.objects.count()

    artist_url = input(
        "请输入酷我歌手主页 URL，直接回车则继续完整爬取: "
    ).strip()
    single_artist_id = ""

    if artist_url:
        single_artist_id = get_single_artist_id(artist_url)
        if not single_artist_id:
            print("无法从 URL 中找到歌手 ID。")
            return
        if single_artist_id in completed_artist_ids:
            print("数据库中已经存在这位歌手，请直接在网站中查看。")
            return
    elif (
        artist_count >= TARGET_ARTIST_COUNT
        and song_count >= TARGET_SONG_COUNT
    ):
        print("数据库中的歌手和歌曲数量已经达到目标。")
        return

    try:
        artist_page = 1
        stop_crawling = False
        single_artist_saved = False

        while not stop_crawling:
            if single_artist_id:
                artist_queue = [("", single_artist_id)]
            else:
                artist_queue = crawl_artist_queue(artist_page)

            if not artist_queue:
                break

            for prefix, current_artist_id in artist_queue:
                if current_artist_id in completed_artist_ids:
                    continue

                artist_data = crawl_artist_info(current_artist_id, prefix)
                artist_songs = crawl_artist_songs(
                    current_artist_id,
                    saved_song_ids,
                )

                if (
                    artist_data["name"]
                    and artist_data["introduction"]
                    and artist_songs
                ):
                    save_artist(artist_data, artist_songs)
                    completed_artist_ids.add(current_artist_id)
                    for song in artist_songs:
                        saved_song_ids.add(song["external_id"])
                    artist_count += 1
                    song_count += len(artist_songs)
                    single_artist_saved = True
                    print(
                        f"已保存 {artist_data['name']}: "
                        f"{len(artist_songs)} 首，"
                        f"当前共 {artist_count} 位歌手、"
                        f"{song_count} 首歌曲"
                    )
                else:
                    print(
                        f"跳过信息不完整的歌手 ID: "
                        f"{current_artist_id}"
                    )

                if single_artist_id:
                    stop_crawling = True
                    break

                if (
                    artist_page > 1
                    and artist_count >= TARGET_ARTIST_COUNT
                    and song_count >= TARGET_SONG_COUNT
                ):
                    stop_crawling = True
                    break

            if single_artist_id or stop_crawling:
                break

            if (
                artist_count >= TARGET_ARTIST_COUNT
                and song_count >= TARGET_SONG_COUNT
            ):
                break

            artist_page += 1

    except KeyboardInterrupt:
        print(
            "\n爬取已停止，完整数据已保存在数据库中，"
            "未完成请求可以从缓存继续。"
        )
        return

    if single_artist_id:
        if single_artist_saved:
            print("保存成功，请在网站中查看这位歌手。")
        return

    print(f"歌手: {artist_count}/{TARGET_ARTIST_COUNT}")
    print(f"歌曲: {song_count}/{TARGET_SONG_COUNT}")
