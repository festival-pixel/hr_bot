from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Candidate, StatEvent


class CandidateRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _next_number(self) -> str:
        result = await self.session.execute(select(func.count(Candidate.id)))
        count = result.scalar_one()
        return f"HR-{count + 1:06d}"

    async def create(self, **data) -> Candidate:
        number = await self._next_number()
        candidate = Candidate(application_number=number, **data)
        self.session.add(candidate)
        await self.session.commit()
        await self.session.refresh(candidate)
        return candidate

    async def get_by_number(self, number: str) -> Candidate | None:
        result = await self.session.execute(
            select(Candidate).where(Candidate.application_number == number)
        )
        return result.scalar_one_or_none()

    @staticmethod
    def _apply_filters(stmt, status: str, vacancy: str):
        if status and status != "all":
            stmt = stmt.where(Candidate.status == status)
        if vacancy and vacancy != "all":
            stmt = stmt.where(Candidate.vacancy == vacancy)
        return stmt

    async def list(
        self,
        status: str = "all",
        vacancy: str = "all",
        offset: int = 0,
        limit: int = 5,
    ) -> list[Candidate]:
        stmt = self._apply_filters(select(Candidate), status, vacancy)
        stmt = stmt.order_by(Candidate.id.desc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count(self, status: str = "all", vacancy: str = "all") -> int:
        stmt = self._apply_filters(
            select(func.count(Candidate.id)), status, vacancy
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def search(self, query: str, limit: int = 20) -> list[Candidate]:
        pattern = f"%{query.strip()}%"
        stmt = (
            select(Candidate)
            .where(
                Candidate.status == "new",
                or_(
                    Candidate.fullname.ilike(pattern),
                    Candidate.phone.ilike(pattern),
                ),
            )
            .order_by(Candidate.id.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_status(
        self, number: str, status: str
    ) -> Candidate | None:
        candidate = await self.get_by_number(number)
        if candidate:
            candidate.status = status
            await self.session.commit()
            await self.session.refresh(candidate)
        return candidate

    async def delete(self, number: str) -> bool:
        """Полностью удаляет заявку из БД. True — если запись существовала."""
        candidate = await self.get_by_number(number)
        if candidate is None:
            return False
        await self.session.delete(candidate)
        await self.session.commit()
        return True

    async def all(self) -> list[Candidate]:
        result = await self.session.execute(
            select(Candidate).order_by(Candidate.id.asc())
        )
        return list(result.scalars().all())

    async def log_event(self, event_type: str) -> None:
        """Фиксирует событие (invited/archived/rejected) для месячной статистики."""
        self.session.add(StatEvent(event_type=event_type))
        await self.session.commit()

    async def monthly_stats(self) -> dict[str, int]:
        """Статистика за текущий месяц (автосброс на границе месяца)."""
        now = datetime.utcnow()
        month_start = now.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )

        # Живые заявки, созданные в этом месяце (new/invited/archived)
        alive = await self.session.execute(
            select(func.count(Candidate.id)).where(
                Candidate.created_at >= month_start
            )
        )
        alive_count = alive.scalar_one()

        # События этого месяца (в т.ч. отказы — уже удалённые заявки)
        events = await self.session.execute(
            select(StatEvent.event_type, func.count(StatEvent.id))
            .where(StatEvent.created_at >= month_start)
            .group_by(StatEvent.event_type)
        )
        ev = {t: c for t, c in events.all()}
        rejected = ev.get("rejected", 0)

        return {
            "total": alive_count + rejected,
            "invited": ev.get("invited", 0),
            "archived": ev.get("archived", 0),
            "rejected": rejected,
        }
