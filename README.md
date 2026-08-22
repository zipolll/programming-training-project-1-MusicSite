# 音乐信息展示与检索系统

程序设计基础课程大作业 1。

项目计划从音乐网站爬取歌曲和歌手信息，使用 Django 完成数据展示、评论和搜索功能，并对爬取的数据进行简单分析。

## 环境

- Python 3.14
- Django 5.2
- SQLite
- requests
- Beautiful Soup
- fake-useragent
- pandas
- Matplotlib

## 项目结构

```text
Project1/
├── manage.py               Django 命令入口
├── requirements.txt        Python 依赖
├── music_site/             Django 项目配置
├── catalog/                歌曲、歌手和评论功能
├── crawler/                爬虫代码
├── templates/              HTML 模板
├── static/                 CSS 等静态文件
├── media/                  下载的歌曲和歌手图片
├── data/                   爬虫原始数据和清洗后数据
└── analysis/               数据分析代码和输出图表
```

### `music_site`

保存 Django 的全局配置和总路由。

- `settings.py`：数据库、模板、静态文件、时区等配置
- `urls.py`：项目总路由
- `wsgi.py`：Django 服务器入口

### `catalog`

网站的主要功能模块。

- `models.py`：歌手、歌曲和评论的数据模型
- `views.py`：列表、详情、评论和搜索的处理函数
- `urls.py`：各页面的 URL
- `forms.py`：评论和搜索表单
- `admin.py`：Django 后台配置
- `tests.py`：功能测试
- `migrations/`：数据库结构迁移记录

### `crawler`

爬虫相关代码。

- `config.py`：酷我接口、请求间隔、超时和目标数量
- `fetch.py`：使用随机 User-Agent 发送请求并缓存原始响应
- `parse.py`：解析歌手、歌曲、歌词和热门评论
- `crawl_process.py`：获取歌手资料、歌曲列表和歌曲详细信息
- `storage.py`：读取和保存处理结果及断点状态
- `run.py`：选择完整爬取或单歌手展示模式

### `templates`

网站页面模板。

- `base.html`：公共页面结构和导航栏
- `catalog/song_list.html`：歌曲列表
- `catalog/song_detail.html`：歌曲详情
- `catalog/artist_list.html`：歌手列表
- `catalog/artist_detail.html`：歌手详情
- `catalog/search_results.html`：搜索和搜索结果

### `analysis`

读取爬取的数据，完成统计分析并将图表保存到 `analysis/output/`。

## 酷我音乐爬虫

安装依赖后运行：

```powershell
.venv\Scripts\python.exe -B -m crawler.run
```

程序支持两种模式：

- 直接回车：按照 A-Z 分页获取歌手，每位歌手最多保存 10 首有效歌曲，并从已有断点继续。
- 输入酷我歌手主页 URL：爬取或读取指定歌手，并在终端展示歌手资料、最多 10 首歌曲及热门评论。例如：

```text
https://kuwo.cn/newh5/artist/artistDetail?id=336
```

爬虫保存歌手姓名、简介、图片 URL 和来源链接，以及歌曲名称、专辑、无时间轴歌词、图片 URL、来源链接和最多 3 条热门评论。图片只保存 URL，不下载音频或视频。

原始接口响应缓存在 `data/raw/kuwo/`，处理后的数据和已完成歌手 ID 保存在 `data/processed/kuwo.json`。每处理完一位歌手就保存一次，程序中断后重新运行即可继续。

## 当前进度

已完成：

- Django 项目结构
- 歌手、歌曲和评论模型
- 数据库初始化
- 页面路由和模板骨架
- 基础页面访问测试
- 酷我音乐歌手、歌曲、歌词和热门评论爬取
- 原始响应缓存和按歌手断点续爬
- 单歌手 URL 展示模式

待完成：

- 完成至少 2000 首歌曲和 100 位歌手的正式数据采集与检查
- 数据清洗与导入
- 列表和分页
- 歌曲、歌手详情
- 评论新增和删除
- 歌曲、歌手搜索
- 页面样式
- 数据分析与图表

