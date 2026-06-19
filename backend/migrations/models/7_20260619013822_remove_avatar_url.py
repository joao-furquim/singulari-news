from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return '''
        ALTER TABLE "users" DROP COLUMN IF EXISTS "avatar_url";'''


async def downgrade(db: BaseDBAsyncClient) -> str:
    return '''
        ALTER TABLE "users" ADD "avatar_url" VARCHAR(500);'''
