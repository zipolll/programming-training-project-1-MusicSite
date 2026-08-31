"""通过Django命令运行三个音乐数据分析模块。"""

from django.core.management.base import BaseCommand

from analysis.analyze import main


class Command(BaseCommand):
    help = "运行音乐数据分析并生成CSV和PNG文件"

    def handle(self, *args: object, **options: object) -> None:
        main()
        self.stdout.write(self.style.SUCCESS("数据分析完成。"))
