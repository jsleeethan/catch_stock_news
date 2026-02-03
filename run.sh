#!/bin/bash

# Activate virtual environment and run the app
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment
source venv_catch_stock_news/bin/activate

# Run the application
python app.py
