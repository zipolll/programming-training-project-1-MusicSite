"""统计歌词中占主导的人称类型。"""

import re
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PERSON_WORDS = {
    "第一人称": ["我们", "咱们", "我", "咱"],
    "第二人称": ["你们", "您们", "你", "您"],
    "第三人称": ["他们", "她们", "它们", "他", "她", "它"],
}

CATEGORY_ORDER = [
    "第一人称主导",
    "第二人称主导",
    "第三人称主导",
    "混合人称",
    "无明显人称",
]


def count_persons(text: str) -> dict[str, int]:
    """统计三类人称代词的出现次数。"""
    result = {}
    for person, words in PERSON_WORDS.items():
        pattern = "|".join(words)
        matched_words = re.findall(pattern, text)
        result[person] = len(matched_words)
    return result

def get_dominant_person(person_counts: dict[str, int]) -> str:
    """根据出现次数判断歌词的主导人称。"""
    highest_count = max(person_counts.values())
    if highest_count == 0:
        return "无明显人称"

    leaders = []
    for person, count in person_counts.items():
        if count == highest_count:
            leaders.append(person)
    if len(leaders) > 1:
        return "混合人称"
    return f"{leaders[0]}主导"


def build_person_metrics(song_metrics: pd.DataFrame) -> pd.DataFrame:
    """为每首歌增加三类人称次数和主导人称。"""
    result = song_metrics.copy()
    for person in PERSON_WORDS:
        result[f"{person}_次数"] = 0
    result["主导人称"] = ""

    for row_index, lyric_lines in result["real_lyrics"].items():
        person_counts = count_persons("\n".join(lyric_lines))
        for person, count in person_counts.items():
            result.at[row_index, f"{person}_次数"] = count
        result.at[row_index, "主导人称"] = get_dominant_person(person_counts)
    return result


def get_result(person_metrics: pd.DataFrame, output_dir: Path) -> pd.DataFrame:
    """保存歌曲人称明细，并生成各主导人称的数量和占比。"""
    output_dir.mkdir(parents=True, exist_ok=True)
    detail_columns = [
        "song_id",
        "title",
        "artist_name",
        *[f"{person}_次数" for person in PERSON_WORDS],
        "主导人称",
    ]
    person_metrics[detail_columns].to_csv(
        output_dir / "person_perspective_metrics.csv",
        index=False,
        encoding="utf-8-sig",
    )

    rows = []
    total = len(person_metrics)
    for category in CATEGORY_ORDER:
        song_count = int((person_metrics["主导人称"] == category).sum())
        rows.append(
            {
                "主导人称": category,
                "歌曲数": song_count,
                "占比": song_count / total if total else 0,
            }
        )
    summary = pd.DataFrame(rows)
    summary.to_csv(
        output_dir / "person_perspective_summary.csv",
        index=False,
        encoding="utf-8-sig",
    )
    return summary


def draw_chart(summary: pd.DataFrame, output_path: Path) -> None:
    """绘制各类主导人称的歌曲占比。"""
    figure, axis = plt.subplots(figsize=(9, 5))
    bars = axis.bar(summary["主导人称"], summary["占比"], color="#4C78A8")
    axis.set_title("歌词主导人称分布")
    axis.set_ylabel("歌曲占比")
    axis.set_ylim(0, max(summary["占比"]) + 0.08)
    for bar, ratio in zip(bars, summary["占比"]):
        axis.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{ratio:.1%}",
            ha="center",
            va="bottom",
        )
    figure.tight_layout()
    figure.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(figure)
