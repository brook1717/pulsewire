from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # PostgreSQL — no safe default; must be provided via env
    DATABASE_URL: str

    # Telegram — required for publishing; no safe defaults
    TELEGRAM_BOT_TOKEN: SecretStr
    TELEGRAM_CHANNEL_ID: str

    # OpenAI — optional; empty string disables AI summarisation
    OPENAI_API_KEY: SecretStr = SecretStr("")

    # Scheduler
    SCHEDULER_INTERVAL_HOURS: int = 2

    # API security
    API_KEY: SecretStr = SecretStr("")

    # Logging
    LOG_LEVEL: str = "INFO"

    # ── Derived helpers ──────────────────────────────────────

    @property
    def openai_key(self) -> str | None:
        value = self.OPENAI_API_KEY.get_secret_value()
        return value if value else None

    @property
    def telegram_token(self) -> str:
        return self.TELEGRAM_BOT_TOKEN.get_secret_value()


settings = Settings()
