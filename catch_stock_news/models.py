"""Data models for the application."""

from dataclasses import dataclass


@dataclass
class NewsItem:
    """Represents a news article."""
    title: str
    url: str
    time: str
    source: str = ""
