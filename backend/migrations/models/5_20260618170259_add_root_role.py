from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return '''
        COMMENT ON COLUMN "users"."role" IS
        'user: user\nreviewer: reviewer\nadmin: admin\nroot: root';'''


async def downgrade(db: BaseDBAsyncClient) -> str:
    return '''
        COMMENT ON COLUMN "users"."role" IS
        'user: user\nreviewer: reviewer\nadmin: admin';'''
