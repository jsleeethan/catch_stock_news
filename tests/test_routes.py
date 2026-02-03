"""Tests for Flask routes."""


def test_index_page(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "증권 뉴스 키워드 알림" in resp.data.decode("utf-8")


def test_status_endpoint(client):
    resp = client.get("/status")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "scheduler_running" in data
    assert "webhook_configured" in data
    assert "keyword_count" in data
    assert "is_notification_time" in data


def test_add_keyword(client):
    resp = client.post("/keywords", json={"keyword": "테스트"})
    assert resp.status_code == 201
    assert "추가" in resp.get_json()["message"]


def test_add_empty_keyword(client):
    resp = client.post("/keywords", json={"keyword": ""})
    assert resp.status_code == 400


def test_add_long_keyword(client):
    resp = client.post("/keywords", json={"keyword": "a" * 101})
    assert resp.status_code == 400


def test_add_duplicate_keyword(client):
    client.post("/keywords", json={"keyword": "중복"})
    resp = client.post("/keywords", json={"keyword": "중복"})
    assert resp.status_code == 409


def test_list_keywords(client):
    client.post("/keywords", json={"keyword": "목록테스트"})
    resp = client.get("/keywords")
    assert resp.status_code == 200
    keywords = resp.get_json()
    names = [k["keyword"] for k in keywords]
    assert "목록테스트" in names


def test_toggle_keyword(client):
    client.post("/keywords", json={"keyword": "토글"})
    keywords = client.get("/keywords").get_json()
    kid = [k for k in keywords if k["keyword"] == "토글"][0]["id"]

    resp = client.post(f"/keywords/{kid}/toggle")
    assert resp.status_code == 200
    assert resp.get_json()["enabled"] is False

    resp = client.post(f"/keywords/{kid}/toggle")
    assert resp.get_json()["enabled"] is True


def test_toggle_nonexistent_keyword(client):
    resp = client.post("/keywords/9999/toggle")
    assert resp.status_code == 404


def test_delete_keyword(client):
    client.post("/keywords", json={"keyword": "삭제대상"})
    keywords = client.get("/keywords").get_json()
    kid = [k for k in keywords if k["keyword"] == "삭제대상"][0]["id"]

    resp = client.delete(f"/keywords/{kid}")
    assert resp.status_code == 200


def test_delete_nonexistent_keyword(client):
    resp = client.delete("/keywords/9999")
    assert resp.status_code == 404


def test_list_alerts(client):
    resp = client.get("/alerts")
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)


def test_clear_alerts(client):
    resp = client.delete("/alerts")
    assert resp.status_code == 200
    assert "삭제" in resp.get_json()["message"]
