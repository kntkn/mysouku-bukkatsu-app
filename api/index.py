"""
Vercel API endpoint for Mysouku Bukkatsu App
"""
import json
from urllib.parse import urlparse, parse_qs

def handler(request):
    url = urlparse(request.url)
    path = url.path
    
    # Health check endpoint
    if path.endswith('/health'):
        if request.method == 'GET':
            response = {
                "status": "healthy",
                "message": "マイソク物確自動化アプリ API",
                "version": "1.0.0",
                "features": {
                    "pdf_analysis": True,
                    "report_generation": True,
                    "itandi_check": False,
                    "ierabu_check": False
                },
                "endpoints": {
                    "health": "GET /api/health",
                    "analyze": "POST /api/analyze (coming soon)"
                }
            }
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json; charset=utf-8',
                    'Cache-Control': 'public, max-age=60'
                },
                'body': json.dumps(response, ensure_ascii=False, indent=2)
            }
    
    # Analyze endpoint (not implemented yet)
    elif path.endswith('/analyze'):
        if request.method == 'POST':
            response = {
                "error": "Not implemented yet",
                "message": "PDF解析機能は現在開発中です。完全版はGitHubからダウンロードしてください。",
                "github": "https://github.com/kntkn/mysouku-bukkatsu-app"
            }
            
            return {
                'statusCode': 501,
                'headers': {
                    'Content-Type': 'application/json; charset=utf-8'
                },
                'body': json.dumps(response, ensure_ascii=False, indent=2)
            }
        else:
            return {
                'statusCode': 405,
                'headers': {
                    'Content-Type': 'application/json; charset=utf-8'
                },
                'body': json.dumps({
                    "error": "Method not allowed",
                    "message": "このエンドポイントはPOSTメソッドのみサポートしています"
                }, ensure_ascii=False)
            }
    
    # Default API response
    else:
        response = {
            "message": "マイソク物確自動化アプリ API",
            "version": "1.0.0",
            "available_endpoints": {
                "health": "GET /api/health",
                "analyze": "POST /api/analyze (coming soon)"
            },
            "documentation": "https://github.com/kntkn/mysouku-bukkatsu-app"
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json; charset=utf-8',
                'Cache-Control': 'public, max-age=300'
            },
            'body': json.dumps(response, ensure_ascii=False, indent=2)
        }