from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "news_queue" CASCADE;
        DROP TABLE IF EXISTS "user_favorites" CASCADE;
        DROP TABLE IF EXISTS "user_preferences" CASCADE;
        DROP TABLE IF EXISTS "password_resets" CASCADE;
        DROP TABLE IF EXISTS "news" CASCADE;
        DROP TABLE IF EXISTS "users" CASCADE;
        DROP TABLE IF EXISTS "categories" CASCADE;

        CREATE TABLE "categories" (
            "id" UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
            "name" VARCHAR(100) NOT NULL UNIQUE,
            "slug" VARCHAR(100) NOT NULL UNIQUE,
            "icon" VARCHAR(50),
            "description" TEXT,
            "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE "users" (
            "id" UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
            "name" VARCHAR(255) NOT NULL,
            "email" VARCHAR(255) NOT NULL UNIQUE,
            "password_hash" VARCHAR(255) NOT NULL,
            "avatar_url" VARCHAR(500),
            "locale" VARCHAR(10) NOT NULL DEFAULT \'pt-BR\',
            "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE "password_resets" (
            "id" UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
            "token" VARCHAR(500) NOT NULL UNIQUE,
            "is_used" BOOL NOT NULL DEFAULT False,
            "expires_at" TIMESTAMPTZ NOT NULL,
            "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            "user_id" UUID NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
        );
        CREATE TABLE "user_preferences" (
            "id" UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
            "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            "category_id" UUID NOT NULL REFERENCES "categories" ("id") ON DELETE CASCADE,
            "user_id" UUID NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
            CONSTRAINT "uid_user_prefer_user_id_bf0617" UNIQUE ("user_id", "category_id")
        );
        CREATE TABLE "news" (
            "id" UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
            "title" VARCHAR(500) NOT NULL,
            "source" VARCHAR(255) NOT NULL,
            "summary" TEXT,
            "content" TEXT NOT NULL,
            "published_at" TIMESTAMPTZ NOT NULL,
            "ai_generated" BOOL NOT NULL DEFAULT False,
            "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            "category_id" UUID NOT NULL REFERENCES "categories" ("id") ON DELETE CASCADE
        );
        CREATE TABLE "user_favorites" (
            "id" UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
            "saved_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            "news_id" UUID NOT NULL REFERENCES "news" ("id") ON DELETE CASCADE,
            "user_id" UUID NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
            CONSTRAINT "uid_user_favori_user_id_7bb691" UNIQUE ("user_id", "news_id")
        );
        CREATE TABLE "news_queue" (
            "id" UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
            "status" VARCHAR(50) NOT NULL DEFAULT \'pending\',
            "error_message" TEXT,
            "processed_at" TIMESTAMPTZ,
            "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            "news_id" UUID NOT NULL REFERENCES "news" ("id") ON DELETE CASCADE
        );"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
MODELS_STATE = (
    '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'
)
