"""通过Django命令启动酷我音乐爬虫。"""

from django.core.management.base import BaseCommand

from crawler.crawl import main


class Command(BaseCommand):
    help = "爬取酷我音乐数据并直接保存到数据库"

    def handle(self, *args: object, **options: object) -> None:
        main()
        self.stdout.write(self.style.SUCCESS("本次爬取结束。"))
