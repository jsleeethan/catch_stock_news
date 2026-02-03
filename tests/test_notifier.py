"""Tests for notifier module."""

from catch_stock_news.notifier import get_webhook_url


def test_get_webhook_url_empty(monkeypatch):
    monkeypatch.delenv("SLACK_WEBHOOK_URL", raising=False)
    assert get_webhook_url() == ""


def test_get_webhook_url_set(monkeypatch):
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://hooks.slack.com/test")
    assert get_webhook_url() == "https://hooks.slack.com/test"
