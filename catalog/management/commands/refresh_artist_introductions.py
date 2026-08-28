"""用缓存的酷我歌手页面重新更新数据库中的简介。"""

from django.core.management.base import BaseCommand

from catalog.models import Artist
from crawler.crawl_process import crawl_artist_info
from crawler.run import get_single_artist_id


class Command(BaseCommand):
    help = "重新解析酷我歌手简介并更新数据库"

    def handle(self, *args, **options):
        updated_count = 0
        skipped_count = 0

        for artist in Artist.objects.all():
            artist_id = get_single_artist_id(artist.source_url)
            if not artist_id:
                skipped_count += 1
                continue

            artist_data = crawl_artist_info(artist_id, artist.prefix)
            if not artist_data["introduction"]:
                skipped_count += 1
                continue

            artist.introduction = artist_data["introduction"]
            artist.save(update_fields=["introduction"])
            updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"更新完成：成功 {updated_count} 位，跳过 {skipped_count} 位"
            )
        )
