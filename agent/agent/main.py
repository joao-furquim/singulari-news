"""Entry point for the curator agent scheduler.

Loads environment configuration, sets up APScheduler with a fixed interval,
runs one immediate cycle on startup, then blocks indefinitely while the
scheduler fires subsequent cycles.

Environment variables:
    AGENT_SCHEDULER_INTERVAL_MINUTES: How often to run ``run_cycle()``
        (default: 5).
"""

import logging
import os

from agent.curator import process_inbox, refill_inbox
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

AGENT_SCHEDULER_INTERVAL_MINUTES = int(
    os.getenv("AGENT_SCHEDULER_INTERVAL_MINUTES", "5")
)


def run_cycle():
    """Execute one full curator cycle: refill inbox then process it.

    Calls :func:`agent.curator.refill_inbox` to move the next queued article
    into the inbox (if the inbox is empty), then calls
    :func:`agent.curator.process_inbox` to classify and publish every file
    currently in the inbox.
    """
    logger.info("Starting curator agent cycle")
    refill_inbox()
    process_inbox()
    logger.info("Cycle completed")


def main():
    """Start the blocking APScheduler and run the first cycle immediately.

    Registers :func:`run_cycle` on an interval job, fires it once before
    starting the scheduler loop so the agent processes any backlog on boot.
    """
    scheduler = BlockingScheduler()
    scheduler.add_job(
        run_cycle,
        "interval",
        minutes=AGENT_SCHEDULER_INTERVAL_MINUTES,
        id="curator_cycle",
    )
    logger.info(f"Agent started — interval: {AGENT_SCHEDULER_INTERVAL_MINUTES} min")
    run_cycle()
    scheduler.start()


if __name__ == "__main__":
    main()
