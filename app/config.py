from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Типизированный конфиг, читается из .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    bot_token: str
    # Один или несколько ID через запятую: ADMIN_ID=111,222,333
    admin_id: str = "0"

    db_user: str = "postgres"
    db_password: str = "postgres"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "hr_bot_db"

    debug: bool = False

    @computed_field
    @property
    def admin_ids(self) -> list[int]:
        return [
            int(part.strip())
            for part in self.admin_id.split(",")
            if part.strip() and part.strip() != "0"
        ]

    @computed_field
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()
