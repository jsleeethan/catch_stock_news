"""Flask Blueprint routes."""

import os
import logging

from flask import Blueprint, render_template, request, jsonify

from catch_stock_news.config import get_config
from catch_stock_news.database import (
    add_keyword, delete_keyword, get_keywords, toggle_keyword,
    get_alerts, clear_all_alerts
)
from catch_stock_news.notifier import get_webhook_url
from catch_stock_news.services.news_checker import check_news_job, is_notification_time
from catch_stock_news.scheduler import scheduler

logger = logging.getLogger(__name__)

bp = Blueprint(
    "main",
    __name__,
    template_folder="templates",
)


@bp.route("/")
def index():
    """Main page - keyword management UI."""
    keywords = get_keywords()
    alerts = get_alerts(limit=50)
    config = get_config()
    return render_template("index.html", keywords=keywords, alerts=alerts, config=config)


@bp.route("/keywords", methods=["POST"])
def create_keyword():
    """Add a new keyword."""
    data = request.get_json()
    keyword = data.get("keyword", "").strip()

    if not keyword:
        return jsonify({"error": "키워드를 입력해주세요."}), 400

    if len(keyword) > 100:
        return jsonify({"error": "키워드는 100자 이하로 입력해주세요."}), 400

    if add_keyword(keyword):
        logger.info(f"Keyword added: {keyword}")
        return jsonify({"message": f"'{keyword}' 키워드가 추가되었습니다."}), 201
    else:
        return jsonify({"error": f"'{keyword}' 키워드가 이미 존재합니다."}), 409


@bp.route("/keywords/<int:keyword_id>", methods=["DELETE"])
def remove_keyword(keyword_id):
    """Delete a keyword."""
    if delete_keyword(keyword_id):
        logger.info(f"Keyword deleted: {keyword_id}")
        return jsonify({"message": "키워드가 삭제되었습니다."}), 200
    else:
        return jsonify({"error": "키워드를 찾을 수 없습니다."}), 404


@bp.route("/keywords/<int:keyword_id>/toggle", methods=["POST"])
def toggle_keyword_status(keyword_id):
    """Toggle keyword enabled/disabled status."""
    new_status = toggle_keyword(keyword_id)

    if new_status is None:
        return jsonify({"error": "키워드를 찾을 수 없습니다."}), 404

    status_text = "활성화" if new_status else "비활성화"
    logger.info(f"Keyword {keyword_id} toggled to: {status_text}")
    return jsonify({
        "message": f"키워드가 {status_text}되었습니다.",
        "enabled": new_status
    }), 200


@bp.route("/keywords", methods=["GET"])
def list_keywords():
    """Get all keywords as JSON."""
    keywords = get_keywords()
    return jsonify(keywords)


@bp.route("/check-now", methods=["POST"])
def check_now():
    """Manually trigger a news check."""
    try:
        check_news_job()
        return jsonify({"message": "뉴스 확인 완료"}), 200
    except Exception as e:
        logger.error(f"Manual check failed: {e}")
        return jsonify({"error": str(e)}), 500


@bp.route("/status", methods=["GET"])
def status():
    """Get system status."""
    webhook_configured = bool(get_webhook_url())
    keywords = get_keywords()
    config = get_config()

    return jsonify({
        "scheduler_running": scheduler.running,
        "webhook_configured": webhook_configured,
        "keyword_count": len(keywords),
        "enabled_keyword_count": len([k for k in keywords if k.get("enabled", True)]),
        "check_interval": config["check_interval"],
        "notification_window": f"{config['notification_start']} - {config['notification_end']}" if config['notification_start'] else "24/7",
        "is_notification_time": is_notification_time()
    })


@bp.route("/alerts", methods=["GET"])
def list_alerts():
    """Get all alerts as JSON."""
    alerts = get_alerts(limit=100)
    return jsonify(alerts)


@bp.route("/alerts", methods=["DELETE"])
def clear_alerts():
    """Clear all alerts."""
    deleted = clear_all_alerts()
    logger.info(f"Cleared {deleted} alerts")
    return jsonify({"message": f"{deleted}개의 알림이 삭제되었습니다."}), 200
