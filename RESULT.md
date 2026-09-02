# 数据分析报告

## 1. 数据与清洗

数据库包含2632首歌曲、264位歌手。程序删除空行和制作信息，排除纯音乐、歌词不足10行及汉字比例不超过60%的歌曲，最终保留1504首。数据不是歌曲全集，以下结论只适用于本项目样本。

公共筛选代码位于 [`data_utils.py`](data_utils.py)：

```python
def is_valid(row: pd.Series) -> bool:
    lines = row["real_lyrics"]
    lyrics_text = "".join(lines).lower().replace(" ", "")
    title = str(row.get("title", "")).lower().replace(" ", "")

    is_pure_music = any(
        marker in lyrics_text or marker in title for marker in PURE_MUSIC_MARKERS
    )
    chinese_count = len(re.findall(r"[\u4e00-\u9fff]", lyrics_text))
    chinese_ratio = chinese_count / len(lyrics_text) if lyrics_text else 0
    return not is_pure_music and len(lines) >= 10 and chinese_ratio > 0.6
```


## 2. 结论一：第一人称和第二人称是歌词中最常见的主导视角

程序统计第一人称“我、我们”等、第二人称“你、你们”等和第三人称“他、她、它”等。次数最多的一类为主导人称；最高次数并列记为“混合人称”，均为0记为“无明显人称”。代码位于 [`person_perspective.py`](person_perspective.py)：

```python
def count_persons(text: str) -> dict[str, int]:
    result = {}
    for person, words in PERSON_WORDS.items():
        result[person] = len(re.findall("|".join(words), text))
    return result


def get_dominant_person(person_counts: dict[str, int]) -> str:
    highest_count = max(person_counts.values())
    if highest_count == 0:
        return "无明显人称"

    leaders = [
        person for person, count in person_counts.items()
        if count == highest_count
    ]
    if len(leaders) > 1:
        return "混合人称"
    return f"{leaders[0]}主导"
```

| 主导人称 | 歌曲数 | 占比 |
|---|---:|---:|
| 第一人称主导 | 784 | 52.1% |
| 第二人称主导 | 524 | 34.8% |
| 第三人称主导 | 79 | 5.3% |
| 混合人称 | 87 | 5.8% |
| 无明显人称 | 30 | 2.0% |

![歌词主导人称分布](output/person_perspective.png)

第一、第二人称合计占86.9%，说明样本歌词主要采用自我表达或向他人诉说的视角；第三人称主导仅占5.3%。字符匹配可能将“迷你”中的“你”等误计，因此结果只反映总体趋势。

## 3. 结论二：本人作曲率更高的歌手更多，作词率与作曲率呈正相关

程序从元数据识别作词、作曲署名，姓名去除空格和标点后完整匹配。为减小偶然性，只保留至少5首有效歌曲且两项参与率至少一项大于0的歌手，共52位。代码位于 [`artist_creation.py`](artist_creation.py)：

```python
self_lyric_count = int(group["self_lyricist"].sum())
self_composer_count = int(group["self_composer"].sum())
if self_lyric_count == 0 and self_composer_count == 0:
    continue

lyric_rate = self_lyric_count / song_count
composer_rate = self_composer_count / song_count
correlation = artist_metrics["self_lyric_rate"].corr(
    artist_metrics["self_composer_rate"]
)
```

| 比较结果 | 歌手数 | 占比 |
|---|---:|---:|
| 本人作词率高于本人作曲率 | 12 | 23.1% |
| 本人作曲率高于本人作词率 | 28 | 53.8% |
| 两项参与率相等 | 12 | 23.1% |

![歌手本人作词率与作曲率的关系](output/artist_creation.png)

作曲率更高的歌手占53.8%，高于作词率更高的23.1%。两项指标的相关系数为0.463，呈中等程度正相关。程序不处理别名和多人联合署名，每位歌手也只采集约10首歌曲，因此不能代表其全部作品。

## 4. 结论三：悲伤与回忆是四类歌词主题中共现程度最高的组合

程序用固定关键词识别爱情、喜悦、悲伤和回忆四类主题。一首歌命中任一关键词，就记为出现该主题。主题关联使用Jaccard系数，即“同时出现数 ÷ 至少出现一个的数量”。代码位于 [`theme_cooccurrence.py`](theme_cooccurrence.py)：

```python
def detect_themes(text: str) -> dict[str, bool]:
    result = {}
    for theme, words in THEME_WORDS.items():
        result[theme] = any(word in text for word in words)
    return result

either_count = int(
    (theme_metrics[first_theme] | theme_metrics[second_theme]).sum()
)
both_count = int(
    (theme_metrics[first_theme] & theme_metrics[second_theme]).sum()
)
matrix.loc[first_theme, second_theme] = (
    both_count / either_count if either_count else 0
)
```

四类主题分别命中：悲伤713首（47.4%）、爱情613首（40.8%）、回忆602首（40.0%）、喜悦408首（27.1%）。共现度最高的三个组合如下：

| 主题组合 | 同时出现 | 至少出现一个 | Jaccard系数 |
|---|---:|---:|---:|
| 悲伤—回忆 | 344 | 971 | 0.354 |
| 爱情—悲伤 | 326 | 1000 | 0.326 |
| 爱情—回忆 | 252 | 963 | 0.262 |

![四类歌词主题的共现关系](output/theme_cooccurrence.png)

悲伤—回忆的系数最高，说明样本中回忆较常与悲伤表达同时出现；爱情—悲伤次之。关键词方法不能识别隐喻和否定语境，Jaccard系数也只表示共现，不代表因果。

## 5. 总结
三项分析分别说明：
1. 歌词以第一、第二人称为主；
2. 有创作参与的歌手中，本人作曲率更高的情况更多；
3. 悲伤与回忆的主题共现度最高。

注：结果可通过 `runanalyze.bat` 重新生成。
