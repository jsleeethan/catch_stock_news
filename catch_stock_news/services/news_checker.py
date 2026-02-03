"""News checking service - core business logic."""

import logging
import traceback
from datetime import datetime

from catch_stock_news.config import get_config
from catch_stock_news.database import (
    get_keywords, is_news_sent, is_similar_news_sent,
    mark_news_sent, save_alert, cleanup_old_sent_news
)
from catch_stock_news.scraper import fetch_realtime_news, find_matching_news
from catch_stock_news.notifier import send_slack_notification, send_error_notification

logger = logging.getLogger(__name__)


def is_notification_time() -> bool:
    """Check if current time is within notification window."""
    config = get_config()

    now = datetime.now()

    # Check weekend
    if not config["enable_weekend"] and now.weekday() >= 5:
        logger.debug("Weekend notifications disabled")
        return False

    # Check time window
    start_str = config["notification_start"]
    end_str = config["notification_end"]

    if not start_str or not end_str:
        return True  # No time restriction

    try:
        start_time = datetime.strptime(start_str, "%H:%M").time()
        end_time = datetime.strptime(end_str, "%H:%M").time()
        current_time = now.time()

        if start_time <= current_time <= end_time:
            return True
        else:
            logger.debug(f"Outside notification window ({start_str} - {end_str})")
            return False
    except ValueError as e:
        logger.warning(f"Invalid time format in config: {e}")
        return True


def check_news_job():
    """Background job to check for news matching keywords."""
    logger.info("Running news check...")

    config = get_config()

    # Get only enabled keywords
    keywords_data = get_keywords(only_enabled=True)
    if not keywords_data:
        logger.info("No enabled keywords configured. Skipping check.")
        return

    keywords = [k["keyword"] for k in keywords_data]

    try:
        # Fetch latest news with source filter and multi-page support
        allowed_sources = config["allowed_sources"] if config["allowed_sources"] else None
        news_items = fetch_realtime_news(
            allowed_sources=allowed_sources,
            max_pages=config["max_pages"]
        )
        logger.info(f"Fetched {len(news_items)} news items.")

        if not news_items:
            return

        # Find matching news
        matched_news = find_matching_news(news_items, keywords)
        logger.info(f"Found {len(matched_news)} matching news items.")

        # Check if we should send notifications
        should_notify = is_notification_time()

        # Send notifications for new matches
        for news in matched_news:
            # Check URL duplicate
            if is_news_sent(news["url"]):
                logger.debug(f"Already sent (URL): {news['title'][:50]}...")
                continue

            # Check title similarity
            if is_similar_news_sent(news["title"], config["similarity_threshold"]):
                logger.debug(f"Already sent (similar title): {news['title'][:50]}...")
                continue

            # Save to database for web UI
            save_alert(
                title=news["title"],
                url=news["url"],
                matched_keywords=news["matched_keywords"],
                news_time=news["time"],
                news_source=news.get("source", "")
            )

            # Send Slack notification only during notification hours
            if should_notify:
                send_slack_notification(news)
                logger.info(f"Sent notification for: {news['title'][:50]}...")
            else:
                logger.info(f"Saved (outside notification hours): {news['title'][:50]}...")

            # Mark as sent with title for similarity check
            mark_news_sent(news["url"], news["title"])

        # Cleanup old records periodically
        cleanup_old_sent_news(days=7)

    except Exception as e:
        error_msg = f"Error during news check: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        send_error_notification(error_msg, traceback.format_exc())
