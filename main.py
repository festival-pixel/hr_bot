import asyncio
import logging

from app.database.db import create_database
from app.handlers import router as main_router
from app.loader import bot, dp
from app.middlewares.block import BlockMiddleware
from app.middlewares.database import DbSessionMiddleware
from app.middlewares.user import UserMiddleware


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    await create_database()

    # DI: сессия БД → пользователь/язык → проверка блокировки
    dp.update.outer_middleware(DbSessionMiddleware())
    dp.update.outer_middleware(UserMiddleware())
    dp.update.outer_middleware(BlockMiddleware())

    dp.include_router(main_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен.")
