#!/bin/bash
# Vercel用 Streamlitアプリ起動スクリプト

export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_SERVER_ENABLE_CORS=false
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# ポート設定（Vercel用）
PORT=${PORT:-8501}

# アプリ起動
python -m streamlit run app_lite.py --server.port=$PORT --server.address=0.0.0.0