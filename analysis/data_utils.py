"""三个分析模块共同使用的数据读取、清洗和筛选函数。"""

import re
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "analysis" / "output"

# 歌名、词曲作者、制作人员等元数据行。
METADATA_LINE = re.compile(
    r"^("
    r"词|作词|曲|作曲|编曲|制作人|监制|配唱|Lyrics by|Composed by|Composer|"
    r"吉他|贝斯|鼓|弦乐|键盘|"
    r"录音|录音师|录音室|混音|混音师|混音录音室|母带|"
    r"歌手|合声|和声|"
    r"音乐总监|出品|发行|企划|统筹|版权|OP|SP|"
    r"Lyrics by|Composed by|Composer|Arranger|Producer|Program"
    r")\s*[:：]",
    re.IGNORECASE,
)

PURE_MUSIC_MARKERS = (
    "纯音乐",
    "伴奏",
    "无歌词",
    "暂无填词",
    "dj舞曲",
    "instrumental",
)


def clean_lyrics(title: str, lyrics: str) -> tuple[list[str], list[str]]:
    """返回元数据行和真正的歌词行。"""
    metadata = []
    real_lyrics = []
    is_first_valid_line = True

    for line in lyrics.splitlines():
        line = " ".join(line.strip().split())
        if not line:
            continue

        if is_first_valid_line and (title in line or " - " in line):
            metadata.append(line)
        elif METADATA_LINE.match(line):
            metadata.append(line)
        else:
            real_lyrics.append(line)
        is_first_valid_line = False

    return metadata, real_lyrics


def load_data() -> pd.DataFrame:
    """使用Django ORM读取歌曲和歌手的基础字段。"""
    from catalog.models import Song

    columns = ["id", "title", "lyrics", "artist_id", "artist__name"]
    songs = Song.objects.order_by("id").values(*columns)
    return pd.DataFrame.from_records(songs, columns=columns).rename(
        columns={"id": "song_id", "artist__name": "artist_name"}
    )

def is_valid(row: pd.Series) -> bool:
    """判断一首歌是否满足公共分析条件。"""
    lines = row["real_lyrics"]
    lyrics_text = "".join(lines).lower().replace(" ", "")
    title = str(row.get("title", "")).lower().replace(" ", "")

    # 判断是否为纯音乐
    is_pure_music = any(
        marker in lyrics_text or marker in title for marker in PURE_MUSIC_MARKERS
    )

    # 汉字在全部歌词字符中超过60%，就认为是中文歌。
    chinese_count = len(re.findall(r"[\u4e00-\u9fff]", lyrics_text))
    chinese_ratio = chinese_count / len(lyrics_text) if lyrics_text else 0
    return (
        not is_pure_music
        and len(lines) >= 10
        and chinese_ratio > 0.6
    )

def build_song_metrics(data: pd.DataFrame) -> pd.DataFrame:
    """建立三个分析模块共用的基础歌曲数据。"""
    rows = []
    for row in data.itertuples(index=False):
        metadata, real_lyrics = clean_lyrics(row.title, row.lyrics)
        rows.append(
            {
                "song_id": row.song_id,
                "title": row.title,
                "artist_id": row.artist_id,
                "artist_name": row.artist_name,
                "metadata": metadata,
                "real_lyrics": real_lyrics,
            }
        )
    temp = pd.DataFrame(rows)
    return temp[temp.apply(is_valid, axis=1)]

def configure_chinese_font() -> None:
    """设置图表使用的中文字体。"""
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
    plt.rcParams["axes.unicode_minus"] = False
