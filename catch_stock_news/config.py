"""Configuration management from environment variables."""

import os


def get_config() -> dict:
    """Get configuration from environment variables."""
    return {
        "check_interval": int(os.environ.get("CHECK_INTERVAL_MINUTES", 1)),
        "notification_start": os.environ.get("NOTIFICATION_START_TIME", ""),
        "notification_end": os.environ.get("NOTIFICATION_END_TIME", ""),
        "enable_weekend": os.environ.get("ENABLE_WEEKEND_NOTIFICATIONS", "false").lower() == "true",
        "allowed_sources": [s.strip() for s in os.environ.get("ALLOWED_NEWS_SOURCES", "").split(",") if s.strip()],
        "similarity_threshold": float(os.environ.get("TITLE_SIMILARITY_THRESHOLD", 0.8)),
        "max_pages": int(os.environ.get("MAX_PAGES", 3)),
    }
