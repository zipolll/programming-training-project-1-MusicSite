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

## 启动指引

以下命令以 Windows PowerShell 为例。首次启动需要安装 Python 3.14；Git 只在克隆项目时需要。

### 1. 克隆并进入项目

```powershell
git clone <仓库地址>
cd Project1
```

将 `<仓库地址>` 替换为本项目的 Git 仓库地址。如果已经下载或解压了项目，直接在 PowerShell 中进入项目根目录即可。

### 2. 创建唯一的虚拟环境

```powershell
py -3.14 -m venv .venv
```

项目统一使用根目录下的 `.venv`。该目录只属于本机，不会提交到 Git；请勿再创建 `venv`、`env` 等其他环境。

### 3. 安装依赖

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

所有运行依赖都记录在 `requirements.txt` 中。编辑器提示包未安装时，请把 Python 解释器选择为 `Project1\.venv\Scripts\python.exe`。

### 4. 初始化数据库

```powershell
.\.venv\Scripts\python.exe manage.py migrate
```

仓库不提交 `db.sqlite3`，因此每位用户首次运行时都要执行迁移。迁移完成后会在项目根目录生成本机数据库。

### 5. 启动网站

```powershell
.\.venv\Scripts\python.exe manage.py runserver
```

浏览器访问 <http://127.0.0.1:8000/>。在终端中按 `Ctrl+C` 可停止服务器。

仓库中的 Windows 快捷脚本也可以完成同一操作：

```powershell
.\runserver.bat
```

### 6. 获取展示数据（可选）

新建的数据库没有歌曲和歌手数据。需要展示真实数据时，可以运行酷我音乐爬虫：

```powershell
.\runcrawler.bat
```

也可以直接执行：

```powershell
.\.venv\Scripts\python.exe -B manage.py crawl_kuwo
```

爬虫会询问是否输入指定歌手主页 URL；直接回车则使用默认的分页爬取模式。原始响应写入 `data/raw/kuwo/`，业务数据写入本机的 `db.sqlite3`，两者均不会提交到 Git。

### 7. 测试与数据分析（可选）

运行全部测试：

```powershell
.\.venv\Scripts\python.exe manage.py test
```

也可以运行 `runtests.bat`，在菜单中选择测试范围。数据库已有爬取数据后，可执行数据分析：

```powershell
.\runanalyze.bat
```

分析命令会把 CSV 明细和 PNG 图表写入 `analysis/output/`。仓库仅保留报告使用的三张 PNG 图表，运行时生成的 CSV 文件不会提交。

## 项目结构与文件说明

下面是提交完成后，用户通过 Git 克隆时会看到的完整目录树。每个文件均在树中标明用途；`.venv`、`db.sqlite3`、爬虫缓存和 Python 缓存等本机生成内容不在其中。

```text
Project1/
├── .gitignore                         Git 忽略规则
├── README.md                          项目介绍、启动指引和文件说明
├── REPORT.md                          课程项目报告
├── manage.py                          Django 命令行入口
├── requirements.txt                   Python 依赖及版本范围
├── runserver.bat                      Windows 网站启动脚本
├── runcrawler.bat                     Windows 爬虫启动脚本
├── runanalyze.bat                     Windows 数据分析启动脚本
├── runtests.bat                       Windows 分模块测试菜单
├── music_site/                        Django 项目级配置
│   ├── __init__.py                    Python 包标记
│   ├── settings.py                    数据库、模板、静态文件、语言及时区配置
│   ├── urls.py                        项目总路由
│   └── wsgi.py                        WSGI 部署入口
├── catalog/                           歌曲、歌手、评论和页面功能
│   ├── __init__.py                    Python 包标记
│   ├── admin.py                       Django 后台模型注册
│   ├── apps.py                        catalog 应用配置
│   ├── forms.py                       搜索、评论等表单定义
│   ├── models.py                      Artist、Song、Comment 数据模型
│   ├── urls.py                        catalog 应用路由
│   ├── views.py                       列表、详情、搜索和评论视图
│   ├── tests.py                       页面、模型和交互功能测试
│   ├── management/                    自定义 Django 管理命令
│   │   ├── __init__.py                Python 包标记
│   │   └── commands/
│   │       ├── __init__.py            Python 包标记
│   │       ├── analyze_music.py       `manage.py analyze_music` 命令入口
│   │       └── crawl_kuwo.py          `manage.py crawl_kuwo` 命令入口
│   └── migrations/                    可复现数据库结构的迁移记录
│       ├── __init__.py                Python 包标记
│       ├── 0001_initial.py            创建歌手、歌曲和评论表
│       ├── 0002_alter_artist_options_alter_song_options_and_more.py
│       │                              调整模型选项及相关字段
│       ├── 0003_alter_comment_created_at.py
│       │                              调整评论创建时间字段
│       └── 0004_alter_artist_image_url_alter_song_image_url.py
│                                      调整歌手和歌曲图片 URL 字段
├── crawler/                           酷我音乐数据采集模块
│   ├── __init__.py                    Python 包标记
│   ├── config.py                      接口地址、数量、超时和请求间隔配置
│   ├── fetch.py                       HTTP 请求、随机 User-Agent 和原始响应缓存
│   ├── parse.py                       歌手、歌曲、歌词和热门评论解析
│   ├── crawl_process.py               单个歌手及其歌曲的爬取流程
│   ├── crawl.py                       URL 处理和完整爬取流程控制
│   ├── storage.py                     断点判断及数据库写入
│   └── tests.py                       请求、解析、流程和存储测试
├── analysis/                          音乐数据统计分析模块
│   ├── __init__.py                    Python 包标记
│   ├── analyze.py                     三类分析的统一执行流程
│   ├── data_utils.py                  数据读取、清洗和公共指标构建
│   ├── artist_creation.py             歌手本人作词率与作曲率分析
│   ├── person_perspective.py          歌词主导人称分析
│   ├── theme_cooccurrence.py          歌词主题共现分析
│   ├── tests.py                       分析规则和结果生成测试
│   ├── result.md                      分析方法及结论说明
│   └── output/                        报告引用的分析图表
│       ├── artist_creation.png        本人作词率与作曲率图
│       ├── person_perspective.png     歌词主导人称分布图
│       └── theme_cooccurrence.png     歌词主题共现热力图
├── templates/                         Django HTML 模板
│   ├── base.html                      全站公共结构和导航栏
│   └── catalog/
│       ├── artist_detail.html         歌手详情页
│       ├── artist_list.html           歌手列表页
│       ├── pagination.html            列表分页组件
│       ├── search.html                歌曲和歌手搜索页
│       ├── song_detail.html           歌曲详情与评论页
│       └── song_list.html             歌曲列表及首页
├── static/                            项目自带静态资源
│   ├── css/
│   │   └── site.css                   全站样式
│   └── images/
│       ├── default-artist.png         歌手默认占位图
│       └── default-song.png           歌曲默认占位图
├── data/
│   └── .gitkeep                       保留空数据目录；实际爬虫缓存被忽略
└── report_assets/                     REPORT.md 使用的页面截图
    ├── artists.png                    歌手列表页截图
    ├── home.png                       网站首页截图
    ├── search.png                     搜索页截图
    └── song_detail.png                歌曲详情页截图
```

运行后还会生成下列内容，但它们属于本机数据并已被 `.gitignore` 排除：

- `.venv/`：当前项目唯一的 Python 虚拟环境。
- `db.sqlite3`：本机 SQLite 数据库。
- `data/raw/kuwo/`：爬虫原始接口响应缓存。
- `analysis/output/*.csv`：分析过程产生的明细和汇总数据。
- `__pycache__/`、`*.pyc`：Python 自动生成的字节码缓存。