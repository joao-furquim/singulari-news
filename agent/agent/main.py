import logging
import os

from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv

from agent.curator import process_inbox, refill_inbox

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

AGENT_SCHEDULER_INTERVAL_MINUTES = int(os.getenv("AGENT_SCHEDULER_INTERVAL_MINUTES", "5"))


def run_cycle():
    logger.info("Starting curator agent cycle")
    refill_inbox()
    process_inbox()
    logger.info("Cycle completed")


def main():
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
