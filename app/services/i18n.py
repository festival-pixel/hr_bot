import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LOCALES_DIR = BASE_DIR / "locales"
DEFAULT_LANG = "ru"

_cache: dict[str, dict] = {}


def _load(lang: str) -> dict:
    if lang not in _cache:
        path = LOCALES_DIR / f"{lang}.json"
        if not path.exists():
            path = LOCALES_DIR / f"{DEFAULT_LANG}.json"
        with open(path, encoding="utf-8") as f:
            _cache[lang] = json.load(f)
    return _cache[lang]


def t(lang: str, key: str, **kwargs) -> str:
    """Возвращает локализованную строку; при отсутствии ключа — фолбэк на ru."""
    text = _load(lang).get(key)
    if text is None:
        text = _load(DEFAULT_LANG).get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text
