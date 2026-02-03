"""Flask application factory."""

from flask import Flask

from catch_stock_news.web.routes import bp


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.register_blueprint(bp)
    return app
