# 音乐信息展示与检索系统

程序设计基础课程大作业 1。

项目计划从音乐网站爬取歌曲和歌手信息，使用 Django 完成数据展示、评论和搜索功能，并对爬取的数据进行简单分析。

## 环境

- Python 3.14
- Django 5.2
- SQLite
- requests
- Beautiful Soup
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

- `config.py`：请求间隔、超时和目标数量
- `fetch.py`：发送请求、缓存页面和下载图片
- `parse.py`：解析歌曲、歌手和歌词
- `storage.py`：保存数据和断点记录
- `run.py`：爬虫运行入口

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

## 当前进度

已完成：

- Django 项目结构
- 歌手、歌曲和评论模型
- 数据库初始化
- 页面路由和模板骨架
- 基础页面访问测试

待完成：

- 歌曲和歌手爬取
- 数据清洗与导入
- 列表和分页
- 歌曲、歌手详情
- 评论新增和删除
- 歌曲、歌手搜索
- 页面样式
- 数据分析与图表

