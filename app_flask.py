"""
マイソク物確自動化アプリ - Flask版（超軽量）
Vercel用の軽量Webアプリ
"""
from flask import Flask, request, render_template_string, jsonify
import time
import sys
import os
from pathlib import Path

# srcディレクトリをパスに追加
sys.path.append(str(Path(__file__).parent / "src"))

from src.cloud_checker import CloudPropertyChecker
from src.simple_pdf_analyzer import SimplePDFAnalyzer, PropertyData
from src.browser_checker import BrowserPropertyChecker

app = Flask(__name__)

# HTML テンプレート
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI物確システム - 自動物件確認</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --color-primary: #0a0a0f;
            --color-accent: #ff4d6d;
            --color-surface: #fafafa;
            --color-muted: #6b6b6b;
            --color-success: #00d084;
            --color-warning: #ff9500;
            --color-error: #ff4d4d;
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            background: 
                radial-gradient(circle at 20% 80%, rgba(255, 77, 109, 0.08) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(0, 208, 132, 0.06) 0%, transparent 50%),
                linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 100%);
            min-height: 100vh;
            padding: 20px;
            position: relative;
        }
        
        body::after {
            content: '';
            position: fixed;
            inset: 0;
            background-image: 
                radial-gradient(circle at 1px 1px, rgba(255,255,255,0.03) 1px, transparent 0);
            background-size: 20px 20px;
            pointer-events: none;
            z-index: -1;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
            animation: fadeIn 0.8s ease-out;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .header {
            text-align: center;
            margin-bottom: 60px;
            color: white;
            animation: slideDown 1s ease-out 0.2s both;
        }
        
        @keyframes slideDown {
            from { opacity: 0; transform: translateY(-30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        h1 {
            font-family: 'Space Grotesk', sans-serif;
            font-size: clamp(2.5rem, 5vw, 4rem);
            font-weight: 700;
            background: linear-gradient(135deg, #ff4d6d 0%, #00d084 50%, #ff9500 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 20px;
            letter-spacing: -0.02em;
        }
        
        .subtitle {
            font-size: 1.2rem;
            color: rgba(255,255,255,0.7);
            font-weight: 400;
        }
        
        .upload-zone {
            background: rgba(255,255,255,0.97);
            border: 2px dashed rgba(255,77,109,0.3);
            border-radius: 24px;
            padding: 60px 40px;
            text-align: center;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            backdrop-filter: blur(10px);
            box-shadow: 
                0 20px 40px rgba(0,0,0,0.1),
                inset 0 1px 0 rgba(255,255,255,0.8);
            animation: slideUp 1s ease-out 0.4s both;
            position: relative;
            overflow: hidden;
        }
        
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(40px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .upload-zone::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,77,109,0.1), transparent);
            transition: left 0.5s ease;
        }
        
        .upload-zone:hover {
            border-color: var(--color-accent);
            transform: translateY(-4px);
            box-shadow: 
                0 32px 64px rgba(255,77,109,0.15),
                inset 0 1px 0 rgba(255,255,255,0.9);
        }
        
        .upload-zone:hover::before {
            left: 100%;
        }
        
        .upload-icon {
            font-size: 4rem;
            margin-bottom: 20px;
            color: var(--color-accent);
            animation: bounce 2s infinite;
        }
        
        @keyframes bounce {
            0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
            40% { transform: translateY(-10px); }
            60% { transform: translateY(-5px); }
        }
        
        .upload-title {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--color-primary);
            margin-bottom: 12px;
        }
        
        .upload-subtitle {
            color: var(--color-muted);
            margin-bottom: 30px;
            line-height: 1.6;
        }
        
        .file-input-wrapper {
            position: relative;
            display: inline-block;
            margin-bottom: 20px;
        }
        
        .file-input {
            opacity: 0;
            position: absolute;
            z-index: -1;
        }
        
        .file-input-label {
            display: inline-flex;
            align-items: center;
            gap: 12px;
            padding: 16px 32px;
            background: linear-gradient(135deg, var(--color-primary) 0%, #2a2a4e 100%);
            color: white;
            border-radius: 50px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 8px 24px rgba(10,10,15,0.3);
        }
        
        .file-input-label:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 32px rgba(10,10,15,0.4);
        }
        
        .start-btn {
            display: inline-flex;
            align-items: center;
            gap: 12px;
            padding: 18px 40px;
            background: linear-gradient(135deg, var(--color-accent) 0%, #ff6b8a 100%);
            color: white;
            border: none;
            border-radius: 50px;
            font-size: 1.1rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 8px 24px rgba(255,77,109,0.3);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .start-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 16px 40px rgba(255,77,109,0.4);
        }
        
        .start-btn:active {
            transform: translateY(0);
        }
        
        .error-zone {
            background: linear-gradient(135deg, #ff4d4d 0%, #ff6b6b 100%);
            color: white;
            padding: 20px 30px;
            border-radius: 16px;
            margin-bottom: 40px;
            animation: shake 0.5s ease-in-out;
            box-shadow: 0 8px 24px rgba(255,77,77,0.3);
        }
        
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-5px); }
            75% { transform: translateX(5px); }
        }
        
        .loading-zone {
            text-align: center;
            padding: 40px;
            background: rgba(255,255,255,0.95);
            border-radius: 20px;
            margin-top: 30px;
            backdrop-filter: blur(10px);
        }
        
        .loading-spinner {
            width: 60px;
            height: 60px;
            border: 4px solid rgba(255,77,109,0.2);
            border-left: 4px solid var(--color-accent);
            border-radius: 50%;
            margin: 0 auto 20px;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        /* 結果表示スタイル */
        .results-container {
            background: rgba(255,255,255,0.97);
            border-radius: 24px;
            padding: 40px;
            margin-top: 40px;
            backdrop-filter: blur(10px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            animation: slideUp 0.8s ease-out;
        }
        
        .results-header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .results-header h2 {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 2rem;
            color: var(--color-primary);
            margin-bottom: 8px;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        
        .metric-card {
            background: rgba(255,255,255,0.8);
            border: 1px solid rgba(255,77,109,0.1);
            border-radius: 16px;
            padding: 24px;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 24px rgba(255,77,109,0.15);
        }
        
        .metric-value {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--color-primary);
            margin-bottom: 8px;
        }
        
        .metric-value.success { color: var(--color-success); }
        .metric-value.error { color: var(--color-error); }
        
        .metric-label {
            color: var(--color-muted);
            font-weight: 500;
            font-size: 0.9rem;
        }
        
        .property-details {
            background: rgba(10,10,15,0.02);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 30px;
        }
        
        .property-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .property-header h3 {
            font-family: 'Space Grotesk', sans-serif;
            color: var(--color-primary);
            margin: 0;
        }
        
        .source-badge {
            background: linear-gradient(135deg, var(--color-accent) 0%, #ff6b8a 100%);
            color: white;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        
        .property-info {
            display: grid;
            gap: 12px;
        }
        
        .info-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255,77,109,0.1);
        }
        
        .info-row:last-child {
            border-bottom: none;
        }
        
        .info-row .label {
            color: var(--color-muted);
            font-weight: 600;
            min-width: 80px;
        }
        
        .info-row .value {
            color: var(--color-primary);
            font-weight: 500;
            text-align: right;
        }
        
        .sites-results {
            margin-bottom: 30px;
        }
        
        .sites-results h3 {
            font-family: 'Space Grotesk', sans-serif;
            color: var(--color-primary);
            margin-bottom: 20px;
        }
        
        .site-card {
            background: rgba(255,255,255,0.8);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 12px;
            transition: all 0.3s ease;
            border-left: 4px solid transparent;
        }
        
        .site-card.found {
            border-left-color: var(--color-success);
            background: rgba(0,208,132,0.05);
        }
        
        .site-card.not-found {
            border-left-color: var(--color-error);
            background: rgba(255,77,77,0.05);
        }
        
        .site-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .site-name {
            font-weight: 700;
            color: var(--color-primary);
            font-size: 1.1rem;
        }
        
        .status-badge {
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 600;
        }
        
        .status-badge.success {
            background: var(--color-success);
            color: white;
        }
        
        .status-badge.error {
            background: var(--color-error);
            color: white;
        }
        
        .confidence {
            margin-top: 8px;
            color: var(--color-muted);
            font-size: 0.9rem;
        }
        
        .final-verdict {
            background: rgba(255,255,255,0.9);
            border-radius: 16px;
            padding: 30px;
            text-align: center;
            border: 2px solid;
        }
        
        .final-verdict.success {
            border-color: var(--color-success);
            background: rgba(0,208,132,0.05);
        }
        
        .final-verdict.error {
            border-color: var(--color-error);
            background: rgba(255,77,77,0.05);
        }
        
        .verdict-icon {
            font-size: 3rem;
            margin-bottom: 16px;
        }
        
        .verdict-text h3 {
            font-family: 'Space Grotesk', sans-serif;
            margin-bottom: 8px;
        }
        
        .verdict-text p {
            color: var(--color-muted);
            line-height: 1.6;
        }
        
        .footer {
            text-align: center;
            margin-top: 60px;
            padding: 20px;
            color: rgba(255,255,255,0.7);
        }
        
        .footer a {
            color: var(--color-accent);
            text-decoration: none;
            transition: color 0.3s ease;
        }
        
        .footer a:hover {
            color: #ff6b8a;
        }
        
        @media (max-width: 640px) {
            .container { padding: 0 10px; }
            .upload-zone, .results-container { padding: 30px 20px; }
            h1 { font-size: 2.5rem; }
            .metrics-grid { grid-template-columns: 1fr; }
            .property-header { flex-direction: column; gap: 10px; }
            .info-row { flex-direction: column; align-items: flex-start; }
            .info-row .value { text-align: left; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI物確システム</h1>
            <p class="subtitle">レインズPDFを投入するだけで、全自動物件確認を実行</p>
        </div>
        
        {% if error %}
        <div class="error-zone">
            <h3>❌ エラーが発生しました</h3>
            <p>{{ error }}</p>
        </div>
        {% endif %}
        
        <form method="POST" action="/upload" enctype="multipart/form-data" id="uploadForm">
            <div class="upload-zone" id="uploadZone">
                <div class="upload-icon">📄</div>
                <h2 class="upload-title">マイソクPDFをドロップ</h2>
                <p class="upload-subtitle">
                    レインズからダウンロードしたPDFファイルをここにドラッグ&ドロップ<br>
                    または下記ボタンからファイルを選択してください
                </p>
                
                <div class="file-input-wrapper">
                    <input type="file" id="pdf_file" name="pdf_file" accept=".pdf" required class="file-input">
                    <label for="pdf_file" class="file-input-label">
                        📁 ファイルを選択
                    </label>
                </div>
                
                <button type="submit" class="start-btn" id="startBtn">
                    🚀 AI物確スタート
                </button>
                
                <div style="margin-top: 20px;">
                    <p style="color: var(--color-muted); margin-bottom: 10px;">または</p>
                    <form method="POST" action="/demo" style="display: inline;">
                        <button type="submit" class="start-btn" style="background: linear-gradient(135deg, var(--color-warning) 0%, #ffb347 100%); box-shadow: 0 8px 24px rgba(255, 149, 0, 0.3);">
                            🎯 デモで試す
                        </button>
                    </form>
                </div>
            </div>
        </form>
        
        {% if results %}
        <div class="results-container">
            <div class="results-header">
                <h2>🎯 AI物確完了</h2>
                <p>{{ results.property.address }}の物確結果</p>
            </div>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{{ results.total }}</div>
                    <div class="metric-label">確認サイト数</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value success">{{ results.found }}</div>
                    <div class="metric-label">発見サイト数</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value {{ 'success' if results.rate > 0 else 'error' }}">
                        {{ "%.0f"|format(results.rate) }}%
                    </div>
                    <div class="metric-label">発見率</div>
                </div>
            </div>
            
            <div class="property-details">
                <div class="property-header">
                    <h3>📍 物件詳細</h3>
                    {% if results.source == 'PDF' %}
                    <span class="source-badge">PDF自動抽出</span>
                    {% endif %}
                </div>
                
                <div class="property-info">
                    <div class="info-row">
                        <span class="label">住所</span>
                        <span class="value">{{ results.property.address }}</span>
                    </div>
                    <div class="info-row">
                        <span class="label">賃料</span>
                        <span class="value">{{ results.property.rent }}</span>
                    </div>
                    <div class="info-row">
                        <span class="label">間取り</span>
                        <span class="value">{{ results.property.layout }}</span>
                    </div>
                    <div class="info-row">
                        <span class="label">最寄り駅</span>
                        <span class="value">{{ results.property.station_info }}</span>
                    </div>
                    {% if results.property.area %}
                    <div class="info-row">
                        <span class="label">面積</span>
                        <span class="value">{{ results.property.area }}</span>
                    </div>
                    {% endif %}
                    {% if results.property.age %}
                    <div class="info-row">
                        <span class="label">築年数</span>
                        <span class="value">{{ results.property.age }}</span>
                    </div>
                    {% endif %}
                </div>
            </div>
            
            <div class="sites-results">
                <h3>🔍 各サイト確認状況</h3>
                
                <div class="site-card {{ 'found' if results.itandi.found else 'not-found' }}">
                    <div class="site-header">
                        <span class="site-name">ITANDI</span>
                        <span class="status-badge {{ 'success' if results.itandi.found else 'error' }}">
                            {{ '✅ 発見' if results.itandi.found else '❌ 未発見' }}
                        </span>
                    </div>
                    {% if results.itandi.found %}
                    <div class="confidence">
                        信頼度: {{ "%.1f"|format(results.itandi.confidence * 100) }}%
                    </div>
                    {% endif %}
                </div>
                
                <div class="site-card {{ 'found' if results.ierabu.found else 'not-found' }}">
                    <div class="site-header">
                        <span class="site-name">いえらぶBB</span>
                        <span class="status-badge {{ 'success' if results.ierabu.found else 'error' }}">
                            {{ '✅ 発見' if results.ierabu.found else '❌ 未発見' }}
                        </span>
                    </div>
                    {% if results.ierabu.found %}
                    <div class="confidence">
                        信頼度: {{ "%.1f"|format(results.ierabu.confidence * 100) }}%
                    </div>
                    {% endif %}
                </div>
                
                <div class="site-card {{ 'found' if results.suumo.found else 'not-found' }}">
                    <div class="site-header">
                        <span class="site-name">SUUMO</span>
                        <span class="status-badge {{ 'success' if results.suumo.found else 'error' }}">
                            {{ '✅ 発見' if results.suumo.found else '❌ 未発見' }}
                        </span>
                    </div>
                    {% if results.suumo.found %}
                    <div class="confidence">
                        信頼度: {{ "%.1f"|format(results.suumo.confidence * 100) }}%
                    </div>
                    {% endif %}
                </div>
            </div>
            
            <div class="final-verdict {{ 'success' if results.overall_found else 'error' }}">
                <div class="verdict-icon">
                    {{ '🎉' if results.overall_found else '🔍' }}
                </div>
                <div class="verdict-text">
                    <h3>{{ '物件発見！' if results.overall_found else '物件未発見' }}</h3>
                    <p>
                        {% if results.overall_found %}
                        この物件は現在も募集中の可能性が高いです
                        {% else %}
                        この物件は成約済みまたは募集停止の可能性があります
                        {% endif %}
                    </p>
                </div>
            </div>
        </div>
        {% endif %}
        
        <div class="footer">
            <p>🤖 AI物確システム | <a href="https://github.com/kntkn/mysouku-bukkatsu-app" target="_blank">GitHub</a></p>
        </div>
    </div>
    
    <script>
        // ドラッグ&ドロップ機能
        const uploadZone = document.getElementById('uploadZone');
        const fileInput = document.getElementById('pdf_file');
        
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadZone.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        ['dragenter', 'dragover'].forEach(eventName => {
            uploadZone.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            uploadZone.addEventListener(eventName, unhighlight, false);
        });
        
        function highlight(e) {
            uploadZone.style.borderColor = 'var(--color-accent)';
            uploadZone.style.backgroundColor = 'rgba(255,77,109,0.05)';
        }
        
        function unhighlight(e) {
            uploadZone.style.borderColor = 'rgba(255,77,109,0.3)';
            uploadZone.style.backgroundColor = 'rgba(255,255,255,0.97)';
        }
        
        uploadZone.addEventListener('drop', handleDrop, false);
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (files.length > 0) {
                fileInput.files = files;
                updateFileLabel(files[0].name);
            }
        }
        
        fileInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                updateFileLabel(this.files[0].name);
            }
        });
        
        function updateFileLabel(fileName) {
            const label = document.querySelector('.file-input-label');
            label.innerHTML = `📄 ${fileName}`;
        }
        
        // フォーム送信時のローディング表示
        document.getElementById('uploadForm').addEventListener('submit', function() {
            const startBtn = document.getElementById('startBtn');
            startBtn.innerHTML = '🔄 物確実行中...';
            startBtn.disabled = true;
            
            // ローディングスピナー表示
            const loadingHTML = `
                <div class="loading-zone">
                    <div class="loading-spinner"></div>
                    <h3>AI物確実行中...</h3>
                    <p>ITANDI・いえらぶBB・SUUMO等を巡回しています</p>
                </div>
            `;
            
            setTimeout(() => {
                uploadZone.innerHTML = loadingHTML;
            }, 500);
        });
    </script>
</body>
</html>
"""

class SimpleProperty:
    """簡易プロパティクラス"""
    def __init__(self, address, rent, layout, station):
        self.address = address
        self.rent = rent
        self.layout = layout
        self.station_info = station

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/upload', methods=['POST'])
def upload_pdf():
    try:
        # ファイル存在確認（より詳細なデバッグ）
        print(f"📁 Files in request: {list(request.files.keys())}")
        print(f"📝 Form data: {list(request.form.keys())}")
        
        if 'pdf_file' not in request.files:
            print("❌ 'pdf_file' not found in request.files")
            return render_template_string(HTML_TEMPLATE, error="PDFファイルが選択されていません。もう一度ファイルを選択してください。")
        
        file = request.files['pdf_file']
        print(f"📄 File received: {file.filename}, size: {file.content_length if hasattr(file, 'content_length') else 'unknown'}")
        
        if not file or file.filename == '' or file.filename is None:
            print("❌ Empty filename")
            return render_template_string(HTML_TEMPLATE, error="有効なファイルが選択されていません。PDFファイルを選択してください。")
        
        if not file.filename.lower().endswith('.pdf'):
            print(f"❌ Invalid file type: {file.filename}")
            return render_template_string(HTML_TEMPLATE, error=f"PDFファイルを選択してください。選択されたファイル: {file.filename}")
        
        print("✅ File validation passed, starting PDF analysis...")
        
        # PDF解析
        analyzer = SimplePDFAnalyzer()
        result = analyzer.analyze_pdf(file)
        
        if not result['success']:
            return render_template_string(HTML_TEMPLATE, error=f"PDF解析エラー: {result['error']}")
        
        properties = result['properties']
        if not properties:
            return render_template_string(HTML_TEMPLATE, error="PDFから物件情報を抽出できませんでした")
        
        # 最初の物件で物確実行（複数物件対応は今後追加）
        property_data = properties[0]
        
        # ブラウザ自動化による物確実行
        print("🤖 AI物確システム開始...")
        browser_checker = BrowserPropertyChecker()
        bukkaku_results = browser_checker.perform_bukkaku(property_data)
        
        # PropertyDataオブジェクト作成
        property_obj = PropertyData(property_data)
        
        # 結果をテンプレートに渡す
        results = {
            'total': bukkaku_results['total'],
            'found': bukkaku_results['found'],
            'rate': bukkaku_results['rate'],
            'property': property_obj,
            'itandi': bukkaku_results['itandi'],
            'ierabu': bukkaku_results['ierabu'],
            'suumo': bukkaku_results['suumo'],
            'overall_found': bukkaku_results['overall_found'],
            'found_sites': bukkaku_results.get('found_sites', []),
            'source': 'PDF'  # PDFから抽出したことを明示
        }
        
        return render_template_string(HTML_TEMPLATE, results=results)
        
    except Exception as e:
        return render_template_string(HTML_TEMPLATE, error=f"処理エラー: {str(e)}")


@app.route('/demo', methods=['GET', 'POST'])
def demo():
    """デモ用物確実行"""
    if request.method == 'GET':
        return render_template_string(HTML_TEMPLATE)
    
    try:
        print("🎯 デモモード: 物確実行開始")
        
        # デモ用物件データ
        demo_property = {
            'property_id': 'DEMO_001',
            'address': '東京都渋谷区',
            'rent': '15万円',
            'layout': '1K',
            'station': '渋谷駅徒歩5分',
            'area': '25㎡',
            'age': '築5年',
            'source_file': 'demo_property'
        }
        
        # ブラウザ自動化による物確実行
        print("🤖 AI物確システム開始...")
        browser_checker = BrowserPropertyChecker()
        bukkaku_results = browser_checker.perform_bukkaku(demo_property)
        
        # PropertyDataオブジェクト作成
        from src.simple_pdf_analyzer import PropertyData
        property_obj = PropertyData(demo_property)
        
        # 結果をテンプレートに渡す
        results = {
            'total': bukkaku_results['total'],
            'found': bukkaku_results['found'],
            'rate': bukkaku_results['rate'],
            'property': property_obj,
            'itandi': bukkaku_results['itandi'],
            'ierabu': bukkaku_results['ierabu'],
            'suumo': bukkaku_results['suumo'],
            'overall_found': bukkaku_results['overall_found'],
            'found_sites': bukkaku_results.get('found_sites', []),
            'source': 'Demo'  # デモモードであることを明示
        }
        
        print("✅ デモ物確完了")
        return render_template_string(HTML_TEMPLATE, results=results)
        
    except Exception as e:
        print(f"❌ デモエラー: {str(e)}")
        return render_template_string(HTML_TEMPLATE, error=f"デモ実行エラー: {str(e)}")

@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy",
        "message": "マイソク物確自動化アプリ API",
        "version": "2.0.0",
        "framework": "Flask"
    })

if __name__ == '__main__':
    app.run(debug=True)