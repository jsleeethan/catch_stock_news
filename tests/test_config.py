"""Tests for configuration module."""

import os


def test_get_config_defaults(monkeypatch):
    """Default values are returned when env vars are not set."""
    monkeypatch.delenv("CHECK_INTERVAL_MINUTES", raising=False)
    monkeypatch.delenv("NOTIFICATION_START_TIME", raising=False)
    monkeypatch.delenv("NOTIFICATION_END_TIME", raising=False)
    monkeypatch.delenv("ENABLE_WEEKEND_NOTIFICATIONS", raising=False)
    monkeypatch.delenv("ALLOWED_NEWS_SOURCES", raising=False)
    monkeypatch.delenv("TITLE_SIMILARITY_THRESHOLD", raising=False)
    monkeypatch.delenv("MAX_PAGES", raising=False)

    from catch_stock_news.config import get_config
    config = get_config()

    assert config["check_interval"] == 1
    assert config["notification_start"] == ""
    assert config["notification_end"] == ""
    assert config["enable_weekend"] is False
    assert config["allowed_sources"] == []
    assert config["similarity_threshold"] == 0.8
    assert config["max_pages"] == 3


def test_get_config_custom_values(monkeypatch):
    """Custom env var values are loaded correctly."""
    monkeypatch.setenv("CHECK_INTERVAL_MINUTES", "5")
    monkeypatch.setenv("NOTIFICATION_START_TIME", "09:00")
    monkeypatch.setenv("NOTIFICATION_END_TIME", "18:00")
    monkeypatch.setenv("ENABLE_WEEKEND_NOTIFICATIONS", "true")
    monkeypatch.setenv("ALLOWED_NEWS_SOURCES", "연합뉴스,한국경제")
    monkeypatch.setenv("TITLE_SIMILARITY_THRESHOLD", "0.9")
    monkeypatch.setenv("MAX_PAGES", "5")

    from catch_stock_news.config import get_config
    config = get_config()

    assert config["check_interval"] == 5
    assert config["notification_start"] == "09:00"
    assert config["notification_end"] == "18:00"
    assert config["enable_weekend"] is True
    assert config["allowed_sources"] == ["연합뉴스", "한국경제"]
    assert config["similarity_threshold"] == 0.9
    assert config["max_pages"] == 5
