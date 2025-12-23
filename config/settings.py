"""
アプリケーション設定
"""
import os
from pathlib import Path

# ベースディレクトリ
BASE_DIR = Path(__file__).parent.parent

# データディレクトリ
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
EXTRACTED_DIR = DATA_DIR / "extracted"
REPORTS_DIR = DATA_DIR / "reports"

# Streamlit設定
STREAMLIT_CONFIG = {
    "page_title": "マイソク物確自動化",
    "page_icon": "🏠",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# PDF処理設定
PDF_CONFIG = {
    "max_file_size": 50 * 1024 * 1024,  # 50MB
    "allowed_extensions": [".pdf"],
    "extract_images": False
}

# 物確設定
BUKKATSU_CONFIG = {
    "timeout_seconds": 30,
    "retry_count": 3,
    "wait_time": 2,
    "headless": True,  # ブラウザをヘッドレスモードで実行
    "sites_order": ["itandi", "ierabu"]  # 物確実行順序
}

# ログ設定
LOG_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file_path": DATA_DIR / "logs" / "app.log"
}

# Playwright設定
PLAYWRIGHT_CONFIG = {
    "browser_type": "chromium",
    "headless": True,
    "slow_mo": 1000,  # アクション間の待機時間（ミリ秒）
    "timeout": 30000   # タイムアウト（ミリ秒）
}