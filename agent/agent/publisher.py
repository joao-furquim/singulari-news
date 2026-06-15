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
    job_id = str(_redis_client.incr(f"bull:{QUEUE_NAME}:id"))
    job_key = f"bull:{QUEUE_NAME}:{job_id}"

    _redis_client.hset(job_key, mapping={
        "id": job_id,
        "name": "process-news",
        "data": json.dumps(curated_article),
        "opts": json.dumps({"attempts": 3, "backoff": {"type": "exponential", "delay": 5000}}),
        "timestamp": int(time.time() * 1000),
        "attemptsMade": "0",
        "delay": "0",
        "priority": "0",
    })
    _redis_client.lpush(f"bull:{QUEUE_NAME}:wait", job_id)
    logger.info(f"Article published to BullMQ queue: {job_id}")
