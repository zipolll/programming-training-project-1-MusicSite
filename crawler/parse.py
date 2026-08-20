#解析器


def remove_lyric_timestamps(raw_lyrics: str) -> str:
    """Remove timestamp markers while retaining lyric text."""
    raise NotImplementedError


def parse_artist(raw_text: str) -> dict[str, str]:
    """Extract name, introduction, image URL, and source URL."""
    raise NotImplementedError


def parse_song(raw_text: str) -> dict[str, str]:
    """Extract title, artist, lyrics, image URL, and source URL."""
    raise NotImplementedError

