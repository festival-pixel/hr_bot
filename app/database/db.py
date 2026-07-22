from app.database.models import Base
from app.database.session import engine


async def create_database() -> None:
    """Создаёт таблицы, если их ещё нет."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
