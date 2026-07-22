from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.candidate import CandidateRepository
from app.keyboards.inline import back_kb, search_results_kb
from app.states.admin import AdminState

router = Router()


@router.callback_query(F.data == "adm:search")
async def ask_search(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminState.search_query)
    await callback.message.edit_text(
        "🔎 Введите <b>ФИО</b> или <b>номер телефона</b> для поиска:",
        reply_markup=back_kb(),
    )
    await callback.answer()


@router.message(AdminState.search_query, F.text)
async def do_search(message: Message, state: FSMContext, session: AsyncSession):
    query = message.text.strip()
    await state.clear()

    results = await CandidateRepository(session).search(query)
    if not results:
        await message.answer(
            f"По запросу «{query}» ничего не найдено.", reply_markup=back_kb()
        )
        return

    await message.answer(
        f"🔎 Результаты по «{query}» — найдено {len(results)}:",
        reply_markup=search_results_kb(results),
    )
