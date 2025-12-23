"""
Vercel用 Streamlit アプリエントリーポイント
"""
import sys
import os
from pathlib import Path

# プロジェクトルートを追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Streamlitアプリのインポート
from app import main

# Vercel serverless function handler
def handler(request, response):
    """Vercel serverless function handler"""
    try:
        main()
    except Exception as e:
        response.status = 500
        return f"Error: {str(e)}"
    
    return "Streamlit app running"

if __name__ == "__main__":
    main()