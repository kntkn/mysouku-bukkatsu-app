"""
Vercel API endpoint for Mysouku Bukkatsu App
Since Streamlit doesn't work well with serverless, this creates a simple API wrapper
"""
from http.server import BaseHTTPRequestHandler
import json
import sys
import os
from pathlib import Path

# Add src path
sys.path.append(str(Path(__file__).parent.parent / "src"))
sys.path.append(str(Path(__file__).parent.parent))

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>マイソク物確自動化アプリ</title>
                <meta charset="utf-8">
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
                    .container { max-width: 800px; margin: 0 auto; }
                    .header { text-align: center; color: #333; }
                    .info { background: #f0f8ff; padding: 20px; border-radius: 8px; margin: 20px 0; }
                    .button { background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block; }
                    .footer { text-align: center; margin-top: 40px; color: #666; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1 class="header">🏠 マイソク物確自動化アプリ</h1>
                    
                    <div class="info">
                        <h3>💡 クラウド版の制限について</h3>
                        <p>このクラウド版では、セキュリティ上の理由により、ブラウザ自動化機能（物確機能）は無効化されています。</p>
                        <p>PDF解析・レポート生成機能のみご利用いただけます。</p>
                    </div>

                    <h3>📋 利用可能な機能</h3>
                    <ul>
                        <li>✅ マイソクPDF解析</li>
                        <li>✅ 物件情報抽出</li>
                        <li>✅ 詳細レポート生成</li>
                        <li>❌ ITANDI物確（ローカル版のみ）</li>
                        <li>❌ いえらぶBB物確（ローカル版のみ）</li>
                    </ul>

                    <h3>🏠 完全版ダウンロード</h3>
                    <p>物確機能付き完全版をローカルで実行したい場合：</p>
                    <a href="https://github.com/kntkn/mysouku-bukkatsu-app" class="button" target="_blank">
                        GitHub リポジトリ
                    </a>

                    <h3>📊 API エンドポイント</h3>
                    <p>プログラムからの利用:</p>
                    <ul>
                        <li><code>GET /api/health</code> - ヘルスチェック</li>
                        <li><code>POST /api/analyze</code> - PDF解析（今後実装予定）</li>
                    </ul>

                    <div class="footer">
                        <p>© 2024 マイソク物確自動化アプリ</p>
                        <p>お問い合わせ: <a href="https://github.com/kntkn/mysouku-bukkatsu-app/issues">GitHub Issues</a></p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            self.wfile.write(html.encode('utf-8'))
            
        elif self.path == '/api/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                "status": "healthy",
                "message": "マイソク物確自動化アプリ API",
                "version": "1.0.0",
                "features": {
                    "pdf_analysis": True,
                    "report_generation": True,
                    "itandi_check": False,
                    "ierabu_check": False
                }
            }
            
            self.wfile.write(json.dumps(response, ensure_ascii=False, indent=2).encode('utf-8'))
            
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def do_POST(self):
        if self.path == '/api/analyze':
            self.send_response(501)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                "error": "Not implemented yet",
                "message": "PDF解析機能は現在開発中です。完全版はGitHubからダウンロードしてください。",
                "github": "https://github.com/kntkn/mysouku-bukkatsu-app"
            }
            
            self.wfile.write(json.dumps(response, ensure_ascii=False, indent=2).encode('utf-8'))
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not Found')