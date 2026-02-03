"""Slack notification module."""

import os
import requests
from typing import Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def get_webhook_url() -> str:
    """Get Slack webhook URL from environment variable."""
    return os.environ.get("SLACK_WEBHOOK_URL", "")


def send_slack_notification(news_info: Dict) -> bool:
    """
    Send a Slack notification for a matched news item.

    Args:
        news_info: Dict containing title, url, time, source, and matched_keywords

    Returns:
        True if sent successfully, False otherwise
    """
    webhook_url = get_webhook_url()

    if not webhook_url:
        logger.warning("SLACK_WEBHOOK_URL not set. Skipping notification.")
        return False

    keywords_str = ", ".join(news_info.get("matched_keywords", []))
    time_str = news_info.get("time", "")
    source_str = news_info.get("source", "")

    # Format the message
    fields = [
        {
            "type": "mrkdwn",
            "text": f"*매칭된 키워드:*\n{keywords_str}"
        },
        {
            "type": "mrkdwn",
            "text": f"*시간:*\n{time_str if time_str else 'N/A'}"
        }
    ]

    # Add source field if available
    if source_str:
        fields.append({
            "type": "mrkdwn",
            "text": f"*출처:*\n{source_str}"
        })

    message = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📰 증권 뉴스 알림",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{news_info['title']}*"
                }
            },
            {
                "type": "section",
                "fields": fields
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "기사 보기",
                            "emoji": True
                        },
                        "url": news_info["url"],
                        "action_id": "view_article"
                    }
                ]
            },
            {
                "type": "divider"
            }
        ],
        "text": f"증권 뉴스 알림: {news_info['title']}"  # Fallback text
    }

    try:
        response = requests.post(
            webhook_url,
            json=message,
            timeout=10
        )
        response.raise_for_status()
        logger.info(f"Slack notification sent: {news_info['title'][:50]}...")
        return True
    except requests.RequestException as e:
        logger.error(f"Failed to send Slack notification: {e}")
        return False


def send_error_notification(error_message: str, error_details: str = None) -> bool:
    """
    Send an error notification to Slack.

    Args:
        error_message: Brief error message
        error_details: Optional detailed error information

    Returns:
        True if sent successfully, False otherwise
    """
    # Check if error notifications are enabled
    if os.environ.get("ENABLE_ERROR_NOTIFICATIONS", "true").lower() != "true":
        return False

    webhook_url = get_webhook_url()

    if not webhook_url:
        logger.warning("SLACK_WEBHOOK_URL not set. Skipping error notification.")
        return False

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "⚠️ 뉴스 알림 시스템 오류",
                "emoji": True
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*오류 내용:*\n{error_message}"
            }
        }
    ]

    if error_details:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*상세 정보:*\n```{error_details[:500]}```"
            }
        })

    blocks.append({
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": f"발생 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }
        ]
    })

    message = {
        "blocks": blocks,
        "text": f"뉴스 알림 시스템 오류: {error_message}"
    }

    try:
        response = requests.post(
            webhook_url,
            json=message,
            timeout=10
        )
        response.raise_for_status()
        logger.info("Error notification sent to Slack")
        return True
    except requests.RequestException as e:
        logger.error(f"Failed to send error notification: {e}")
        return False


def send_batch_notification(news_list: List[Dict]) -> int:
    """
    Send notifications for multiple news items.

    Returns the count of successfully sent notifications.
    """
    sent_count = 0
    for news in news_list:
        if send_slack_notification(news):
            sent_count += 1
    return sent_count


def send_simple_notification(text: str) -> bool:
    """Send a simple text notification to Slack."""
    webhook_url = get_webhook_url()

    if not webhook_url:
        logger.warning("SLACK_WEBHOOK_URL not set. Skipping notification.")
        return False

    message = {"text": text}

    try:
        response = requests.post(
            webhook_url,
            json=message,
            timeout=10
        )
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        logger.error(f"Failed to send Slack notification: {e}")
        return False


if __name__ == "__main__":
    # Test notification
    logging.basicConfig(level=logging.INFO)

    test_news = {
        "title": "테스트 뉴스 제목입니다",
        "url": "https://n.news.naver.com/mnews/article/015/0005240919",
        "time": "2024-01-01 12:00",
        "source": "한국경제",
        "matched_keywords": ["테스트", "키워드"]
    }

    print("Sending test notification...")
    result = send_slack_notification(test_news)
    print(f"Result: {'Success' if result else 'Failed (check SLACK_WEBHOOK_URL)'}")

    print("\nSending test error notification...")
    result = send_error_notification("테스트 오류", "상세한 오류 내용입니다.")
    print(f"Result: {'Success' if result else 'Failed'}")
