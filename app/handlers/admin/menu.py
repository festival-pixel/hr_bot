from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.candidate import CandidateRepository
from app.keyboards.inline import admin_menu_kb, back_kb
from app.services.excel import build_candidates_xlsx

router = Router()

GREETING = "🛠 <b>Панель HR</b>\n\nВыберите действие:"


@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(GREETING, reply_markup=admin_menu_kb())


@router.callback_query(F.data == "adm:menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(GREETING, reply_markup=admin_menu_kb())
    await callback.answer()


@router.callback_query(F.data == "adm:stats")
async def show_stats(callback: CallbackQuery, session: AsyncSession):
    s = await CandidateRepository(session).stats()
    text = (
        "📊 <b>Статистика</b>\n\n"
        f"Всего заявок: <b>{s.get('total', 0)}</b>\n\n"
        f"🆕 Новые: {s.get('new', 0)}\n"
        f"✅ Приглашены: {s.get('invited', 0)}\n"
        f"📦 Архив: {s.get('archived', 0)}"
    )
    await callback.message.edit_text(text, reply_markup=back_kb())
    await callback.answer()


@router.callback_query(F.data == "adm:excel")
async def export_excel(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    candidates = await CandidateRepository(session).all()
    if not candidates:
        await callback.answer("Заявок пока нет", show_alert=True)
        return

    buffer = build_candidates_xlsx(candidates)
    document = BufferedInputFile(buffer.read(), filename="candidates.xlsx")
    await bot.send_document(
        callback.message.chat.id,
        document,
        caption=f"📥 Экспорт заявок ({len(candidates)})",
    )
    await callback.answer()


@router.callback_query(F.data == "noop")
async def noop(callback: CallbackQuery):
    await callback.answer()
