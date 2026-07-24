from datetime import datetime

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


MONTHS_RU = [
    "январь", "февраль", "март", "апрель", "май", "июнь", "июль",
    "август", "сентябрь", "октябрь", "ноябрь", "декабрь",
]


@router.callback_query(F.data == "adm:stats")
async def show_stats(callback: CallbackQuery, session: AsyncSession):
    s = await CandidateRepository(session).monthly_stats()
    now = datetime.utcnow()
    month = MONTHS_RU[now.month - 1]
    text = (
        f"📊 <b>Статистика за {month} {now.year}</b>\n\n"
        f"📥 Всего заявок за месяц: <b>{s.get('total', 0)}</b>\n\n"
        f"✅ Приглашено: {s.get('invited', 0)}\n"
        f"📦 В архиве: {s.get('archived', 0)}\n"
        f"❌ Отказов: {s.get('rejected', 0)}"
    )
    await callback.message.edit_text(text, reply_markup=back_kb())
    await callback.answer()


@router.callback_query(F.data == "adm:excel")
async def export_excel(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    # Экспорт за текущий 2-месячный период (сбрасывается каждые 2 месяца)
    candidates = await CandidateRepository(session).for_current_period()
    if not candidates:
        await callback.answer("За текущий период заявок нет", show_alert=True)
        return

    start = CandidateRepository.current_period_start()
    period = f"{MONTHS_RU[start.month - 1]}–{MONTHS_RU[start.month]} {start.year}"
    buffer = build_candidates_xlsx(candidates)
    document = BufferedInputFile(
        buffer.read(), filename=f"candidates_{start:%Y_%m}.xlsx"
    )
    await bot.send_document(
        callback.message.chat.id,
        document,
        caption=f"📥 Экспорт за период: {period} ({len(candidates)} заявок)",
    )
    await callback.answer()


@router.callback_query(F.data == "noop")
async def noop(callback: CallbackQuery):
    await callback.answer()
