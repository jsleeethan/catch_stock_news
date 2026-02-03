"""Tests for news checker service."""

from catch_stock_news.services.news_checker import is_notification_time


def test_notification_time_no_window(monkeypatch):
    """No time window configured means always allow."""
    monkeypatch.delenv("NOTIFICATION_START_TIME", raising=False)
    monkeypatch.delenv("NOTIFICATION_END_TIME", raising=False)
    monkeypatch.setenv("ENABLE_WEEKEND_NOTIFICATIONS", "true")
    assert is_notification_time() is True


def test_notification_time_invalid_format(monkeypatch):
    """Invalid time format falls back to True."""
    monkeypatch.setenv("NOTIFICATION_START_TIME", "invalid")
    monkeypatch.setenv("NOTIFICATION_END_TIME", "also-invalid")
    monkeypatch.setenv("ENABLE_WEEKEND_NOTIFICATIONS", "true")
    assert is_notification_time() is True
