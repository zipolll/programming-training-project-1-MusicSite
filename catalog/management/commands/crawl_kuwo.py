"""直接把酷我爬虫结果保存到数据库。"""

from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from catalog.models import Artist, Comment, Song
from crawler.config import TARGET_ARTIST_COUNT, TARGET_SONG_COUNT
from crawler.crawl_process import (
    crawl_artist_info,
    crawl_artist_songs,
    get_artist_queue,
    get_single_artist_id,
)


def get_saved_ids() -> tuple[set[str], set[str]]:
    """从数据库来源链接中取得已经保存的酷我 ID。"""
    completed_artist_ids = set()
    for source_url in Artist.objects.values_list("source_url", flat=True):
        artist_id = source_url.rsplit("/", 1)[-1]
        if artist_id.isdigit():
            completed_artist_ids.add(artist_id)

    saved_song_ids = set()
    for source_url in Song.objects.values_list("source_url", flat=True):
        song_id = source_url.rsplit("/", 1)[-1]
        if song_id.isdigit():
            saved_song_ids.add(song_id)

    return completed_artist_ids, saved_song_ids


def save_artist(artist_data: dict, artist_songs: list[dict]) -> None:
    """把一位歌手、歌曲和来源评论完整写入数据库。"""
    # 使用数据库事务确保歌手及其歌曲和评论的一次性写入。
    with transaction.atomic():
        artist, _ = Artist.objects.update_or_create(
            source_url=artist_data["source_url"],
            defaults={
                "name": artist_data["name"],
                "prefix": artist_data["prefix"],
                "introduction": artist_data["introduction"],
                "image_url": artist_data["image_url"],
            },
        )

        for song_data in artist_songs:
            song, _ = Song.objects.update_or_create(
                source_url=song_data["source_url"],
                defaults={
                    "title": song_data["title"],
                    "artist": artist,
                    "lyrics": song_data["lyrics"],
                    "image_url": song_data["image_url"],
                },
            )

            for comment_data in song_data["source_comments"]:
                comment_time = datetime.strptime(
                    comment_data["created_at"],
                    "%Y-%m-%d %H:%M:%S",
                )
                comment_time = timezone.make_aware(comment_time)
                Comment.objects.get_or_create(
                    song=song,
                    body=comment_data["content"],
                    created_at=comment_time,
                )


class Command(BaseCommand):
    help = "爬取酷我音乐数据并直接保存到数据库"

    def handle(self, *args, **options):
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
                    artist_queue = get_artist_queue(artist_page)

                if not artist_queue:
                    break

                for prefix, current_artist_id in artist_queue:
                    if current_artist_id in completed_artist_ids:
                        continue

                    artist_data = crawl_artist_info(
                        current_artist_id,
                        prefix,
                    )
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

        print("\n爬取结束")
        print(f"歌手: {artist_count}/{TARGET_ARTIST_COUNT}")
        print(f"歌曲: {song_count}/{TARGET_SONG_COUNT}")
