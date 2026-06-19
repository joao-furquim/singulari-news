"""Hotfolder-based article pipeline for the curator agent.

Manages three directories that articles move through sequentially:

- ``queue/``     — raw JSON files waiting to be processed (source)
- ``inbox/``     — the single file currently being worked on
- ``processed/`` — successfully processed files (archive)

:func:`refill_inbox` and :func:`process_inbox` are called together in each
scheduler cycle.  Processing one file per cycle keeps memory usage bounded
and allows the scheduler to stay responsive.

Environment variables:
    AGENT_INBOX_PATH:     Path to the inbox directory (default: ``data/inbox``).
    AGENT_QUEUE_PATH:     Path to the queue directory (default: ``data/queue``).
    AGENT_PROCESSED_PATH: Path to the processed archive (default: ``data/processed``).
"""

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
    """Move one article file from the queue into the inbox if the inbox is empty.

    Ensures the directories exist, then checks whether the inbox already
    contains pending files.  If the inbox is empty and the queue has files,
    the lexicographically first file in the queue is moved to the inbox so
    that the next :func:`process_inbox` call can handle it.

    Does nothing when:
    - The inbox already contains one or more files.
    - Both the inbox and the queue are empty.
    """
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
    """Process all JSON files currently in the inbox directory.

    For each file found in the inbox:

    1. Reads and parses the JSON content (supports both a single article
       dict and a list of article dicts in the same file).
    2. Calls :func:`agent.classifier.classify_article` on each article to
       assign a ``category_slug``.
    3. Calls :func:`agent.publisher.publish_to_queue` to enqueue the
       classified article in BullMQ via Redis.
    4. Moves the file to ``processed/`` on success.

    Errors during individual file processing are caught and logged; the file
    remains in the inbox so it can be retried or inspected manually.
    """
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
