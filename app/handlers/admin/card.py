from html import escape

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.candidate import CandidateRepository
from app.keyboards.inline import card_kb
from app.states.admin import AdminState
from app.utils.formatters import format_admin_card
from app.utils.notify import (
    notify_candidate_status,
    send_invitation,
    send_resume,
)

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
        reply_markup=card_kb(candidate),
    )

    if candidate.latitude and candidate.longitude:
        await bot.send_location(
            chat_id,
            latitude=candidate.latitude,
            longitude=candidate.longitude,
        )

    await send_resume(bot, chat_id, candidate)

    await callback.answer()


@router.callback_query(F.data.startswith("st:"))
async def change_status(
    callback: CallbackQuery,
    session: AsyncSession,
    bot: Bot,
    state: FSMContext,
):
    _, number, status = callback.data.split(":")
    repo = CandidateRepository(session)

    candidate = await repo.get_by_number(number)
    if candidate is None:
        await callback.answer("Заявка не найдена", show_alert=True)
        return

    # «Приглашён» → просим у админа дату собеседования (можно и повторно)
    if status == "invited":
        if candidate.status != "invited":
            candidate = await repo.update_status(number, "invited")
            await callback.message.edit_text(
                format_admin_card(candidate), reply_markup=card_kb(candidate)
            )
        await state.set_state(AdminState.invite_date)
        await state.update_data(invite_number=number)
        await callback.message.answer(
            f"✍️ Кандидат: <b>{escape(candidate.fullname)}</b>\n\n"
            "Введите <b>дату и время собеседования</b> "
            "(например: <i>28.07.2026, 14:00</i>).\n"
            "Адрес и локация добавятся автоматически и будут отправлены кандидату."
        )
        await callback.answer("Укажите дату собеседования 👇")
        return

    if candidate.status == status:
        await callback.answer("Уже в этом статусе")
        return

    candidate = await repo.update_status(number, status)
    await callback.message.edit_text(
        format_admin_card(candidate),
        reply_markup=card_kb(candidate),
    )

    if status == "rejected":
        notified = await notify_candidate_status(bot, candidate)
        suffix = "кандидат уведомлён ✅" if notified else "не удалось уведомить ⚠️"
        await callback.answer(f"Статус обновлён. {suffix}", show_alert=True)
    else:
        await callback.answer("Статус обновлён ✅")


@router.message(AdminState.invite_date, F.text)
async def set_invite_date(
    message: Message, state: FSMContext, session: AsyncSession, bot: Bot
):
    data = await state.get_data()
    number = data.get("invite_number")
    await state.clear()

    candidate = await CandidateRepository(session).get_by_number(number)
    if candidate is None:
        await message.answer("Заявка не найдена. Откройте карточку заново.")
        return

    date_text = message.text.strip()
    ok = await send_invitation(bot, candidate, date_text)
    if ok:
        await message.answer(
            f"✅ Приглашение отправлено кандидату <b>{escape(candidate.fullname)}</b>\n"
            f"📅 {escape(date_text)}\n"
            f"📍 Адрес и локация приложены."
        )
    else:
        await message.answer(
            "⚠️ Не удалось отправить приглашение "
            "(кандидат заблокировал бота или не запускал его)."
        )
