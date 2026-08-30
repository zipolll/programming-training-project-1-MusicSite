import unittest

from analysis.data_utils import clean_lyrics
from analysis.person_perspective import count_persons
from analysis.theme_cooccurrence import detect_themes


class AnalyzeTest(unittest.TestCase):
    def test_clean_lyrics(self):
        lyrics = "歌曲名\n作词：张三\n第一句歌词"
        metadata, real_lyrics = clean_lyrics("歌曲名", lyrics)

        self.assertEqual(metadata, ["歌曲名", "作词：张三"])
        self.assertEqual(real_lyrics, ["第一句歌词"])

    def test_count_persons(self):
        result = count_persons("我喜欢你")
        self.assertEqual(result["第一人称"], 1)
        self.assertEqual(result["第二人称"], 1)

    def test_detect_themes(self):
        result = detect_themes("回忆让我难过")
        self.assertTrue(result["回忆"])
        self.assertTrue(result["悲伤"])


if __name__ == "__main__":
    unittest.main()
