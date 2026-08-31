"""组织三个音乐数据分析模块的公共执行流程。"""

from __future__ import annotations

import pandas as pd

from analysis.artist_creation import (
    build_artist_metrics,
    draw_chart as draw_artist_chart,
    get_result as get_artist_result,
)
from analysis.data_utils import (
    OUTPUT_DIR,
    build_song_metrics,
    configure_chinese_font,
    load_data,
)
from analysis.person_perspective import (
    build_person_metrics,
    draw_chart as draw_person_chart,
    get_result as get_person_result,
)
from analysis.theme_cooccurrence import (
    build_theme_metrics,
    draw_chart as draw_theme_chart,
    get_result as get_theme_result,
)


# 只能通过 manage.py analyze_music 来执行该脚本
if __name__ == "__main__":
    raise SystemExit("请使用 .venv\\Scripts\\python.exe manage.py analyze_music")


def print_data_summary(valid_song_metrics: pd.DataFrame) -> None:
    """输出三个模块共用的数据质量信息。"""
    print(f"进入分析的有效中文歌曲：{len(valid_song_metrics)}")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    configure_chinese_font()

    # 加载原始数据并构建有效歌曲表
    raw_data = load_data()
    valid_song_metrics = build_song_metrics(raw_data)

    # 三个模块进行分析
    person_metrics = build_person_metrics(valid_song_metrics)
    artist_metrics = build_artist_metrics(valid_song_metrics)
    theme_metrics = build_theme_metrics(valid_song_metrics)

    person_summary = get_person_result(person_metrics, OUTPUT_DIR)
    get_artist_result(artist_metrics, OUTPUT_DIR)
    theme_matrix = get_theme_result(theme_metrics, OUTPUT_DIR)

    # 三个模块分别生成自己的图表。
    draw_person_chart(person_summary, OUTPUT_DIR / "person_perspective.png")
    draw_artist_chart(artist_metrics, OUTPUT_DIR / "artist_creation.png")
    draw_theme_chart(theme_matrix, OUTPUT_DIR / "theme_cooccurrence.png")

    print_data_summary(valid_song_metrics)
