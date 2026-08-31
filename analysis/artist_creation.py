"""分析歌手本人作词率与本人作曲率的关系。"""

import re
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def check_credit(metadata: list[str], credit_type: str, artist_name: str) -> bool:
    """判断词曲署名中是否包含指定歌手。"""
    if credit_type == "lyricist":
        pattern = re.compile(r"^(词|作词|Lyrics by)\s*[:：]\s*(.+)$", re.IGNORECASE)
    else:
        pattern = re.compile(
            r"^(曲|作曲|Composed by|Composer)\s*[:：]\s*(.+)$", re.IGNORECASE
        )

    for line in metadata:
        match = pattern.match(line)
        if match:
            credit = match.group(2)
            normalized_artist = "".join(
                re.findall(r"[A-Za-z0-9\u4e00-\u9fff]", artist_name)
            ).lower()  # 去除姓名中的非字母数字汉字字符
            normalized_credit = "".join(
                re.findall(r"[A-Za-z0-9\u4e00-\u9fff]", credit)
            ).casefold()
            return bool(normalized_artist) and normalized_artist == normalized_credit
    return False


def add_credit_fields(song_metrics: pd.DataFrame) -> pd.DataFrame:
    """从每首歌的元数据中增加词曲署名和本人参与字段。"""
    result = song_metrics.copy()
    result["self_lyricist"] = result.apply(
        lambda row: check_credit(row["metadata"], "lyricist", row["artist_name"]),
        axis=1,
    )
    result["self_composer"] = result.apply(
        lambda row: check_credit(row["metadata"], "composer", row["artist_name"]),
        axis=1,
    )
    return result


def build_artist_metrics(song_metrics: pd.DataFrame) -> pd.DataFrame:
    """计算至少有五首歌曲且至少参与一项创作的歌手指标。"""
    songs = add_credit_fields(song_metrics)
    rows = []
    groups = songs.groupby("artist_name")
    for artist_name, group in groups:
        song_count = len(group)
        if song_count < 5:
            continue

        self_lyric_count = int(group["self_lyricist"].sum())
        self_composer_count = int(group["self_composer"].sum())
        if self_lyric_count == 0 and self_composer_count == 0:
            continue

        lyric_rate = self_lyric_count / song_count
        composer_rate = self_composer_count / song_count
        rows.append(
            {
                "artist_name": artist_name,
                "song_count": song_count,
                "self_lyric_count": self_lyric_count,
                "self_lyric_rate": lyric_rate,
                "self_composer_count": self_composer_count,
                "self_composer_rate": composer_rate,
            }
        )
    return pd.DataFrame(rows).sort_values("artist_name").reset_index(drop=True)


def get_result(artist_metrics: pd.DataFrame, output_dir: Path) -> pd.DataFrame:
    """保存歌手明细，并返回和保存汇总结果。"""
    output_dir.mkdir(parents=True, exist_ok=True)
    artist_metrics.to_csv(
        output_dir / "artist_credit_metrics.csv", index=False, encoding="utf-8-sig"
    )
    result = pd.DataFrame(
        [
            {
                "lyric_rate_higher_ratio": (
                    artist_metrics["self_lyric_rate"]
                    > artist_metrics["self_composer_rate"]
                ).mean(),
                "composer_rate_higher_ratio": (
                    artist_metrics["self_composer_rate"]
                    > artist_metrics["self_lyric_rate"]
                ).mean(),
                "correlation": artist_metrics["self_lyric_rate"].corr(
                    artist_metrics["self_composer_rate"]
                ),
            }
        ]
    )
    result.to_csv(
        output_dir / "artist_creation_result.csv", index=False, encoding="utf-8-sig"
    )
    return result


def draw_chart(artist_metrics: pd.DataFrame, output_path: Path) -> None:
    """用气泡散点图展示本人作词率与本人作曲率的关系。"""
    correlation = artist_metrics["self_lyric_rate"].corr(
        artist_metrics["self_composer_rate"]
    )
    bubbles = (
        artist_metrics.groupby(["self_lyric_rate", "self_composer_rate"])
        .size()
        .reset_index(name="artist_count")
    )
    figure, axis = plt.subplots(figsize=(7, 6))
    axis.scatter(
        bubbles["self_lyric_rate"],
        bubbles["self_composer_rate"],
        s=bubbles["artist_count"] * 30,
        alpha=0.6,
        edgecolors="white",
    )
    axis.plot([0, 1], [0, 1], "--", color="gray")
    axis.set_xlim(-0.05, 1.05)
    axis.set_ylim(-0.05, 1.05)
    axis.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    axis.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    axis.set_xlabel("本人作词率")
    axis.set_ylabel("本人作曲率")
    axis.set_title(f"本人作词率与作曲率的关系（r={correlation:.2f}）\n")
    axis.grid(alpha=0.25)
    figure.tight_layout()
    figure.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(figure)
