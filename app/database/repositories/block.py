from sqlalchemy import delete as sql_delete
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import BlockedUser


class BlockRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def is_blocked(self, telegram_id: int) -> bool:
        result = await self.session.execute(
            select(BlockedUser.id).where(BlockedUser.telegram_id == telegram_id)
        )
        return result.first() is not None

    async def block(self, telegram_id: int) -> None:
        if not await self.is_blocked(telegram_id):
            self.session.add(BlockedUser(telegram_id=telegram_id))
            await self.session.commit()

    async def unblock(self, telegram_id: int) -> None:
        await self.session.execute(
            sql_delete(BlockedUser).where(BlockedUser.telegram_id == telegram_id)
        )
        await self.session.commit()
