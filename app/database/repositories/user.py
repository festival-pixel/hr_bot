from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, telegram_id: int) -> User | None:
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def get_or_create(
        self,
        telegram_id: int,
        username: str | None,
        first_name: str | None,
    ) -> User:
        user = await self.get(telegram_id)

        if user is None:
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
            )
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            return user

        # Обновляем контактные данные, если изменились
        changed = False
        if user.username != username:
            user.username = username
            changed = True
        if user.first_name != first_name:
            user.first_name = first_name
            changed = True
        if changed:
            await self.session.commit()

        return user

    async def set_language(self, telegram_id: int, language: str) -> None:
        user = await self.get(telegram_id)
        if user:
            user.language = language
            await self.session.commit()
