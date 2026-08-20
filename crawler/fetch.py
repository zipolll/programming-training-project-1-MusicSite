#下载器

from pathlib import Path


def fetch_text(url: str, cache_path: Path) -> str:
    """Return cached text or request it and save it locally.

    TODO: use requests.Session, headers, timeout, status checks, retry policy,
    polite delay, and UTF-8-safe file handling. Do not bypass access controls.
    """
    raise NotImplementedError


def download_image(url: str, output_path: Path) -> Path:
    """Download one image for stable local display.

    TODO: validate response type and avoid overwriting unrelated files.
    """
    raise NotImplementedError

