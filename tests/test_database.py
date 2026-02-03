"""Tests for database module."""

from catch_stock_news.database import (
    add_keyword, delete_keyword, get_keywords, toggle_keyword,
    is_news_sent, is_similar_news_sent, mark_news_sent,
    save_alert, get_alerts, clear_all_alerts, cleanup_old_sent_news,
)


def test_add_and_get_keywords(app):
    assert add_keyword("삼성전자") is True
    assert add_keyword("현대차") is True

    keywords = get_keywords()
    names = [k["keyword"] for k in keywords]
    assert "삼성전자" in names
    assert "현대차" in names


def test_add_duplicate_keyword(app):
    add_keyword("삼성전자")
    assert add_keyword("삼성전자") is False


def test_delete_keyword(app):
    add_keyword("삭제용")
    keywords = get_keywords()
    kid = [k for k in keywords if k["keyword"] == "삭제용"][0]["id"]

    assert delete_keyword(kid) is True
    assert delete_keyword(9999) is False

    keywords = get_keywords()
    assert all(k["keyword"] != "삭제용" for k in keywords)


def test_toggle_keyword(app):
    add_keyword("토글용")
    keywords = get_keywords()
    kid = [k for k in keywords if k["keyword"] == "토글용"][0]["id"]

    assert toggle_keyword(kid) is False  # 1 -> 0
    assert toggle_keyword(kid) is True   # 0 -> 1
    assert toggle_keyword(9999) is None


def test_get_keywords_only_enabled(app):
    add_keyword("활성")
    add_keyword("비활성")
    keywords = get_keywords()
    kid = [k for k in keywords if k["keyword"] == "비활성"][0]["id"]
    toggle_keyword(kid)

    enabled = get_keywords(only_enabled=True)
    names = [k["keyword"] for k in enabled]
    assert "활성" in names
    assert "비활성" not in names


def test_mark_and_check_news_sent(app):
    assert is_news_sent("https://example.com/1") is False
    mark_news_sent("https://example.com/1", "뉴스 제목")
    assert is_news_sent("https://example.com/1") is True


def test_similar_news_detection(app):
    mark_news_sent("https://example.com/1", "삼성전자 실적 발표 예정")

    assert is_similar_news_sent("삼성전자 실적 발표 예정", threshold=0.8) is True
    assert is_similar_news_sent("삼성전자 실적 발표 예정일", threshold=0.8) is True
    assert is_similar_news_sent("완전히 다른 뉴스 제목입니다", threshold=0.8) is False


def test_save_and_get_alerts(app):
    save_alert(
        title="테스트 뉴스",
        url="https://example.com/1",
        matched_keywords=["삼성전자"],
        news_time="12:00",
        news_source="한국경제"
    )

    alerts = get_alerts()
    assert len(alerts) == 1
    assert alerts[0]["title"] == "테스트 뉴스"
    assert alerts[0]["matched_keywords"] == "삼성전자"
    assert alerts[0]["news_source"] == "한국경제"


def test_clear_all_alerts(app):
    save_alert("뉴스1", "https://a.com", ["키워드"], "12:00")
    save_alert("뉴스2", "https://b.com", ["키워드"], "12:01")

    deleted = clear_all_alerts()
    assert deleted == 2
    assert get_alerts() == []


def test_cleanup_old_sent_news(app):
    mark_news_sent("https://example.com/old", "오래된 뉴스")
    # 방금 추가한 것이므로 삭제되지 않아야 함
    deleted = cleanup_old_sent_news(days=7)
    assert deleted == 0
    assert is_news_sent("https://example.com/old") is True
