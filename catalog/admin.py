"""把歌手、歌曲和评论注册到 Django 自带的后台，方便调试"""

from django.contrib import admin
from .models import Artist, Comment, Song


admin.site.register(Artist)
admin.site.register(Song)
admin.site.register(Comment)

