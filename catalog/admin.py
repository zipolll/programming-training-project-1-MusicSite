"""把歌手、歌曲和评论注册到 Django 自带的后台，方便调试"""

from django.contrib import admin

from .models import Artist, Comment, Song

# 管理员系统中可查询歌手、歌曲
@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ("name", "prefix")
    search_fields = ("name", "introduction")


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ("title", "artist")
    search_fields = ("title", "artist__name", "lyrics")


admin.site.register(Comment)
