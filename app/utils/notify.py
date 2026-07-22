from aiogram import Bot

from app.config import settings
from app.database.models import Candidate
from app.keyboards.inline import open_card_kb
from app.utils.formatters import format_admin_card


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
            if candidate.resume_file_id:
                await bot.send_document(
                    admin_id,
                    candidate.resume_file_id,
                    caption=f"📄 Резюме {candidate.application_number}",
                )
        except Exception:
            # Админ ещё не запускал бота или заблокировал — не роняем поток кандидата
            continue
