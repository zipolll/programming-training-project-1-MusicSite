"""测试网站首页、歌曲详情页和评论提交功能。"""

from django.test import TestCase

from .models import Artist, Comment, Song


class CatalogTest(TestCase):
    def setUp(self) -> None:
        '''设置测试所需的初始数据，包括一个歌手和一首歌曲。'''
        self.artist = Artist.objects.create(
            name="测试歌手",
            prefix="C",
            source_url="https://example.com/artist",
        )
        self.song = Song.objects.create(
            title="测试歌曲",
            artist=self.artist,
            lyrics="测试歌词",
            source_url="https://example.com/song",
        )

    def test_home_page(self) -> None:
        response = self.client.get("/")  # 相当于创建一个虚拟的浏览器请求
        self.assertEqual(response.status_code, 200)

    def test_song_page(self) -> None:
        response = self.client.get("/songs/%s/" % self.song.id)
        self.assertContains(response, "测试歌曲")
        self.assertContains(response, "测试歌手")

    def test_add_comment(self) -> None:
        self.client.post("/songs/%s/" % self.song.id, {"body": "很好听"})
        self.assertEqual(Comment.objects.count(), 1)
