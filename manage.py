#!/usr/bin/env python
"""提供 Django 项目的命令行管理入口。"""

import os
import sys

from django.core.management import execute_from_command_line


# 管理 Django 项目的命令行工具，自动创建
def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "music_site.settings")
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
