"""Naver Securities real-time news scraper."""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from urllib.parse import urlparse, parse_qs
import logging

from catch_stock_news.models import NewsItem

logger = logging.getLogger(__name__)


def convert_to_direct_news_url(url: str) -> str:
    """
    Convert finance.naver.com/news/news_read.naver URL to direct n.news.naver.com URL.

    Example:
        Input: /news/news_read.naver?article_id=0005240919&office_id=015&...
        Output: https://n.news.naver.com/mnews/article/015/0005240919
    """
    parsed = urlparse(url)

    if 'news_read.naver' not in parsed.path:
        return url

    params = parse_qs(parsed.query)
    article_id = params.get('article_id', [None])[0]
    office_id = params.get('office_id', [None])[0]

    if article_id and office_id:
        return f"https://n.news.naver.com/mnews/article/{office_id}/{article_id}"

    return url


def _parse_news_page(soup: BeautifulSoup, allowed_sources: Optional[List[str]] = None) -> List[NewsItem]:
    """Parse news items from a single page's BeautifulSoup object."""
    news_items = []

    article_subjects = soup.select("dd.articleSubject a, dt.articleSubject a")

    for link_tag in article_subjects:
        title = link_tag.get("title") or link_tag.get_text(strip=True)
        href = link_tag.get("href", "")

        if not title or not href:
            continue

        # Make absolute URL if needed
        if href and not href.startswith("http"):
            href = "https://finance.naver.com" + href

        # Convert to direct news URL
        href = convert_to_direct_news_url(href)

        # Find time and source elements in sibling dd.articleSummary
        parent = link_tag.find_parent("dd") or link_tag.find_parent("dt")
        time_str = ""
        source_str = ""

        if parent:
            next_sibling = parent.find_next_sibling("dd", class_="articleSummary")
            if next_sibling:
                time_tag = next_sibling.select_one(".wdate")
                time_str = time_tag.get_text(strip=True) if time_tag else ""

                source_tag = next_sibling.select_one(".press")
                source_str = source_tag.get_text(strip=True) if source_tag else ""

        # Filter by allowed sources if specified
        if allowed_sources and source_str:
            if not any(allowed in source_str for allowed in allowed_sources):
                continue

        news_items.append(NewsItem(
            title=title,
            url=href,
            time=time_str,
            source=source_str
        ))

    return news_items


def fetch_realtime_news(allowed_sources: Optional[List[str]] = None, max_pages: int = 3) -> List[NewsItem]:
    """
    Fetch real-time news from Naver Securities across multiple pages.

    Args:
        allowed_sources: List of allowed news source names. If None, all sources are allowed.
        max_pages: Maximum number of pages to scrape (default: 3).

    Returns a list of NewsItem objects containing title, url, time, and source.
    """
    base_url = "https://finance.naver.com/news/news_list.naver?mode=LSS2D&section_id=101&section_id2=258"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    all_news_items = []
    seen_urls = set()

    try:
        for page in range(1, max_pages + 1):
            url = f"{base_url}&page={page}"
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            response.encoding = "euc-kr"

            soup = BeautifulSoup(response.text, "html.parser")
            page_items = _parse_news_page(soup, allowed_sources)

            # Try alternative format if first page returns nothing
            if not page_items and page == 1:
                page_items = _fetch_alternative_format(soup, allowed_sources)

            # Deduplicate by URL across pages
            for item in page_items:
                if item.url not in seen_urls:
                    seen_urls.add(item.url)
                    all_news_items.append(item)

            # Stop if no items found on this page (no more pages)
            if not page_items:
                break

        logger.debug(f"Fetched {len(all_news_items)} news items from {min(page, max_pages)} page(s)")

    except requests.RequestException as e:
        logger.error(f"Error fetching news: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while scraping: {e}")
        raise

    return all_news_items


def _fetch_alternative_format(soup: BeautifulSoup, allowed_sources: Optional[List[str]] = None) -> List[NewsItem]:
    """Try alternative HTML structure for news parsing."""
    news_items = []

    # Try different selectors for news items
    selectors = [
        "div.mainNewsList li a",
        "table.type5 td.title a",
        "div.news_area a.tit",
    ]

    for selector in selectors:
        links = soup.select(selector)
        for link in links:
            title = link.get_text(strip=True)
            href = link.get("href", "")

            if href and not href.startswith("http"):
                href = "https://finance.naver.com" + href

            # Convert to direct news URL
            href = convert_to_direct_news_url(href)

            if title and href and len(title) > 5:  # Filter out navigation links
                news_items.append(NewsItem(
                    title=title,
                    url=href,
                    time="",
                    source=""
                ))

        if news_items:
            break

    return news_items


def find_matching_news(news_items: List[NewsItem], keywords: List[str]) -> List[Dict]:
    """
    Find news items that contain any of the given keywords.

    Returns a list of dicts with news info and matched keywords.
    """
    matched = []

    for news in news_items:
        matched_keywords = []
        for keyword in keywords:
            if keyword.lower() in news.title.lower():
                matched_keywords.append(keyword)

        if matched_keywords:
            matched.append({
                "title": news.title,
                "url": news.url,
                "time": news.time,
                "source": news.source,
                "matched_keywords": matched_keywords
            })

    return matched


if __name__ == "__main__":
    # Test the scraper
    logging.basicConfig(level=logging.DEBUG)
    print("Fetching news...")
    news = fetch_realtime_news()
    print(f"Found {len(news)} news items:")
    for item in news[:10]:
        print(f"  - {item.title}")
        print(f"    URL: {item.url}")
        print(f"    Source: {item.source}")
        print(f"    Time: {item.time}")
        print()
