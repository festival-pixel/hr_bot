from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    """Пользователь Telegram (заполняется на /start)."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, index=True
    )
    username: Mapped[str | None] = mapped_column(String(100), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    language: Mapped[str] = mapped_column(String(2), default="ru")

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )


class Candidate(Base):
    """Заявка кандидата на вакансию."""

    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(primary_key=True)

    application_number: Mapped[str] = mapped_column(String(20), unique=True)

    # Telegram
    telegram_id: Mapped[int] = mapped_column(BigInteger, index=True)
    username: Mapped[str | None] = mapped_column(String(100), nullable=True)
    language: Mapped[str] = mapped_column(String(2), default="ru")

    # Вакансия
    vacancy: Mapped[str] = mapped_column(String(50))
    schedule: Mapped[str] = mapped_column(String(50))

    # Личные данные
    fullname: Mapped[str] = mapped_column(String(255))
    age: Mapped[int] = mapped_column(Integer)
    phone: Mapped[str] = mapped_column(String(30))
    student: Mapped[bool] = mapped_column(Boolean, default=False)

    # Опыт работы
    experience: Mapped[str] = mapped_column(String(255))
    last_workplace: Mapped[str] = mapped_column(String(255))

    # Дети
    has_children: Mapped[bool] = mapped_column(Boolean, default=False)
    children_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    youngest_child_age: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )

    address: Mapped[str] = mapped_column(String(255))
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    languages: Mapped[str] = mapped_column(String(255))
    motivation: Mapped[str] = mapped_column(Text)

    # Резюме (Telegram file_id) + тип: "document" | "photo"
    resume_file_id: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )
    resume_type: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Статус обработки
    status: Mapped[str] = mapped_column(String(30), default="new", index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class BlockedUser(Base):
    """Заблокированные пользователи (не могут пользоваться ботом)."""

    __tablename__ = "blocked_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )


class StatEvent(Base):
    """Журнал событий для месячной статистики (переживает удаление заявок)."""

    __tablename__ = "stat_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_type: Mapped[str] = mapped_column(String(20), index=True)  # invited/archived/rejected
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, index=True
    )
