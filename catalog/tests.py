# 自动测试

from django.test import TestCase
from django.templatetags.static import static
from django.urls import reverse

from .models import Artist, Comment, Song


class ProjectSkeletonTest(TestCase):
    def test_home_page_exists(self) -> None:
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.view_name, "catalog:song_list")
        self.assertContains(response, "ZFX's Music Site")


class CatalogViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.artist_a = Artist.objects.create(
            name="A歌手",
            prefix="A",
            introduction="歌手简介",
            source_url="https://example.com/artists/a",
            image_url="https://example.com/artists/a.jpg",
        )
        cls.artist_b = Artist.objects.create(
            name="B歌手",
            prefix="B",
            introduction="另一段简介",
            source_url="https://example.com/artists/b",
            image_url="https://example.com/artists/b.jpg",
        )
        for number in range(21):
            Song.objects.create(
                title=f"歌曲{number:02d}",
                artist=cls.artist_a,
                lyrics="第一行歌词\n第二行歌词",
                source_url=f"https://example.com/songs/{number}",
                image_url=f"https://example.com/songs/{number}.jpg",
            )

    def test_song_list_is_paginated(self) -> None:
        response = self.client.get(reverse("catalog:song_list"), {"page": 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["song_list"]), 1)
        self.assertTemplateUsed(response, "catalog/song_list.html")

    def test_song_list_uses_image_cards(self) -> None:
        song = Song.objects.first()
        response = self.client.get(reverse("catalog:song_list"))
        self.assertContains(response, song.image_url)
        self.assertContains(response, 'class="result-card"')
        self.assertContains(
            response,
            reverse("catalog:song_detail", args=[song.id]),
        )
        self.assertNotContains(
            response,
            reverse("catalog:artist_detail", args=[song.artist.id]),
        )

    def test_display_image_url_uses_real_and_default_images(self) -> None:
        song = Song.objects.first()
        self.assertEqual(song.display_image_url, song.image_url)
        self.assertEqual(
            self.artist_a.display_image_url,
            self.artist_a.image_url,
        )

        song.image_url = ""
        self.artist_b.image_url = ""
        self.assertEqual(
            song.display_image_url,
            static("images/default-song.png"),
        )
        self.assertEqual(
            self.artist_b.display_image_url,
            static("images/default-artist.png"),
        )

    def test_pages_display_default_images(self) -> None:
        song = Song.objects.first()
        song.image_url = ""
        song.save()
        self.artist_b.image_url = ""
        self.artist_b.save()

        song_response = self.client.get(
            reverse("catalog:song_detail", args=[song.id])
        )
        artist_response = self.client.get(
            reverse("catalog:artist_list"),
            {"initial": "B"},
        )
        self.assertContains(
            song_response,
            static("images/default-song.png"),
        )
        self.assertContains(
            artist_response,
            static("images/default-artist.png"),
        )

    def test_artist_list_filters_by_initial(self) -> None:
        response = self.client.get(
            reverse("catalog:artist_list"),
            {"initial": "A"},
        )
        self.assertEqual(
            list(response.context["artist_list"]),
            [self.artist_a],
        )
        self.assertEqual(response.context["initial"], "A")
        self.assertTemplateUsed(response, "catalog/artist_list.html")
        self.assertContains(
            response,
            reverse("catalog:artist_detail", args=[self.artist_a.id]),
        )
        self.assertContains(response, self.artist_a.image_url)

    def test_song_detail_displays_required_information(self) -> None:
        song = Song.objects.first()
        comment = Comment.objects.create(song=song, body="测试评论")
        response = self.client.get(
            reverse("catalog:song_detail", args=[song.id])
        )
        self.assertContains(response, song.title)
        self.assertContains(response, song.artist.name)
        self.assertContains(response, song.image_url)
        self.assertContains(response, song.source_url)
        self.assertContains(response, "第一行歌词")
        self.assertContains(response, "测试评论")
        self.assertContains(
            response,
            reverse("catalog:delete_comment", args=[song.id, comment.id]),
        )

    def test_artist_detail_displays_required_information(self) -> None:
        song = Song.objects.first()
        response = self.client.get(
            reverse("catalog:artist_detail", args=[self.artist_a.id])
        )
        self.assertEqual(response.context["artist"], self.artist_a)
        self.assertContains(response, self.artist_a.name)
        self.assertContains(response, self.artist_a.introduction)
        self.assertContains(response, self.artist_a.image_url)
        self.assertContains(response, self.artist_a.source_url)
        self.assertContains(
            response,
            reverse("catalog:song_detail", args=[song.id]),
        )

    def test_song_detail_creates_comment(self) -> None:
        song = Song.objects.first()
        response = self.client.post(
            reverse("catalog:song_detail", args=[song.id]),
            {"body": "一条新评论"},
        )
        self.assertRedirects(
            response,
            reverse("catalog:song_detail", args=[song.id]),
        )
        self.assertTrue(
            Comment.objects.filter(song=song, body="一条新评论").exists()
        )

    def test_delete_comment_accepts_post(self) -> None:
        song = Song.objects.first()
        comment = Comment.objects.create(song=song, body="待删除评论")
        response = self.client.post(
            reverse("catalog:delete_comment", args=[song.id, comment.id])
        )
        self.assertRedirects(
            response,
            reverse("catalog:song_detail", args=[song.id]),
        )
        self.assertFalse(Comment.objects.filter(id=comment.id).exists())

    def test_search_songs_and_paginate_results(self) -> None:
        song = Song.objects.first()
        response = self.client.get(
            reverse("catalog:search"),
            {"query": "第一行", "search_type": "song"},
        )
        self.assertEqual(response.context["result_count"], 21)
        self.assertEqual(response.context["page_obj"].paginator.num_pages, 2)
        self.assertIsNotNone(response.context["elapsed_time"])
        self.assertTemplateUsed(response, "catalog/search.html")
        self.assertContains(response, song.image_url)
        self.assertContains(
            response,
            reverse("catalog:song_detail", args=[song.id]),
        )

    def test_search_artists(self) -> None:
        response = self.client.get(
            reverse("catalog:search"),
            {"query": "另一段", "search_type": "artist"},
        )
        self.assertEqual(response.context["result_count"], 1)
        self.assertEqual(list(response.context["page_obj"]), [self.artist_b])
        self.assertContains(response, self.artist_b.image_url)
        self.assertContains(
            response,
            reverse("catalog:artist_detail", args=[self.artist_b.id]),
        )

    def test_search_displays_empty_result(self) -> None:
        response = self.client.get(
            reverse("catalog:search"),
            {"query": "不存在的关键词", "search_type": "song"},
        )
        self.assertEqual(response.context["result_count"], 0)
        self.assertContains(response, "找到 0 条结果")
        self.assertContains(response, "没有找到符合条件的结果")

    def test_song_search_uses_priority_order(self) -> None:
        def make_artist(name: str, slug: str) -> Artist:
            return Artist.objects.create(
                name=name,
                prefix="M",
                introduction="普通简介",
                source_url=f"https://example.com/rank-artists/{slug}",
                image_url=f"https://example.com/rank-artists/{slug}.jpg",
            )

        def make_song(
            title: str,
            artist: Artist,
            slug: str,
            lyrics: str = "普通歌词",
        ) -> Song:
            return Song.objects.create(
                title=title,
                artist=artist,
                lyrics=lyrics,
                source_url=f"https://example.com/rank-songs/{slug}",
                image_url=f"https://example.com/rank-songs/{slug}.jpg",
            )

        other_artist = make_artist("其他歌手", "other")
        exact_artist = make_artist("目标", "exact")
        starts_artist = make_artist("目标乐队", "starts")
        contains_artist = make_artist("超级目标乐队", "contains")

        expected = [
            make_song("目标", other_artist, "1-title-exact"),
            make_song("普通歌曲二", exact_artist, "2-artist-exact"),
            make_song("目标开头歌曲", other_artist, "3-title-starts"),
            make_song("包含目标歌曲", other_artist, "4-title-contains"),
            make_song("普通歌曲五", starts_artist, "5-artist-starts"),
            make_song("普通歌曲六", contains_artist, "6-artist-contains"),
            make_song(
                "普通歌曲七",
                other_artist,
                "7-lyrics-contains",
                lyrics="这段歌词包含目标",
            ),
        ]

        response = self.client.get(
            reverse("catalog:search"),
            {"query": "目标", "search_type": "song"},
        )
        self.assertEqual(list(response.context["page_obj"]), expected)

    def test_artist_search_uses_priority_order(self) -> None:
        def make_artist(
            name: str,
            slug: str,
            introduction: str = "普通简介",
        ) -> Artist:
            return Artist.objects.create(
                name=name,
                prefix="M",
                introduction=introduction,
                source_url=f"https://example.com/artist-rank/{slug}",
                image_url=f"https://example.com/artist-rank/{slug}.jpg",
            )

        expected = [
            make_artist("目标", "1-name-exact"),
            make_artist("目标组合", "2-name-starts"),
            make_artist("超级目标组合", "3-name-contains"),
            make_artist("其他艺人", "4-introduction", "简介包含目标"),
        ]

        response = self.client.get(
            reverse("catalog:search"),
            {"query": "目标", "search_type": "artist"},
        )
        self.assertEqual(list(response.context["page_obj"]), expected)
