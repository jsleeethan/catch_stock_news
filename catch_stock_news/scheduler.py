"""APScheduler initialization."""

import atexit
import logging

from apscheduler.schedulers.background import BackgroundScheduler

from catch_stock_news.config import get_config

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def init_scheduler(job_func) -> None:
    """Initialize and start the scheduler.

    Args:
        job_func: The function to run periodically.
    """
    config = get_config()
    interval = config["check_interval"]

    scheduler.add_job(
        func=job_func,
        trigger="interval",
        minutes=interval,
        id="news_check_job",
        name=f"Check news every {interval} minute(s)",
        replace_existing=True,
        misfire_grace_time=120  # Allow up to 2 minutes late execution
    )
    scheduler.start()
    logger.info(f"Scheduler started - checking news every {interval} minute(s)")

    # Shut down scheduler when app exits
    atexit.register(lambda: scheduler.shutdown())
