#URL管理器

from pathlib import Path
from typing import Any


def append_json_record(record: dict[str, Any], output_path: Path) -> None:
    """Append one validated record without losing previous progress."""
    raise NotImplementedError


def load_seen_urls(checkpoint_path: Path) -> set[str]:
    """Load URLs already processed so an interrupted crawl can resume."""
    raise NotImplementedError

