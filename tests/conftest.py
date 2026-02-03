"""Shared test fixtures."""

import os
import pytest

os.environ.setdefault("SLACK_WEBHOOK_URL", "")
os.environ.setdefault("CHECK_INTERVAL_MINUTES", "1")

from catch_stock_news.database import init_db, DATABASE_PATH
from catch_stock_news.web import create_app


@pytest.fixture()
def app(tmp_path, monkeypatch):
    """Create a Flask test app with a temporary database."""
    db_path = str(tmp_path / "test.db")
    monkeypatch.setattr("catch_stock_news.database.DATABASE_PATH", db_path)
    init_db()

    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture()
def client(app):
    """Create a Flask test client."""
    return app.test_client()
