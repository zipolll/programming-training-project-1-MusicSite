"""读取爬取进度并把爬取结果保存到数据库。"""

from datetime import datetime
from typing import Any

from django.db import transaction
from django.utils import timezone

from catalog.models import Artist, Comment, Song


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


def save_artist(
    artist_data: dict[str, Any],
    artist_songs: list[dict[str, Any]],
) -> None:
    """把一位歌手、歌曲和来源评论完整写入数据库。"""
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
