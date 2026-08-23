"""集中保存酷我音乐爬虫的配置"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent # 获取项目根目录
KUWO_RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw" / "kuwo" # 获取酷我音乐原始数据存储目录
KUWO_OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "kuwo.json" # 获取酷我音乐处理后数据存储路径

KUWO_ARTIST_LIST_URL = "https://wapi.kuwo.cn/api/www/artist/artistInfo"
KUWO_ARTIST_INFO_URL = "https://www.kuwo.cn/singer_detail/{artist_id}/info"
KUWO_SONG_LIST_URL = "https://wapi.kuwo.cn/api/www/artist/artistMusic"
KUWO_LYRIC_URL = "https://wapi.kuwo.cn/openapi/v1/www/lyric/getlyric"
KUWO_COMMENT_URL = (
    "https://comment.kuwo.cn/com.s?"
    "type=get_rec_comment&f=web&page=1"
    "&rows={rows}&digest=15&sid={song_id}"
    "&uid=0&prod=newWeb&httpsStatus=1"
)

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ARTISTS_PER_PAGE = 10
SONGS_PER_ARTIST = 10
SONGS_PER_PAGE = 10
COMMENTS_PER_SONG = 3
TARGET_SONG_COUNT = 2000
TARGET_ARTIST_COUNT = 100

MIN_REQUEST_INTERVAL_SECONDS = 0.1
MAX_REQUEST_INTERVAL_SECONDS = 0.5
REQUEST_TIMEOUT_SECONDS = 15

