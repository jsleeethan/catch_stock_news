"""Tests for data models."""

from catch_stock_news.models import NewsItem


def test_news_item_creation():
    item = NewsItem(title="테스트 뉴스", url="https://example.com", time="12:00")
    assert item.title == "테스트 뉴스"
    assert item.url == "https://example.com"
    assert item.time == "12:00"
    assert item.source == ""


def test_news_item_with_source():
    item = NewsItem(title="뉴스", url="https://example.com", time="12:00", source="한국경제")
    assert item.source == "한국경제"
