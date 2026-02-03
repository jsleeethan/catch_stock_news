"""Entry point for the news monitoring application."""

import os
from dotenv import load_dotenv

load_dotenv()

from catch_stock_news.logging_setup import setup_logging
from catch_stock_news.database import init_db
from catch_stock_news.scheduler import init_scheduler
from catch_stock_news.services.news_checker import check_news_job
from catch_stock_news.web import create_app

logger = setup_logging()

if __name__ == "__main__":
    init_db()
    logger.info("Database initialized")

    init_scheduler(check_news_job)

    logger.info("Running initial news check...")
    check_news_job()

    app = create_app()
    port = int(os.environ.get("PORT", 5001))
    logger.info(f"Starting Flask server on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
