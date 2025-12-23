"""
Vercel Root Handler for Mysouku Bukkatsu App
Handles the main website root path
"""
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html = """
        <!DOCTYPE html>
        <html lang="ja">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>マイソク物確自動化アプリ</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    color: #333;
                }
                .container { 
                    max-width: 900px; 
                    margin: 0 auto; 
                    padding: 40px 20px;
                }
                .header { 
                    background: white;
                    border-radius: 20px;
                    padding: 40px;
                    text-align: center;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                    margin-bottom: 30px;
                }
                .header h1 { 
                    font-size: 2.5em;
                    margin-bottom: 10px;
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                }
                .subtitle { 
                    color: #666;
                    font-size: 1.2em;
                    margin-bottom: 20px;
                }
                .info-card {
                    background: #f8f9fa;
                    border-radius: 15px;
                    padding: 30px;
                    margin: 20px 0;
                    border-left: 5px solid #667eea;
                }
                .feature-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin: 30px 0;
                }
                .feature-card {
                    background: white;
                    border-radius: 15px;
                    padding: 25px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                    transition: transform 0.3s ease;
                }
                .feature-card:hover {
                    transform: translateY(-5px);
                }
                .feature-title {
                    font-size: 1.3em;
                    font-weight: 600;
                    margin-bottom: 15px;
                    color: #333;
                }
                .feature-list {
                    list-style: none;
                    padding: 0;
                }
                .feature-list li {
                    margin: 8px 0;
                    padding-left: 25px;
                    position: relative;
                }
                .feature-list li:before {
                    content: "✅";
                    position: absolute;
                    left: 0;
                }
                .unavailable:before {
                    content: "❌";
                }
                .button {
                    display: inline-block;
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    color: white;
                    padding: 15px 30px;
                    text-decoration: none;
                    border-radius: 25px;
                    font-weight: 600;
                    margin: 10px;
                    transition: all 0.3s ease;
                    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
                }
                .button:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
                }
                .button.secondary {
                    background: #6c757d;
                    box-shadow: 0 5px 15px rgba(108, 117, 125, 0.3);
                }
                .footer {
                    text-align: center;
                    margin-top: 40px;
                    padding: 20px;
                    background: rgba(255,255,255,0.1);
                    border-radius: 15px;
                    color: white;
                }
                .status-badge {
                    background: #28a745;
                    color: white;
                    padding: 5px 12px;
                    border-radius: 20px;
                    font-size: 0.9em;
                    margin-left: 10px;
                }
                @media (max-width: 768px) {
                    .container { padding: 20px 15px; }
                    .header { padding: 25px; }
                    .header h1 { font-size: 2em; }
                    .feature-grid { grid-template-columns: 1fr; }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏠 マイソク物確自動化アプリ</h1>
                    <p class="subtitle">マイソクPDFから物件情報を抽出し、自動物確を実行<span class="status-badge">LIVE</span></p>
                </div>

                <div class="info-card">
                    <h3>💡 クラウド版の制限について</h3>
                    <p>このクラウド版では、セキュリティ上の理由により、ブラウザ自動化機能（物確機能）は無効化されています。PDF解析・レポート生成機能のみご利用いただけます。</p>
                </div>

                <div class="feature-grid">
                    <div class="feature-card">
                        <div class="feature-title">📱 クラウド版（現在表示中）</div>
                        <ul class="feature-list">
                            <li>マイソクPDF解析</li>
                            <li>物件情報自動抽出</li>
                            <li>詳細レポート生成</li>
                            <li class="unavailable">ITANDI物確（ローカル版のみ）</li>
                            <li class="unavailable">いえらぶBB物確（ローカル版のみ）</li>
                        </ul>
                    </div>

                    <div class="feature-card">
                        <div class="feature-title">💻 完全版（ローカル実行）</div>
                        <ul class="feature-list">
                            <li>マイソクPDF解析</li>
                            <li>物件情報自動抽出</li>
                            <li>ITANDI自動物確</li>
                            <li>いえらぶBB自動物確</li>
                            <li>自動ログイン機能</li>
                            <li>詳細レポート生成</li>
                        </ul>
                    </div>
                </div>

                <div style="text-align: center; margin: 40px 0;">
                    <a href="https://github.com/kntkn/mysouku-bukkatsu-app" class="button" target="_blank">
                        📥 完全版をダウンロード
                    </a>
                    <a href="/api/health" class="button secondary">
                        🔍 API ヘルスチェック
                    </a>
                </div>

                <div class="info-card">
                    <h3>📊 API エンドポイント</h3>
                    <p><strong>ヘルスチェック:</strong> <code>GET /api/health</code></p>
                    <p><strong>PDF解析:</strong> <code>POST /api/analyze</code> (開発予定)</p>
                </div>

                <div class="footer">
                    <p>🚀 Powered by Vercel</p>
                    <p>© 2024 マイソク物確自動化アプリ | <a href="https://github.com/kntkn/mysouku-bukkatsu-app/issues" style="color: white;">お問い合わせ</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        self.wfile.write(html.encode('utf-8'))