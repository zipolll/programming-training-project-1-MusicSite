# 定义歌手、歌曲、评论3类模型

from django.db import models


class Artist(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    introduction = models.TextField(blank=True)
    source_url = models.URLField(max_length=1000, unique=True)
    image = models.FileField(upload_to="artists/", blank=True)

    def __str__(self) -> str:
        return self.name


class Song(models.Model):
    title = models.CharField(max_length=300, db_index=True)
    artist = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE,
        related_name="songs",
    )
    lyrics = models.TextField()
    source_url = models.URLField(max_length=1000, unique=True)
    image = models.FileField(upload_to="songs/", blank=True)

    def __str__(self) -> str:
        return f"{self.title} - {self.artist.name}"


class Comment(models.Model):
    song = models.ForeignKey(
        Song,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    body = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.body[:30]

