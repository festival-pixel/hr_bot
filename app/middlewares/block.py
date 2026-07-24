from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update
from aiogram.types import User as TgUser

from app.config import settings
from app.database.repositories.block import BlockRepository
from app.services.i18n import t


class BlockMiddleware(BaseMiddleware):
    """Не пропускает заблокированных пользователей (кроме админов)."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        tg_user: TgUser | None = data.get("event_from_user")
        session = data.get("session")

        if (
            tg_user is not None
            and session is not None
            and tg_user.id not in settings.admin_ids
        ):
            if await BlockRepository(session).is_blocked(tg_user.id):
                lang = data.get("lang", "ru")
                text = t(lang, "blocked_msg")
                if isinstance(event, Update):
                    if event.message:
                        await event.message.answer(text)
                    elif event.callback_query:
                        await event.callback_query.answer(text, show_alert=True)
                return  # обрываем обработку

        return await handler(event, data)
