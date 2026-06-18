from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return '''
        ALTER TABLE "users" ADD "must_change_password" BOOL NOT NULL DEFAULT FALSE;'''


async def downgrade(db: BaseDBAsyncClient) -> str:
    return '''
        ALTER TABLE "users" DROP COLUMN "must_change_password";'''
