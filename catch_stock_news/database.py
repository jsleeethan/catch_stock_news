"""SQLite database management for keywords and sent news tracking."""

import sqlite3
from datetime import datetime
from typing import List, Optional
from difflib import SequenceMatcher

DATABASE_PATH = "news_alerts.db"


def get_connection() -> sqlite3.Connection:
    """Get a database connection."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize the database tables."""
    conn = get_connection()
    cursor = conn.cursor()

    # Keywords table with enabled flag
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS keywords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT NOT NULL UNIQUE,
            enabled INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Add enabled column if it doesn't exist (for migration)
    try:
        cursor.execute("ALTER TABLE keywords ADD COLUMN enabled INTEGER DEFAULT 1")
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Sent news table for duplicate prevention
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sent_news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            news_url TEXT NOT NULL,
            news_title TEXT,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Add news_title column if it doesn't exist (for migration)
    try:
        cursor.execute("ALTER TABLE sent_news ADD COLUMN news_title TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Create unique index on news_url to prevent duplicates
    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_sent_news_url ON sent_news(news_url)
    """)

    # Create index for faster title search
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_sent_news_title ON sent_news(news_title)
    """)

    # Alerts table for storing matched news history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            matched_keywords TEXT NOT NULL,
            news_time TEXT,
            news_source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Add news_source column if it doesn't exist (for migration)
    try:
        cursor.execute("ALTER TABLE alerts ADD COLUMN news_source TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists

    conn.commit()
    conn.close()


def add_keyword(keyword: str) -> bool:
    """Add a new keyword. Returns True if successful, False if already exists."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO keywords (keyword, enabled) VALUES (?, 1)", (keyword.strip(),))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def delete_keyword(keyword_id: int) -> bool:
    """Delete a keyword by ID. Returns True if deleted, False if not found."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM keywords WHERE id = ?", (keyword_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()

    return deleted


def toggle_keyword(keyword_id: int) -> Optional[bool]:
    """Toggle keyword enabled status. Returns new status or None if not found."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT enabled FROM keywords WHERE id = ?", (keyword_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return None

    new_status = 0 if row["enabled"] else 1
    cursor.execute("UPDATE keywords SET enabled = ? WHERE id = ?", (new_status, keyword_id))
    conn.commit()
    conn.close()

    return bool(new_status)


def get_keywords(only_enabled: bool = False) -> List[dict]:
    """Get all keywords. If only_enabled is True, return only enabled keywords."""
    conn = get_connection()
    cursor = conn.cursor()

    if only_enabled:
        cursor.execute("SELECT id, keyword, enabled, created_at FROM keywords WHERE enabled = 1 ORDER BY created_at DESC")
    else:
        cursor.execute("SELECT id, keyword, enabled, created_at FROM keywords ORDER BY created_at DESC")

    keywords = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return keywords


def is_news_sent(news_url: str) -> bool:
    """Check if a news URL has already been sent."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM sent_news WHERE news_url = ?", (news_url,))
    exists = cursor.fetchone() is not None
    conn.close()

    return exists


def is_similar_news_sent(news_title: str, threshold: float = 0.8) -> bool:
    """Check if a similar news title has already been sent."""
    conn = get_connection()
    cursor = conn.cursor()

    # Get recent titles (last 24 hours worth, approximately 1000 items)
    cursor.execute("""
        SELECT news_title FROM sent_news
        WHERE news_title IS NOT NULL
        ORDER BY sent_at DESC
        LIMIT 1000
    """)
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        if row["news_title"]:
            similarity = SequenceMatcher(None, news_title, row["news_title"]).ratio()
            if similarity >= threshold:
                return True

    return False


def mark_news_sent(news_url: str, news_title: str = None) -> None:
    """Mark a news URL as sent."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO sent_news (news_url, news_title) VALUES (?, ?)",
            (news_url, news_title)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # Already exists
    finally:
        conn.close()


def cleanup_old_sent_news(days: int = 7) -> int:
    """Remove sent news records older than specified days. Returns count of deleted records."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM sent_news
        WHERE sent_at < datetime('now', ? || ' days')
    """, (f"-{days}",))

    deleted = cursor.rowcount
    conn.commit()
    conn.close()

    return deleted


def save_alert(title: str, url: str, matched_keywords: List[str], news_time: str, news_source: str = None) -> int:
    """Save a matched news alert. Returns the alert ID."""
    conn = get_connection()
    cursor = conn.cursor()

    keywords_str = ", ".join(matched_keywords)
    cursor.execute(
        "INSERT INTO alerts (title, url, matched_keywords, news_time, news_source) VALUES (?, ?, ?, ?, ?)",
        (title, url, keywords_str, news_time, news_source)
    )
    alert_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return alert_id


def get_alerts(limit: int = 50) -> List[dict]:
    """Get recent alerts."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, title, url, matched_keywords, news_time, news_source, created_at FROM alerts ORDER BY created_at DESC LIMIT ?",
        (limit,)
    )
    alerts = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return alerts


def delete_alert(alert_id: int) -> bool:
    """Delete an alert by ID."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM alerts WHERE id = ?", (alert_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()

    return deleted


def clear_all_alerts() -> int:
    """Clear all alerts. Returns count of deleted records."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM alerts")
    deleted = cursor.rowcount
    conn.commit()
    conn.close()

    return deleted
