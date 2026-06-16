from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" ADD "role" VARCHAR(20) NOT NULL DEFAULT 'user';
        COMMENT ON COLUMN "users"."role" IS 'user: user\nreviewer: reviewer\nadmin: admin';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" DROP COLUMN "role";"""


MODELS_STATE = (
    "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"
    "ONZFSRWJHFBTpZS/I6l5eX/wGkx1Qu"
)
