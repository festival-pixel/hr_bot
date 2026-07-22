from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.user import UserRepository
from app.keyboards.inline import language_kb, vacancy_kb
from app.services.i18n import t

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, lang: str):
    await state.clear()
    await message.answer(t(lang, "welcome"), reply_markup=language_kb())


@router.callback_query(F.data.startswith("lang:"))
async def choose_language(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await state.clear()
    lang = callback.data.split(":", 1)[1]
    await UserRepository(session).set_language(callback.from_user.id, lang)

    await callback.message.edit_text(t(lang, "language_selected"))
    await callback.message.answer(
        t(lang, "choose_vacancy"), reply_markup=vacancy_kb(lang)
    )
    await callback.answer()
