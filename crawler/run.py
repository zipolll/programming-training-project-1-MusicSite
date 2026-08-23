# 酷我音乐爬虫入口

import re
from urllib.parse import parse_qs, urlparse

from .config import (
    KUWO_OUTPUT_PATH,
    SONGS_PER_ARTIST,
    TARGET_ARTIST_COUNT,
    TARGET_SONG_COUNT,
)
from .crawl_process import (
    crawl_artist_info,
    crawl_artist_songs,
    get_artist_queue,
)
from .storage import load_json, save_json


def get_single_artist_id(artist_url: str) -> str:
    """从酷我歌手主页 URL 中提取歌手 ID,辅助实现根据歌手主页url进行爬取的功能"""
    parsed_url = urlparse(artist_url) # 用于拆分解析url
    query_id = parse_qs(parsed_url.query).get("id", [""])[0] #把查询参数字符串转换成字典，并查询第一个值，不存在则使用默认值
    path_match = re.search(r"/(\d+)/?$", parsed_url.path) # 支持如下形式：https://www.kuwo.cn/singer_detail/336

    if query_id.isdigit():
        return query_id
    if path_match:
        return path_match.group(1)
    return ""


def show_artist(data: dict, artist_id: str) -> None:
    """展示指定歌手及其歌曲和评论。"""
    selected_artist = None
    for artist in data["artists"]:
        if str(artist["external_id"]) == artist_id:
            selected_artist = artist
            break

    if not selected_artist:
        print("这位歌手没有可展示的完整数据。")
        return

    selected_songs = [
        song
        for song in data["songs"]
        if str(song["artist_id"]) == artist_id
    ]
    print(f"\n歌手: {selected_artist['name']}")
    print(f"简介: {selected_artist['introduction'][:150]}...") # 超过150字省略
    print(f"图片: {selected_artist['image_url']}")
    print(f"主页: {selected_artist['source_url']}")
    print("歌曲:")
    for song in selected_songs[:SONGS_PER_ARTIST]: # 至多展示10首
        print(f"- {song['title']} ({song['album']})")
        for comment in song["source_comments"]:
            content = comment["content"]
            if len(content) > 15:
                content = content[:15] + "..."
            print(f"{comment['created_at']}-{content}")


def main() -> None:
    """读取断点，并控制单歌手模式或默认完整爬取模式。"""
    data = load_json(KUWO_OUTPUT_PATH) # 把json文件内容解析为Python对象并返回
    completed_artist_ids = {
        str(artist_id) for artist_id in data["completed_artist_ids"]
    } # 不能通过检索来获得，可能加入了仅个人信息但未统计完毕
    saved_song_ids = {str(song["external_id"]) for song in data["songs"]}

    artist_url = input("请输入酷我歌手主页 URL，直接回车则继续完整爬取: ").strip()
    single_artist_id = ""

    if artist_url:
        single_artist_id = get_single_artist_id(artist_url)
        if not single_artist_id:
            print("无法从 URL 中找到歌手 ID。")
            return

    try:
        artist_page = 1
        stop_crawling = False

        while not stop_crawling:
            if single_artist_id:
                artist_queue = [("", single_artist_id)]
            else:
                artist_queue = get_artist_queue(artist_page)

            if not artist_queue:
                break

            for prefix, current_artist_id in artist_queue:
                if current_artist_id in completed_artist_ids:
                    continue

                artist = crawl_artist_info(current_artist_id, prefix)
                artist_songs = crawl_artist_songs(
                    current_artist_id,
                    artist["image_url"],
                    saved_song_ids,
                )

                if (
                    artist["name"]
                    and artist["introduction"]
                    and artist["image_url"]
                    and artist_songs
                ):
                    data["artists"].append(artist)
                    data["songs"].extend(artist_songs)
                    saved_song_ids.update(
                        song["external_id"] for song in artist_songs # 把本次新保存的所有歌曲 ID 加入已保存歌曲集合。
                    )
                    print(
                        f"已保存 {artist['name']}: {len(artist_songs)} 首，"
                        f"当前共 {len(data['artists'])} 位歌手、"
                        f"{len(data['songs'])} 首歌曲"
                    )
                else:
                    print(f"跳过信息不完整的歌手 ID: {current_artist_id}")

                completed_artist_ids.add(current_artist_id)
                data["completed_artist_ids"] = sorted(
                    completed_artist_ids,
                    key=int,
                )
                save_json(data, KUWO_OUTPUT_PATH)

                if single_artist_id:
                    stop_crawling = True
                    break

                if artist_page > 1 and len(data["songs"]) >= TARGET_SONG_COUNT:
                    stop_crawling = True
                    break

            if single_artist_id or stop_crawling:
                break

            if len(data["songs"]) >= TARGET_SONG_COUNT:
                break

            artist_page += 1

    except KeyboardInterrupt: # 处理用户中断爬虫的情况
        save_json(data, KUWO_OUTPUT_PATH)
        print("\n爬取已停止，已完成的歌手和缓存均已保存，重新运行程序即可从断点继续。")
        return

    if single_artist_id:
        show_artist(data, single_artist_id)
        return

    print("\n爬取结束")
    print(f"歌手: {len(data['artists'])}/{TARGET_ARTIST_COUNT}")
    print(f"歌曲: {len(data['songs'])}/{TARGET_SONG_COUNT}")
    print(f"结果文件: {KUWO_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
