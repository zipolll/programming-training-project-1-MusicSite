#负责根据地址找到对应函数。

from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.song_list, name="song_list"),
    path("songs/<int:song_id>/", views.song_detail, name="song_detail"),
    path(
        "songs/<int:song_id>/comments/<int:comment_id>/delete/",
        views.delete_comment,
        name="delete_comment",
    ),
    path("artists/", views.artist_list, name="artist_list"),
    path(
        "artists/<int:artist_id>/",
        views.artist_detail,
        name="artist_detail",
    ),
    path("search/", views.search, name="search"),
]
