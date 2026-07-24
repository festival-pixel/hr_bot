from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Candidate


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
                or_(
                    Candidate.fullname.ilike(pattern),
                    Candidate.phone.ilike(pattern),
                )
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

    async def stats(self) -> dict[str, int]:
        result = await self.session.execute(
            select(Candidate.status, func.count(Candidate.id)).group_by(
                Candidate.status
            )
        )
        counts = {status: cnt for status, cnt in result.all()}
        counts["total"] = sum(counts.values())
        return counts
