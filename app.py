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

try:
    from src.simple_pdf_analyzer import SimplePDFAnalyzer, PropertyData
    from src.real_browser_checker import RealBrowserPropertyChecker
    PDF_ANALYZER_AVAILABLE = True
    BROWSER_CHECKER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Import warning: {e}")
    PDF_ANALYZER_AVAILABLE = False
    BROWSER_CHECKER_AVAILABLE = False
    
    # フォールバック用の簡易クラス
    class SimplePDFAnalyzer:
        def analyze_pdf(self, file):
            return {'success': False, 'error': 'PDF解析機能が利用できません'}
    
    class PropertyData:
        def __init__(self, data):
            self.address = data.get('address', '住所不明')
            self.rent = data.get('rent', '賃料不明')
            self.layout = data.get('layout', '間取り不明')
            self.station_info = data.get('station', '駅情報不明')
            self.area = data.get('area', '')
            self.age = data.get('age', '')
    
    class RealBrowserPropertyChecker:
        def perform_bukkaku(self, property_data):
            return {
                'total': 3,
                'found': 0,
                'rate': 0,
                'overall_found': False,
                'found_sites': [],
                'itandi': {'found': False, 'confidence': 0.0, 'notes': 'システムエラー'},
                'ierabu': {'found': False, 'confidence': 0.0, 'notes': 'システムエラー'},
                'suumo': {'found': False, 'confidence': 0.0, 'notes': 'システムエラー'},
            }

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB制限

@app.errorhandler(413)
def too_large(e):
    return render_template_string(HTML_TEMPLATE, error="ファイルが大きすぎます。50MB以下のPDFファイルを選択してください。"), 413

@app.errorhandler(500)
def internal_error(e):
    return render_template_string(HTML_TEMPLATE, error=f"内部サーバーエラー: {str(e)}"), 500

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
        }
        
        .step-progress {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin: 20px 0;
            flex-wrap: wrap;
        }
        
        .step {
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 500;
            background: #f0f0f0;
            color: var(--color-muted);
            transition: all 0.3s ease;
        }
        
        .step.active {
            background: linear-gradient(135deg, var(--color-accent) 0%, #ff6b8a 100%);
            color: white;
            animation: pulse 1.5s ease-in-out infinite;
        }
        
        .step.completed {
            background: var(--color-success);
            color: white;
        }
        
        @media (max-width: 768px) {
            .step-progress {
                flex-direction: column;
                gap: 10px;
            }
            
            .step {
                padding: 10px 20px;
                font-size: 0.95rem;
            }
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
        
        .phone-step-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 16px;
            padding: 25px;
            margin: 20px 0;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
            border-left: 4px solid var(--color-warning);
        }
        
        .phone-step-card.phone-required {
            border-left-color: var(--color-warning);
            background: rgba(255, 149, 0, 0.1);
        }
        
        .phone-step-card.no-phone {
            border-left-color: var(--color-success);
            background: rgba(0, 208, 132, 0.1);
        }
        
        .phone-status {
            margin-bottom: 15px;
        }
        
        .phone-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.9rem;
        }
        
        .phone-badge.required {
            background: var(--color-warning);
            color: white;
        }
        
        .phone-badge.not-required {
            background: var(--color-success);
            color: white;
        }
        
        .phone-notes {
            white-space: pre-line;
            line-height: 1.6;
            color: var(--color-primary);
            margin-top: 10px;
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
            <h1>🏢 不動産物確システム</h1>
            <p class="subtitle">物件情報PDFから自動物確実行 - ITANDI・いえらぶBB・ATBBを一括検索</p>
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
                <h2 class="upload-title">物件PDF解析</h2>
                <p class="upload-subtitle">
                    物件情報のPDFファイルをドラッグ&ドロップ<br>
                    または下記ボタンから選択して物確を開始
                </p>
                
                <div class="file-input-wrapper">
                    <input type="file" id="pdf_file" name="pdf_file" accept=".pdf" required class="file-input">
                    <label for="pdf_file" class="file-input-label">
                        📁 ファイルを選択
                    </label>
                </div>
                
                <button type="submit" class="start-btn" id="startBtn">
                    🔍 物確実行
                </button>
                
            </div>
        </form>
        
        {% if results %}
        <div class="results-container">
            <div class="results-header">
                <h2>📊 物確結果</h2>
                <p>{{ results.property.address }}の確認状況</p>
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
                        <span class="site-name">ATBB</span>
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
            
            {% if results.phone_step %}
            <div class="phone-step-card {{ 'phone-required' if results.phone_step.phone_required else 'no-phone' }}">
                <h3>📞 Step 4: 電話確認</h3>
                <div class="phone-status">
                    <span class="phone-badge {{ 'required' if results.phone_step.phone_required else 'not-required' }}">
                        {{ '📞 電話確認必要' if results.phone_step.phone_required else '✅ 電話確認不要' }}
                    </span>
                </div>
                <div class="phone-notes">
                    {{ results.phone_step.notes.replace('\n', '<br>')|safe }}
                </div>
            </div>
            {% endif %}
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
        // DOM要素が完全に読み込まれるまで待機
        document.addEventListener('DOMContentLoaded', function() {
            // ドラッグ&ドロップ機能
            const uploadZone = document.getElementById('uploadZone');
            const fileInput = document.getElementById('pdf_file');
            const uploadForm = document.getElementById('uploadForm');
            
            // DOM要素が存在しない場合は早期return
            if (!uploadZone || !fileInput || !uploadForm) {
                console.warn('Required DOM elements not found');
                return;
            }
            
            try {
                // ドラッグ&ドロップイベントリスナー
                ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                    uploadZone.addEventListener(eventName, preventDefaults, false);
                });
                
                function preventDefaults(e) {
                    if (e) {
                        e.preventDefault();
                        e.stopPropagation();
                    }
                }
                
                ['dragenter', 'dragover'].forEach(eventName => {
                    uploadZone.addEventListener(eventName, highlight, false);
                });
                
                ['dragleave', 'drop'].forEach(eventName => {
                    uploadZone.addEventListener(eventName, unhighlight, false);
                });
                
                function highlight(e) {
                    if (uploadZone && uploadZone.style) {
                        uploadZone.style.borderColor = 'var(--color-accent)';
                        uploadZone.style.backgroundColor = 'rgba(255,61,109,0.05)';
                    }
                }
                
                function unhighlight(e) {
                    if (uploadZone && uploadZone.style) {
                        uploadZone.style.borderColor = 'rgba(255,61,109,0.3)';
                        uploadZone.style.backgroundColor = 'rgba(255,255,255,0.97)';
                    }
                }
                
                uploadZone.addEventListener('drop', handleDrop, false);
                
                function handleDrop(e) {
                    if (!e || !e.dataTransfer) return;
                    
                    const dt = e.dataTransfer;
                    const files = dt.files;
                    
                    if (files && files.length > 0 && fileInput) {
                        fileInput.files = files;
                        updateFileLabel(files[0].name);
                    }
                }
                
                fileInput.addEventListener('change', function() {
                    if (this.files && this.files.length > 0) {
                        updateFileLabel(this.files[0].name);
                    }
                });
                
                function updateFileLabel(fileName) {
                    const label = document.querySelector('.file-input-label');
                    if (label && fileName) {
                        label.innerHTML = `📄 ${fileName}`;
                    }
                }
                
                // フォーム送信時のローディング表示
                uploadForm.addEventListener('submit', function(e) {
                    const startBtn = document.getElementById('startBtn');
                    
                    if (startBtn) {
                        startBtn.innerHTML = '🔄 物確実行中...';
                        startBtn.disabled = true;
                    }
                    
                    // 段階的ローディング表示
                    const loadingHTML = `
                        <div class="loading-zone">
                            <div class="loading-spinner"></div>
                            <h3>物確実行中...</h3>
                            <div class="step-progress">
                                <div class="step active">Step 1: マイソク解析</div>
                                <div class="step">Step 2: ATBB検索</div>
                                <div class="step">Step 3: ITANDI検索</div>
                                <div class="step">Step 4: 電話確認準備</div>
                            </div>
                            <p>実際の不動産業務フローに沿って段階的に処理しています</p>
                        </div>
                    `;
                    
                    setTimeout(() => {
                        if (uploadZone) {
                            uploadZone.innerHTML = loadingHTML;
                        }
                    }, 500);
                });
                
            } catch (error) {
                console.error('JavaScript initialization error:', error);
            }
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
    """4ステップ物確システム"""
    try:
        # システム状態の確認
        if not PDF_ANALYZER_AVAILABLE:
            return render_template_string(HTML_TEMPLATE, error="PDF解析機能が利用できません。管理者にお問い合わせください。")
        
        # ファイル検証
        if 'pdf_file' not in request.files:
            return render_template_string(HTML_TEMPLATE, error="PDFファイルが選択されていません。")
        
        file = request.files['pdf_file']
        if not file or file.filename == '' or not file.filename.lower().endswith('.pdf'):
            return render_template_string(HTML_TEMPLATE, error="有効なPDFファイルを選択してください。")
        
        print(f"📁 ファイル受信: {file.filename}")
        
        # Step 1: マイソクPDF解析と物件情報抽出
        print("📋 Step 1: マイソク解析開始...")
        step1_result = perform_step1_extraction(file)
        if not step1_result['success']:
            return render_template_string(HTML_TEMPLATE, error=step1_result['error'])
        
        property_data = step1_result['property_data']
        property_obj = step1_result['property_obj']
        
        # Step 2: ATBB検索
        print("🌐 Step 2: ATBB検索開始...")
        step2_result = perform_step2_atbb_search(property_data)
        
        # Step 3: ITANDI検索
        print("🌐 Step 3: ITANDI検索開始...")
        step3_result = perform_step3_itandi_search(property_data)
        
        # Step 4: 電話確認準備
        print("📞 Step 4: 電話確認準備...")
        step4_result = perform_step4_phone_preparation(property_data, step2_result, step3_result)
        
        # 総合結果をまとめる
        results = compile_final_results(property_obj, step2_result, step3_result, step4_result)
        
        print("✅ 4ステップ物確完了")
        return render_template_string(HTML_TEMPLATE, results=results)
        
    except Exception as e:
        print(f"❌ システムエラー: {str(e)}")
        import traceback
        traceback.print_exc()
        return render_template_string(HTML_TEMPLATE, error=f"予期しないエラーが発生しました: {str(e)}")

def perform_step1_extraction(file):
    """Step 1: マイソク物件情報抽出"""
    try:
        analyzer = SimplePDFAnalyzer()
        pdf_results = analyzer.analyze_pdf(file)
        
        if not pdf_results.get('success', False):
            return {
                'success': False,
                'error': f"PDF処理エラー: {pdf_results.get('error', '不明なエラー')}"
            }
        
        properties = pdf_results.get('properties', [])
        if not properties:
            return {
                'success': False,
                'error': "物件情報を抽出できませんでした。正しいマイソクPDFかご確認ください。"
            }
        
        property_data = properties[0]
        property_obj = PropertyData(property_data)
        
        print(f"✅ Step 1完了: {property_data.get('address', 'N/A')}")
        return {
            'success': True,
            'property_data': property_data,
            'property_obj': property_obj
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f"Step 1エラー: {str(e)}"
        }

def perform_step2_atbb_search(property_data):
    """Step 2: ATBB検索実行"""
    try:
        browser_checker = RealBrowserPropertyChecker()
        browser_checker.property_data = property_data
        result = browser_checker._check_atbb_real()
        
        print(f"✅ Step 2完了 - ATBB: {'発見' if result['found'] else '未発見'}")
        return result
        
    except Exception as e:
        print(f"❌ Step 2エラー: {e}")
        return {
            'found': False,
            'confidence': 0.0,
            'error': f"ATBB検索エラー: {str(e)}",
            'notes': 'ATBB検索でエラーが発生しました'
        }

def perform_step3_itandi_search(property_data):
    """Step 3: ITANDI検索実行"""
    try:
        browser_checker = RealBrowserPropertyChecker()
        browser_checker.property_data = property_data
        result = browser_checker._check_itandi_real()
        
        print(f"✅ Step 3完了 - ITANDI: {'発見' if result['found'] else '未発見'}")
        return result
        
    except Exception as e:
        print(f"❌ Step 3エラー: {e}")
        return {
            'found': False,
            'confidence': 0.0,
            'error': f"ITANDI検索エラー: {str(e)}",
            'notes': 'ITANDI検索でエラーが発生しました'
        }

def perform_step4_phone_preparation(property_data, atbb_result, itandi_result):
    """Step 4: 電話確認が必要な物件の整理"""
    try:
        found_anywhere = atbb_result.get('found', False) or itandi_result.get('found', False)
        
        if found_anywhere:
            phone_required = False
            phone_notes = "🌐 Web検索で物件が確認できました。電話確認は不要です。"
        else:
            phone_required = True
            address = property_data.get('address', '住所不明')
            rent = property_data.get('rent', '賃料不明')
            layout = property_data.get('layout', '間取り不明')
            
            phone_notes = f"""📞 Web検索では物件が見つかりませんでした。電話確認が必要です。

確認事項:
• 物件の現在の募集状況
• 賃料・条件に変更はないか  
• 内見可能時期
• 申込み受付状況

物件情報:
• 住所: {address}
• 賃料: {rent}
• 間取り: {layout}

※管理会社・仲介会社への直接確認をお勧めします"""
        
        print(f"✅ Step 4完了 - 電話確認: {'必要' if phone_required else '不要'}")
        return {
            'phone_required': phone_required,
            'notes': phone_notes,
            'found_sites_count': sum([
                1 if atbb_result.get('found') else 0,
                1 if itandi_result.get('found') else 0
            ])
        }
        
    except Exception as e:
        print(f"❌ Step 4エラー: {e}")
        return {
            'phone_required': True,
            'notes': f"Step 4処理エラー: {str(e)}",
            'found_sites_count': 0
        }

def compile_final_results(property_obj, atbb_result, itandi_result, phone_result):
    """最終結果をまとめる"""
    total_sites = 2  # ATBB + ITANDI
    found_count = sum([
        1 if atbb_result.get('found') else 0,
        1 if itandi_result.get('found') else 0
    ])
    
    found_sites = []
    if atbb_result.get('found'): found_sites.append('ATBB')
    if itandi_result.get('found'): found_sites.append('ITANDI')
    
    overall_found = found_count > 0
    
    return {
        'total': total_sites,
        'found': found_count,
        'rate': (found_count / total_sites) * 100,
        'property': property_obj,
        'itandi': itandi_result,
        'suumo': atbb_result,  # フロントエンドではsuumoキーを使用
        'overall_found': overall_found,
        'found_sites': found_sites,
        'phone_step': phone_result,
        'step_by_step': True  # 段階的処理であることを示す
    }



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