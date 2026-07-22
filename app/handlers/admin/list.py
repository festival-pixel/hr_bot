from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import STATUS_NAMES, VACANCY_NAMES
from app.database.repositories.candidate import CandidateRepository
from app.keyboards.inline import PAGE_SIZE, list_kb

router = Router()


def _title(status: str, vacancy: str, total: int) -> str:
    s = "Все" if status == "all" else STATUS_NAMES.get(status, status)
    v = "Все" if vacancy == "all" else VACANCY_NAMES["ru"].get(vacancy, vacancy)
    return (
        "📋 <b>Заявки</b>\n"
        f"Статус: {s} · Вакансия: {v}\n"
        f"Найдено: <b>{total}</b>"
    )


async def _render(
    callback: CallbackQuery,
    session: AsyncSession,
    status: str,
    vacancy: str,
    offset: int,
):
    repo = CandidateRepository(session)
    total = await repo.count(status, vacancy)
    candidates = await repo.list(status, vacancy, offset, PAGE_SIZE)

    text = _title(status, vacancy, total)
    if not candidates:
        text += "\n\n<i>Заявок не найдено.</i>"

    await callback.message.edit_text(
        text, reply_markup=list_kb(candidates, status, vacancy, offset, total)
    )
    await callback.answer()


@router.callback_query(F.data == "adm:list")
async def open_list(callback: CallbackQuery, session: AsyncSession):
    await _render(callback, session, "all", "all", 0)


@router.callback_query(F.data.startswith("L:"))
async def paginate(callback: CallbackQuery, session: AsyncSession):
    _, status, vacancy, offset = callback.data.split(":")
    await _render(callback, session, status, vacancy, int(offset))
