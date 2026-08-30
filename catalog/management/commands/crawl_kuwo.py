"""通过Django命令启动酷我音乐爬虫。"""

from django.core.management.base import BaseCommand

from crawler.crawl import run_crawler


class Command(BaseCommand):
    help = "爬取酷我音乐数据并直接保存到数据库"

    def handle(self, *args, **options):
        run_crawler()
