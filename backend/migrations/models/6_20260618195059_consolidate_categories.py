from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True

KEEP_SLUGS = "'technology','ai','business','science','health','politics','sports','general'"


async def upgrade(db: BaseDBAsyncClient) -> str:
    return f'''
        -- Move news from extra categories to general
        UPDATE news
        SET category_id = (
            SELECT id FROM categories WHERE slug = 'general'
        )
        WHERE category_id IN (
            SELECT id FROM categories
            WHERE slug NOT IN ({KEEP_SLUGS})
        );

        -- Remove extra categories
        DELETE FROM categories
        WHERE slug NOT IN ({KEEP_SLUGS});
    '''


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- Categories cannot be restored automatically after deletion
        SELECT 1;
    """
