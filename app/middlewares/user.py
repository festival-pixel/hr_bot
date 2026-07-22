from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from aiogram.types import User as TgUser

from app.database.repositories.user import UserRepository


class UserMiddleware(BaseMiddleware):
    """Загружает/создаёт пользователя и прокидывает user + lang в хендлеры."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        tg_user: TgUser | None = data.get("event_from_user")
        session = data.get("session")

        if tg_user is not None and not tg_user.is_bot and session is not None:
            repo = UserRepository(session)
            user = await repo.get_or_create(
                telegram_id=tg_user.id,
                username=tg_user.username,
                first_name=tg_user.first_name,
            )
            data["user"] = user
            data["lang"] = user.language
        else:
            data["lang"] = "ru"

        return await handler(event, data)
