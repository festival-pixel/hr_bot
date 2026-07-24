from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import VACANCY_NAMES
from app.database.repositories.candidate import CandidateRepository
from app.keyboards.inline import PAGE_SIZE, list_kb

router = Router()


def _title(vacancy: str, total: int) -> str:
    v = "все вакансии" if vacancy == "all" else VACANCY_NAMES["ru"].get(vacancy, vacancy)
    return (
        "🆕 <b>Новые заявки</b>\n"
        f"Вакансия: {v}\n"
        f"Найдено: <b>{total}</b>"
    )


async def _render(
    callback: CallbackQuery,
    session: AsyncSession,
    vacancy: str,
    offset: int,
):
    repo = CandidateRepository(session)
    # В списке — только новые заявки (NEW)
    total = await repo.count("new", vacancy)
    candidates = await repo.list("new", vacancy, offset, PAGE_SIZE)

    text = _title(vacancy, total)
    if not candidates:
        text += "\n\n<i>Новых заявок нет.</i>"

    await callback.message.edit_text(
        text, reply_markup=list_kb(candidates, "new", vacancy, offset, total)
    )
    await callback.answer()


@router.callback_query(F.data == "adm:list")
async def open_list(callback: CallbackQuery, session: AsyncSession):
    await _render(callback, session, "all", 0)


@router.callback_query(F.data.startswith("L:"))
async def paginate(callback: CallbackQuery, session: AsyncSession):
    _, _status, vacancy, offset = callback.data.split(":")
    await _render(callback, session, vacancy, int(offset))
