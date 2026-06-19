"""BullMQ-compatible publisher for the curator agent.

Writes article jobs directly to Redis using BullMQ's native key schema
(``bull:<queue>:<id>`` hash + ``bull:<queue>:wait`` list) so the NestJS
consumer can pick them up without any additional adapter.

Environment variables:
    REDIS_URL: Redis connection URL (default: ``redis://redis:6379``).
"""

import json
import logging
import os
import time

import redis

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
QUEUE_NAME = "news-processing"

_redis_client = redis.from_url(REDIS_URL)


def publish_to_queue(curated_article: dict) -> None:
    """Publish a classified article as a BullMQ job in Redis.

    Atomically increments the queue's job ID counter, writes the job
    metadata hash, and pushes the job ID onto the waiting list so BullMQ
    workers can dequeue it in FIFO order.

    The job is configured with 3 attempts and exponential back-off starting
    at 5 seconds, matching the consumer's retry strategy.

    :param curated_article: Dictionary representing the classified article.
        Must contain at minimum ``title``, ``source``, ``content``,
        ``published_at``, and ``category_slug`` keys.
    """
    job_id = str(_redis_client.incr(f"bull:{QUEUE_NAME}:id"))
    job_key = f"bull:{QUEUE_NAME}:{job_id}"

    _redis_client.hset(
        job_key,
        mapping={
            "id": job_id,
            "name": "process-news",
            "data": json.dumps(curated_article),
            "opts": json.dumps(
                {"attempts": 3, "backoff": {"type": "exponential", "delay": 5000}}
            ),
            "timestamp": int(time.time() * 1000),
            "attemptsMade": "0",
            "delay": "0",
            "priority": "0",
        },
    )
    _redis_client.lpush(f"bull:{QUEUE_NAME}:wait", job_id)
    logger.info(f"Article published to BullMQ queue: {job_id}")
