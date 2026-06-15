from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "users" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "email" VARCHAR(255) NOT NULL UNIQUE,
    "password_hash" VARCHAR(255) NOT NULL,
    "avatar_url" VARCHAR(500),
    "locale" VARCHAR(10) NOT NULL DEFAULT \'pt-BR\',
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "password_resets" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "token" VARCHAR(500) NOT NULL UNIQUE,
    "is_used" BOOL NOT NULL DEFAULT False,
    "expires_at" TIMESTAMPTZ NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "categories" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(100) NOT NULL UNIQUE,
    "slug" VARCHAR(100) NOT NULL UNIQUE,
    "icon" VARCHAR(50),
    "description" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "user_preferences" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "category_id" INT NOT NULL REFERENCES "categories" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_user_prefer_user_id_bf0617" UNIQUE ("user_id", "category_id")
);
CREATE TABLE IF NOT EXISTS "news" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(500) NOT NULL,
    "source" VARCHAR(255) NOT NULL,
    "summary" TEXT,
    "content" TEXT NOT NULL,
    "published_at" TIMESTAMPTZ NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "category_id" INT NOT NULL REFERENCES "categories" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "user_favorites" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "saved_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "news_id" INT NOT NULL REFERENCES "news" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_user_favori_user_id_7bb691" UNIQUE ("user_id", "news_id")
);
CREATE TABLE IF NOT EXISTS "news_queue" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "status" VARCHAR(50) NOT NULL DEFAULT \'pending\',
    "error_message" TEXT,
    "processed_at" TIMESTAMPTZ,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "news_id" INT NOT NULL REFERENCES "news" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "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"
    "VtK6U="
)
