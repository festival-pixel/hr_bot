from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.constants import (
    STATUS_EMOJI,
    VACANCY_EMOJI,
    VACANCY_NAMES,
    VACANCY_ORDER,
    Schedule,
)
from app.services.i18n import t

PAGE_SIZE = 5


# ─────────────────────────── Кандидат ───────────────────────────

def language_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="🇷🇺 Русский", callback_data="lang:ru")
    b.button(text="🇺🇿 O'zbekcha", callback_data="lang:uz")
    b.adjust(2)
    return b.as_markup()


def vacancy_kb(lang: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for v in VACANCY_ORDER:
        b.button(text=VACANCY_NAMES[lang][v], callback_data=f"vac:{v}")
    b.adjust(1)
    return b.as_markup()


def yes_no_kb(lang: str, prefix: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t(lang, "btn_yes"), callback_data=f"{prefix}:yes")
    b.button(text=t(lang, "btn_no"), callback_data=f"{prefix}:no")
    b.adjust(2)
    return b.as_markup()


def schedule_kb(lang: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t(lang, "schedule_day"), callback_data=f"sch:{Schedule.DAY.value}")
    b.button(
        text=t(lang, "schedule_evening"),
        callback_data=f"sch:{Schedule.EVENING.value}",
    )
    b.adjust(1)
    return b.as_markup()


def skip_location_kb(lang: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t(lang, "btn_skip"), callback_data="loc:skip")
    return b.as_markup()


def skip_resume_kb(lang: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t(lang, "btn_skip"), callback_data="resume:skip")
    return b.as_markup()


def confirm_kb(lang: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t(lang, "btn_send"), callback_data="app:send")
    b.button(text=t(lang, "btn_restart"), callback_data="app:restart")
    b.adjust(1)
    return b.as_markup()


# ─────────────────────────── Админ ───────────────────────────

def admin_menu_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="📋 Все заявки", callback_data="adm:list")
    b.button(text="🔎 Поиск", callback_data="adm:search")
    b.button(text="📊 Статистика", callback_data="adm:stats")
    b.button(text="📥 Экспорт в Excel", callback_data="adm:excel")
    b.adjust(1)
    return b.as_markup()


def back_kb(callback_data: str = "adm:menu") -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="⬅️ Меню", callback_data=callback_data)
    return b.as_markup()


def open_card_kb(number: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="📂 Открыть карточку", callback_data=f"card:{number}")
    return b.as_markup()


def reject_confirm_kb(number: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="✅ Да, отклонить и удалить", callback_data=f"del:{number}")
    b.button(text="↩️ Отмена", callback_data=f"dcancel:{number}")
    b.adjust(1)
    return b.as_markup()


def to_list_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="⬅️ К списку", callback_data="L:all:all:0")
    return b.as_markup()


def list_kb(candidates, status: str, vacancy: str, offset: int, total: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()

    # Кнопки кандидатов
    for c in candidates:
        emoji = STATUS_EMOJI.get(c.status, "•")
        name = c.fullname if len(c.fullname) <= 20 else c.fullname[:19] + "…"
        b.row(
            InlineKeyboardButton(
                text=f"{c.application_number} · {name} · {emoji}",
                callback_data=f"card:{c.application_number}",
            )
        )

    # Пагинация
    pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    current = offset // PAGE_SIZE + 1
    nav = []
    if offset > 0:
        nav.append(
            InlineKeyboardButton(
                text="◀️", callback_data=f"L:{status}:{vacancy}:{offset - PAGE_SIZE}"
            )
        )
    nav.append(InlineKeyboardButton(text=f"{current}/{pages}", callback_data="noop"))
    if offset + PAGE_SIZE < total:
        nav.append(
            InlineKeyboardButton(
                text="▶️", callback_data=f"L:{status}:{vacancy}:{offset + PAGE_SIZE}"
            )
        )
    b.row(*nav)

    # Фильтр по статусу
    def mark(active: bool, label: str) -> str:
        return f"·{label}·" if active else label

    status_row = [
        InlineKeyboardButton(
            text=mark(status == "all", "Все"), callback_data=f"L:all:{vacancy}:0"
        )
    ]
    for s, emoji in STATUS_EMOJI.items():
        # «Отказ» = удаление, отдельного статуса нет — фильтр не показываем
        if s == "rejected":
            continue
        status_row.append(
            InlineKeyboardButton(
                text=mark(status == s, emoji), callback_data=f"L:{s}:{vacancy}:0"
            )
        )
    b.row(*status_row)

    # Фильтр по вакансии
    vac_row = [
        InlineKeyboardButton(
            text=mark(vacancy == "all", "Все"), callback_data=f"L:{status}:all:0"
        )
    ]
    for v, emoji in VACANCY_EMOJI.items():
        vac_row.append(
            InlineKeyboardButton(
                text=mark(vacancy == v, emoji), callback_data=f"L:{status}:{v}:0"
            )
        )
    b.row(*vac_row)

    b.row(InlineKeyboardButton(text="⬅️ Меню", callback_data="adm:menu"))
    return b.as_markup()


def card_kb(candidate) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    labels = [
        ("new", "🆕 Новая"),
        ("invited", "✅ Приглашён"),
        ("rejected", "❌ Отказ"),
        ("archived", "📦 Архив"),
    ]
    for s, label in labels:
        text = f"· {label} ·" if s == candidate.status else label
        b.button(text=text, callback_data=f"st:{candidate.application_number}:{s}")
    b.adjust(2)

    # Быстрая связь с кандидатом (только при наличии @username — надёжная ссылка)
    if candidate.username:
        b.row(
            InlineKeyboardButton(
                text="✍️ Написать кандидату",
                url=f"https://t.me/{candidate.username}",
            )
        )

    b.row(InlineKeyboardButton(text="⬅️ К списку", callback_data="L:all:all:0"))
    return b.as_markup()


def search_results_kb(candidates) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for c in candidates:
        emoji = STATUS_EMOJI.get(c.status, "•")
        name = c.fullname if len(c.fullname) <= 20 else c.fullname[:19] + "…"
        b.row(
            InlineKeyboardButton(
                text=f"{c.application_number} · {name} · {emoji}",
                callback_data=f"card:{c.application_number}",
            )
        )
    b.row(InlineKeyboardButton(text="⬅️ Меню", callback_data="adm:menu"))
    return b.as_markup()
