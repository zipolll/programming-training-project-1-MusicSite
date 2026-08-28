"""定义歌手、歌曲、评论3类模型"""
from django.utils import timezone
from django.db import models
from django.templatetags.static import static


class Artist(models.Model):
    name = models.CharField(max_length=200, db_index=True) # 为数据创建索引，加快查找
    prefix = models.CharField(max_length=1)
    introduction = models.TextField(blank=True)
    source_url = models.URLField(max_length=1000, unique=True) # 不允许出现相同的个人主页链接
    image_url = models.URLField(max_length=1000, blank=True)

    class Meta:
        ordering = ["prefix", "name", "id"] # 指定排序依据

    @property
    def display_image_url(self) -> str:
        return self.image_url or static("images/default-artist.png")

    def __str__(self) -> str:
        return self.name


class Song(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    artist = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE, # 级联删除
        related_name="songs",# 反向查询
    )
    lyrics = models.TextField()
    source_url = models.URLField(max_length=1000, unique=True)
    image_url = models.URLField(max_length=1000, blank=True)

    class Meta:
        ordering = ["title", "id"]

    @property
    def display_image_url(self) -> str:
        return self.image_url or static("images/default-song.png")

    def __str__(self) -> str:
        return f"{self.title} - {self.artist.name}"


class Comment(models.Model):
    song = models.ForeignKey(
        Song,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    body = models.TextField()
    created_at = models.DateTimeField(default=timezone.now) # 便于导入之前爬取到的评论

    class Meta:
        ordering = ["-created_at"] # 降序排列，保证最新评论最靠前

    # 对象简略显示时只取前30个字符
    def __str__(self) -> str:
        if len(self.body) > 30:
            return self.body[:30] + "..."
        return self.body
