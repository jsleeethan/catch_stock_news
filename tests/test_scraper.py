"""Tests for scraper module."""

from catch_stock_news.scraper import convert_to_direct_news_url, find_matching_news
from catch_stock_news.models import NewsItem


def test_convert_news_read_url():
    url = "/news/news_read.naver?article_id=0005240919&office_id=015"
    result = convert_to_direct_news_url(url)
    assert result == "https://n.news.naver.com/mnews/article/015/0005240919"


def test_convert_already_direct_url():
    url = "https://n.news.naver.com/mnews/article/015/0005240919"
    assert convert_to_direct_news_url(url) == url


def test_convert_unrelated_url():
    url = "https://example.com/some/path"
    assert convert_to_direct_news_url(url) == url


def test_convert_missing_params():
    url = "/news/news_read.naver?something=else"
    assert convert_to_direct_news_url(url) == url


def test_find_matching_news_basic():
    items = [
        NewsItem(title="삼성전자 실적 발표", url="https://a.com", time="12:00", source="한국경제"),
        NewsItem(title="현대차 신차 출시", url="https://b.com", time="12:01", source="연합뉴스"),
        NewsItem(title="날씨 정보", url="https://c.com", time="12:02", source="기상청"),
    ]
    matched = find_matching_news(items, ["삼성전자", "현대차"])

    assert len(matched) == 2
    assert matched[0]["title"] == "삼성전자 실적 발표"
    assert matched[0]["matched_keywords"] == ["삼성전자"]
    assert matched[1]["matched_keywords"] == ["현대차"]


def test_find_matching_news_case_insensitive():
    items = [
        NewsItem(title="LG전자 신제품", url="https://a.com", time="12:00"),
    ]
    matched = find_matching_news(items, ["lg전자"])
    assert len(matched) == 1


def test_find_matching_news_multiple_keywords():
    items = [
        NewsItem(title="삼성전자 LG전자 실적 비교", url="https://a.com", time="12:00"),
    ]
    matched = find_matching_news(items, ["삼성전자", "LG전자"])
    assert len(matched) == 1
    assert set(matched[0]["matched_keywords"]) == {"삼성전자", "LG전자"}


def test_find_matching_news_no_match():
    items = [
        NewsItem(title="날씨 정보", url="https://a.com", time="12:00"),
    ]
    matched = find_matching_news(items, ["삼성전자"])
    assert matched == []
