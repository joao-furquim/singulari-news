from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # ── Required ─────────────────────────────────────────────────────────────
    DATABASE_URL: str
    JWT_SECRET_KEY: str

    # ── Optional with safe defaults ───────────────────────────────────────────
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_RESET_TOKEN_EXPIRE_MINUTES: int = 15

    # Redis — required for BullMQ but defaults to Docker Compose service name
    REDIS_URL: str = "redis://redis:6379"

    # AI summary generation — empty = consumer falls back to first 2 sentences
    AI_API_KEY: str = ""
    AI_MODEL: str = "gemini-2.0-flash-lite"

    # Email — empty = password-reset emails are logged to stdout only
    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = "onboarding@resend.dev"

    # Agent hotfolder paths
    AGENT_SCHEDULER_INTERVAL_MINUTES: int = 5
    AGENT_QUEUE_PATH: str = "data/queue"
    AGENT_INBOX_PATH: str = "data/inbox"
    AGENT_PROCESSED_PATH: str = "data/processed"


settings = Settings()

TORTOISE_ORM = {
    "connections": {"default": settings.DATABASE_URL},
    "apps": {
        "models": {
            "models": [
                "app.models.user",
                "app.models.category",
                "app.models.news",
                "aerich.models",
            ],
            "default_connection": "default",
        }
    },
}
