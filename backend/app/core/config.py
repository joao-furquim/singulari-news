from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_RESET_TOKEN_EXPIRE_MINUTES: int = 15
    REDIS_URL: str
    RESEND_API_KEY: str
    EMAIL_FROM: str
    R2_ACCOUNT_ID: str
    R2_ACCESS_KEY_ID: str
    R2_SECRET_ACCESS_KEY: str
    R2_BUCKET_NAME: str
    R2_PUBLIC_URL: str
    AI_API_KEY: str
    AI_MODEL: str = "claude-haiku-4-5-20251001"


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
