import json
import logging
import os
import shutil
from pathlib import Path

from agent.classifier import classify_article
from agent.publisher import publish_to_queue

logger = logging.getLogger(__name__)

inbox_path = Path(os.getenv("AGENT_INBOX_PATH", "data/inbox"))
queue_path = Path(os.getenv("AGENT_QUEUE_PATH", "data/queue"))
processed_path = Path(os.getenv("AGENT_PROCESSED_PATH", "data/processed"))


def refill_inbox() -> None:
    inbox_path.mkdir(parents=True, exist_ok=True)
    queue_path.mkdir(parents=True, exist_ok=True)

    pending_articles = sorted(inbox_path.glob("*.json"))
    is_inbox_empty = len(pending_articles) == 0

    if not is_inbox_empty:
        return

    queue_files = sorted(queue_path.glob("*.json"))
    has_pending_articles = len(queue_files) > 0

    if not has_pending_articles:
        logger.info("Queue is empty — no articles to process")
        return

    first_article_file = queue_files[0]
    shutil.move(str(first_article_file), str(inbox_path / first_article_file.name))
    logger.info(f"Article moved to inbox: {first_article_file.name}")


def process_inbox() -> None:
    inbox_path.mkdir(parents=True, exist_ok=True)
    processed_path.mkdir(parents=True, exist_ok=True)

    pending_articles = sorted(inbox_path.glob("*.json"))
    has_pending_articles = len(pending_articles) > 0

    if not has_pending_articles:
        logger.info("Inbox is empty")
        return

    for article_file in pending_articles:
        try:
            raw_content = article_file.read_text(encoding="utf-8")
            article_data = json.loads(raw_content)

            # Support both single article (dict) and batch (list)
            raw_articles = (
                article_data if isinstance(article_data, list) else [article_data]
            )

            for raw_article in raw_articles:
                curated_article = classify_article(raw_article)
                publish_to_queue(curated_article)

            shutil.move(str(article_file), str(processed_path / article_file.name))
            logger.info(f"Processed {article_file.name} ({len(raw_articles)} articles)")
        except Exception as error:
            logger.error(f"Failed to process {article_file.name}: {error}")
