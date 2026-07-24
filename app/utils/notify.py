from html import escape

from aiogram import Bot

from app.config import settings
from app.constants import VACANCY_NAMES
from app.database.models import Candidate
from app.keyboards.inline import open_card_kb
from app.services.i18n import t
from app.utils.formatters import format_admin_card

# Статусы, о которых уведомляем кандидата, и ключ текста в локали
CANDIDATE_STATUS_MESSAGES = {
    "invited": "status_invited_msg",
    "rejected": "status_rejected_msg",
}


async def send_resume(bot: Bot, chat_id: int, candidate: Candidate) -> None:
    """Отправляет резюме нужным методом в зависимости от типа (фото/документ)."""
    if not candidate.resume_file_id:
        return
    caption = f"📄 Резюме {candidate.application_number}"
    try:
        if candidate.resume_type == "photo":
            await bot.send_photo(chat_id, candidate.resume_file_id, caption=caption)
        else:
            await bot.send_document(
                chat_id, candidate.resume_file_id, caption=caption
            )
    except Exception:
        pass


async def notify_candidate_status(bot: Bot, candidate: Candidate) -> bool:
    """Шлёт кандидату сообщение при статусе «приглашён»/«отказ». True — если доставлено."""
    key = CANDIDATE_STATUS_MESSAGES.get(candidate.status)
    if not key:
        return False

    lang = candidate.language or "ru"
    vacancy = VACANCY_NAMES.get(lang, VACANCY_NAMES["ru"]).get(
        candidate.vacancy, candidate.vacancy
    )
    text = t(
        lang,
        key,
        name=escape(candidate.fullname),
        number=candidate.application_number,
        vacancy=vacancy,
    )
    try:
        await bot.send_message(candidate.telegram_id, text)
        return True
    except Exception:
        # Кандидат заблокировал бота / удалил чат
        return False


async def notify_new_application(bot: Bot, candidate: Candidate) -> None:
    """Рассылает всем HR-админам уведомление о новой заявке (+ файл резюме)."""
    text = "🔔 <b>Новая заявка!</b>\n\n" + format_admin_card(candidate)

    for admin_id in settings.admin_ids:
        try:
            await bot.send_message(
                admin_id,
                text,
                reply_markup=open_card_kb(candidate.application_number),
            )
            # Резюме приходит сразу, без открытия карточки
            await send_resume(bot, admin_id, candidate)
        except Exception:
            # Админ ещё не запускал бота или заблокировал — не роняем поток кандидата
            continue
