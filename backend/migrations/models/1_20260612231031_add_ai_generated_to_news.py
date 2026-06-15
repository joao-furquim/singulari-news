from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "news" ADD "ai_generated" BOOL NOT NULL DEFAULT False;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "news" DROP COLUMN "ai_generated";"""


MODELS_STATE = (
    "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"
    "4XextJxyIhe0QFvawteZ/by8v/uW2ajg=="
)
