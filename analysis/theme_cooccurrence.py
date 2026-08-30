"""分析歌词中四类主题的共现关系。"""

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd


THEME_WORDS = {
    "爱情": ["爱情", "爱你", "爱我", "喜欢", "恋人", "拥抱", "亲吻", "心动"],
    "喜悦": ["开心", "快乐", "幸福", "微笑", "笑容", "喜悦", "甜蜜", "美好"],
    "悲伤": ["悲伤", "难过", "伤心", "心痛", "眼泪", "哭", "孤独", "寂寞", "遗憾", "失去"],
    "回忆": ["回忆", "曾经", "从前", "过去", "当年", "往事", "记得", "想起"],
}

def detect_themes(text: str) -> dict[str, bool]:
    """返回每个主题是否出现关键词。"""
    result = {}
    for theme, words in THEME_WORDS.items():
        result[theme] = any(word in text for word in words)
    return result

def build_theme_metrics(song_metrics: pd.DataFrame) -> pd.DataFrame:
    """在歌曲数据后增加四个主题判断字段。"""
    result = song_metrics.copy()

    # 检测并写入每首歌的主题出现情况
    for theme in THEME_WORDS:
        result[theme] = False

    for row_index, lyric_lines in result["real_lyrics"].items():
        lyrics_text = "\n".join(lyric_lines)
        detected_themes = detect_themes(lyrics_text)

        for theme, has_keyword in detected_themes.items():
            result.at[row_index, theme] = has_keyword

    return result

def get_result(theme_metrics: pd.DataFrame, output_dir: Path) -> pd.DataFrame:
    """计算主题共现系数，并保存歌曲主题表和共现系数表。"""
    output_dir.mkdir(parents=True, exist_ok=True)
    matrix = pd.DataFrame(index=THEME_WORDS, columns=THEME_WORDS, dtype=float)
    for first_theme in THEME_WORDS:
        for second_theme in THEME_WORDS:
            either_count = int(
                (theme_metrics[first_theme] | theme_metrics[second_theme]).sum()
            )
            both_count = int(
                (theme_metrics[first_theme] & theme_metrics[second_theme]).sum()
            )
            matrix.loc[first_theme, second_theme] = (
                both_count / either_count if either_count else 0
            )

    theme_columns = ["song_id", "title", "artist_name", *THEME_WORDS.keys()]
    theme_metrics[theme_columns].to_csv(
        output_dir / "theme_metrics.csv", index=False, encoding="utf-8-sig"
    )
    matrix.to_csv(output_dir / "theme_cooccurrence.csv", encoding="utf-8-sig")
    return matrix

def draw_chart(matrix: pd.DataFrame, output_path: Path) -> None:
    """绘制主题共现热力图。"""
    color_values = matrix.copy()
    for index in range(len(color_values)):
        color_values.iloc[index, index] = float("nan")

    color_map = plt.colormaps["YlOrRd"].copy()
    color_map.set_bad("#E6E6E6")
    figure, axis = plt.subplots(figsize=(7, 6))
    image = axis.imshow(color_values.values, cmap=color_map, vmin=0, vmax=0.4)  # 把pandas DataFrame 转换为二维数组用于绘图
    axis.set_title("主题共现系数")
    axis.set_xticks(range(len(matrix.columns)), matrix.columns)
    axis.set_yticks(range(len(matrix.index)), matrix.index)
    for row_index in range(len(matrix.index)):
        for column_index in range(len(matrix.columns)):
            value = matrix.iloc[row_index, column_index]
            axis.text(
                column_index,
                row_index,
                "—" if row_index == column_index else f"{value:.2f}",
                ha="center",
                va="center",
                color="white" if row_index != column_index and value >= 0.3 else "black",  # 根据值的大小选择文字颜色，以保证在热力图上可读
            )
    figure.colorbar(image, ax=axis, fraction=0.046, pad=0.04)  # 添加颜色条以显示热力图的数值对应关系，并控制其位置和大小
    figure.tight_layout()
    figure.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(figure)
