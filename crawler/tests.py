import unittest

from crawler.crawl import get_single_artist_id
from crawler.parse import parse_artist, parse_song


class CrawlerTest(unittest.TestCase):
    def test_get_artist_id(self):
        url = "https://www.kuwo.cn/singer_detail/336"
        self.assertEqual(get_single_artist_id(url), "336")

    def test_parse_artist(self):
        html = '<p class="name_out"><span class="name">测试歌手</span></p>'
        artist = parse_artist("1", html)
        self.assertEqual(artist["name"], "测试歌手")

    def test_parse_song(self):
        song = {"rid": "1", "name": "测试歌曲", "pic": ""}
        lyrics = {"data": {"lrclist": [{"lineLyric": "第一句"}]}}
        comments = {"rows": []}

        result = parse_song(song, lyrics, comments, "1")
        self.assertEqual(result["title"], "测试歌曲")
        self.assertEqual(result["lyrics"], "第一句")


if __name__ == "__main__":
    unittest.main()
