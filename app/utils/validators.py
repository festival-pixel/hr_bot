MIN_AGE = 14
MAX_AGE = 80


def parse_age(text: str) -> int | None:
    """Возвращает возраст, если введено корректное число в диапазоне, иначе None."""
    return parse_int(text, MIN_AGE, MAX_AGE)


def parse_int(text: str, lo: int, hi: int) -> int | None:
    """Возвращает целое число в диапазоне [lo, hi], иначе None."""
    text = text.strip()
    if not text.isdigit():
        return None
    value = int(text)
    if lo <= value <= hi:
        return value
    return None
