from html import escape

from app.constants import STATUS_NAMES, VACANCY_NAMES
from app.database.models import Candidate
from app.services.i18n import t


def short_name(fullname: str, limit: int = 22) -> str:
    fullname = fullname.strip()
    return fullname if len(fullname) <= limit else fullname[: limit - 1] + "…"


def format_confirmation(data: dict, lang: str) -> str:
    """Карточка анкеты для подтверждения кандидатом (локализованная)."""
    vacancy = VACANCY_NAMES[lang][data["vacancy"]]
    student = t(lang, "word_yes") if data["student"] else t(lang, "word_no")
    location = (
        t(lang, "location_attached")
        if data.get("latitude")
        else t(lang, "location_skipped")
    )
    resume = (
        t(lang, "resume_attached")
        if data.get("resume_file_id")
        else t(lang, "resume_none")
    )
    if data.get("has_children"):
        children = t(
            lang,
            "children_yes_fmt",
            count=data["children_count"],
            age=data["youngest_child_age"],
        )
    else:
        children = t(lang, "word_no")

    lines = [
        t(lang, "confirm_title"),
        "",
        f"🔹 <b>{t(lang, 'label_vacancy')}:</b> {vacancy}",
        f"🕒 <b>{t(lang, 'label_schedule')}:</b> {escape(data['schedule'])}",
        f"👤 <b>{t(lang, 'label_fullname')}:</b> {escape(data['fullname'])}",
        f"🎂 <b>{t(lang, 'label_age')}:</b> {data['age']}",
        f"📱 <b>{t(lang, 'label_phone')}:</b> {escape(data['phone'])}",
        f"🎓 <b>{t(lang, 'label_student')}:</b> {student}",
        f"💼 <b>{t(lang, 'label_experience')}:</b> {escape(data['experience'])}",
        f"🏢 <b>{t(lang, 'label_last_workplace')}:</b> {escape(data['last_workplace'])}",
        f"👶 <b>{t(lang, 'label_children')}:</b> {children}",
        f"🏠 <b>{t(lang, 'label_address')}:</b> {escape(data['address'])}",
        f"📍 <b>{t(lang, 'label_location')}:</b> {location}",
        f"🌐 <b>{t(lang, 'label_languages')}:</b> {escape(data['languages'])}",
        f"💬 <b>{t(lang, 'label_motivation')}:</b> {escape(data['motivation'])}",
        f"📄 <b>{t(lang, 'label_resume')}:</b> {resume}",
    ]
    return "\n".join(lines)


def format_admin_card(c: Candidate) -> str:
    """Полная карточка кандидата для HR (RU)."""
    student = "Да" if c.student else "Нет"
    location = "приложена" if c.latitude else "нет"
    if c.resume_file_id:
        resume = "🖼 фото" if c.resume_type == "photo" else "📄 документ"
    else:
        resume = "нет"
    username = f"@{c.username}" if c.username else "—"
    if c.has_children:
        children = f"Да (детей: {c.children_count}, младшему: {c.youngest_child_age})"
    else:
        children = "Нет"

    lines = [
        f"📋 <b>Заявка {c.application_number}</b>",
        f"Статус: {STATUS_NAMES.get(c.status, c.status)}",
        f"Дата: {c.created_at:%d.%m.%Y %H:%M}",
        "",
        f"🔹 <b>Вакансия:</b> {VACANCY_NAMES['ru'].get(c.vacancy, c.vacancy)}",
        f"🕒 <b>График:</b> {escape(c.schedule)}",
        f"👤 <b>ФИО:</b> {escape(c.fullname)}",
        f"🎂 <b>Возраст:</b> {c.age}",
        f"📱 <b>Телефон:</b> {escape(c.phone)}",
        f"🎓 <b>Студент:</b> {student}",
        f"💼 <b>Стаж:</b> {escape(c.experience)}",
        f"🏢 <b>Последнее место:</b> {escape(c.last_workplace)}",
        f"👶 <b>Дети:</b> {children}",
        f"🏠 <b>Адрес:</b> {escape(c.address)}",
        f"📍 <b>Геолокация:</b> {location}",
        f"🌐 <b>Языки:</b> {escape(c.languages)}",
        f"💬 <b>О себе:</b> {escape(c.motivation)}",
        f"📄 <b>Резюме:</b> {resume}",
        f"🔗 <b>Контакт:</b> {username}",
        f"🆔 <b>Telegram ID:</b> <code>{c.telegram_id}</code>",
    ]
    return "\n".join(lines)
