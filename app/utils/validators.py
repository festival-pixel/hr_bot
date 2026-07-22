MIN_AGE = 14
MAX_AGE = 80


def parse_age(text: str) -> int | None:
    """Возвращает возраст, если введено корректное число в диапазоне, иначе None."""
    text = text.strip()
    if not text.isdigit():
        return None
    age = int(text)
    if MIN_AGE <= age <= MAX_AGE:
        return age
    return None
