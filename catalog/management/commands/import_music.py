"""把爬虫生成的 JSON 数据导入 Django 数据库。"""

import json
from datetime import datetime
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from catalog.models import Artist, Comment, Song


class Command(BaseCommand):
    help = "导入 data/processed/kuwo.json 中的歌手、歌曲和评论" # 命令说明

    def handle(self, *args, **options):
        data_path = Path(settings.BASE_DIR) / "data" / "processed" / "kuwo.json"
        if not data_path.exists():
            raise CommandError(f"找不到数据文件：{data_path}")
        with data_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        artist_map = {}
        artist_count = 0
        song_count = 0
        comment_count = 0

        # 更新或创建歌手
        for artist_data in data["artists"]:
            # 根据 source_url 查找歌手；找不到就创建；找到了就使用 defaults 中的数据更新。
            artist, created = Artist.objects.update_or_create(
                source_url=artist_data["source_url"],
                defaults={
                    "name": artist_data["name"],
                    "prefix": artist_data["prefix"],
                    "introduction": artist_data["introduction"],
                    "image_url": artist_data["image_url"],
                },
            )
            artist_map[str(artist_data["external_id"])] = artist
            if created:
                artist_count += 1

        # 更新或创建歌曲
        for song_data in data["songs"]:
            artist = artist_map[str(song_data["artist_id"])]
            song, created = Song.objects.update_or_create(
                source_url=song_data["source_url"],
                defaults={
                    "title": song_data["title"],
                    "artist": artist,
                    "lyrics": song_data["lyrics"],
                    "image_url": song_data["image_url"],
                },
            )
            if created:
                song_count += 1

            # 更新或创建评论
            for comment_data in song_data.get("source_comments", []):
                comment_time = datetime.strptime(
                    comment_data["created_at"],
                    "%Y-%m-%d %H:%M:%S",
                ) # 解析评论时间
                comment_time = timezone.make_aware(comment_time) # 添加时区
                _, created = Comment.objects.get_or_create(
                    song=song,
                    body=comment_data["content"],
                    created_at=comment_time,
                )
                if created:
                    comment_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"导入完成：新增 {artist_count} 位歌手、"
                f"{song_count} 首歌曲、"
                f"{comment_count} 条评论"
            )
        )
