from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.candidate import CandidateRepository
from app.keyboards.inline import card_kb
from app.utils.formatters import format_admin_card

router = Router()


@router.callback_query(F.data.startswith("card:"))
async def open_card(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    number = callback.data.split(":", 1)[1]
    candidate = await CandidateRepository(session).get_by_number(number)
    if candidate is None:
        await callback.answer("Заявка не найдена", show_alert=True)
        return

    chat_id = callback.message.chat.id
    await bot.send_message(
        chat_id,
        format_admin_card(candidate),
        reply_markup=card_kb(candidate.application_number, candidate.status),
    )

    if candidate.latitude and candidate.longitude:
        await bot.send_location(
            chat_id,
            latitude=candidate.latitude,
            longitude=candidate.longitude,
        )

    if candidate.resume_file_id:
        try:
            await bot.send_document(
                chat_id,
                candidate.resume_file_id,
                caption=f"📄 Резюме {candidate.application_number}",
            )
        except Exception:
            pass

    await callback.answer()


@router.callback_query(F.data.startswith("st:"))
async def change_status(callback: CallbackQuery, session: AsyncSession):
    _, number, status = callback.data.split(":")
    candidate = await CandidateRepository(session).update_status(number, status)
    if candidate is None:
        await callback.answer("Заявка не найдена", show_alert=True)
        return

    await callback.message.edit_text(
        format_admin_card(candidate),
        reply_markup=card_kb(candidate.application_number, candidate.status),
    )
    await callback.answer("Статус обновлён ✅")
