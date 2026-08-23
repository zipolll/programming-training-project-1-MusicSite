"""负责根据地址找到对应函数。"""

from django.urls import path
from . import views


app_name = "catalog"  # 为这个应用设置 URL 命名空间。

urlpatterns = [
    path("", views.SongListView.as_view(), name="song_list"),
    path(
        "songs/<int:song_id>/",
        views.SongDetailView.as_view(),
        name="song_detail", # 路由别名
    ),
    path(
        "songs/<int:song_id>/comments/<int:comment_id>/delete/",
        views.delete_comment,
        name="delete_comment",
    ),
    path("artists/", views.ArtistListView.as_view(), name="artist_list"),
    path(
        "artists/<int:artist_id>/",
        views.ArtistDetailView.as_view(),
        name="artist_detail",
    ),
    path("search/", views.search, name="search"),
]
