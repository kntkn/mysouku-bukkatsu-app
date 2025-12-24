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

app = Flask(__name__)

# HTML テンプレート
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>マイソク物確自動化アプリ</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5em;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: #555;
        }
        input[type="text"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 25px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            display: inline-block;
            text-decoration: none;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .results {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 5px solid #667eea;
        }
        .property-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .status-good { color: #28a745; }
        .status-bad { color: #dc3545; }
        .loading {
            text-align: center;
            padding: 20px;
            color: #666;
        }
        .metric {
            text-align: center;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }
        .metric-label {
            color: #666;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏠 マイソク物確自動化アプリ</h1>
        
        <form method="POST" action="/">
            <div class="grid">
                <div class="form-group">
                    <label for="address">住所</label>
                    <input type="text" id="address" name="address" value="{{ request.form.get('address', '東京都渋谷区') }}" required>
                </div>
                <div class="form-group">
                    <label for="rent">賃料</label>
                    <input type="text" id="rent" name="rent" value="{{ request.form.get('rent', '15万円') }}" required>
                </div>
                <div class="form-group">
                    <label for="layout">間取り</label>
                    <input type="text" id="layout" name="layout" value="{{ request.form.get('layout', '1K') }}" required>
                </div>
                <div class="form-group">
                    <label for="station">最寄り駅</label>
                    <input type="text" id="station" name="station" value="{{ request.form.get('station', '渋谷駅徒歩5分') }}" required>
                </div>
            </div>
            
            <div style="text-align: center;">
                <button type="submit" class="btn">🔍 物確実行</button>
            </div>
        </form>
        
        {% if results %}
        <div class="results">
            <h2>📊 物確結果</h2>
            
            <div class="grid" style="margin-bottom: 20px;">
                <div class="metric">
                    <div class="metric-value">{{ results.total }}</div>
                    <div class="metric-label">総確認数</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{{ results.found }}</div>
                    <div class="metric-label">発見件数</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{{ "%.1f"|format(results.rate) }}%</div>
                    <div class="metric-label">発見率</div>
                </div>
            </div>
            
            <div class="property-card">
                <h3>物件: {{ results.property.address }}</h3>
                <p><strong>賃料:</strong> {{ results.property.rent }} | <strong>間取り:</strong> {{ results.property.layout }}</p>
                <p><strong>最寄り駅:</strong> {{ results.property.station }}</p>
                
                <div style="margin-top: 15px;">
                    <p><strong>ITANDI:</strong> 
                        {% if results.itandi.found %}
                        <span class="status-good">✅ 発見 (信頼度: {{ "%.1f"|format(results.itandi.confidence * 100) }}%)</span>
                        {% else %}
                        <span class="status-bad">❌ 未発見</span>
                        {% endif %}
                    </p>
                    <p><strong>いえらぶBB:</strong> 
                        {% if results.ierabu.found %}
                        <span class="status-good">✅ 発見 (信頼度: {{ "%.1f"|format(results.ierabu.confidence * 100) }}%)</span>
                        {% else %}
                        <span class="status-bad">❌ 未発見</span>
                        {% endif %}
                    </p>
                    <p><strong>SUUMO:</strong> 
                        {% if results.suumo.found %}
                        <span class="status-good">✅ 発見 (信頼度: {{ "%.1f"|format(results.suumo.confidence * 100) }}%)</span>
                        {% else %}
                        <span class="status-bad">❌ 未発見</span>
                        {% endif %}
                    </p>
                </div>
                
                {% if results.overall_found %}
                <div style="margin-top: 10px; padding: 10px; background: #d4edda; color: #155724; border-radius: 5px;">
                    <strong>✅ 総合判定: 発見</strong>
                </div>
                {% else %}
                <div style="margin-top: 10px; padding: 10px; background: #f8d7da; color: #721c24; border-radius: 5px;">
                    <strong>❌ 総合判定: 未発見</strong>
                </div>
                {% endif %}
            </div>
        </div>
        {% endif %}
        
        <div style="margin-top: 40px; text-align: center; color: #666;">
            <p>🚀 Powered by Vercel | <a href="https://github.com/kntkn/mysouku-bukkatsu-app" style="color: #667eea;">GitHub</a></p>
        </div>
    </div>
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

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # フォームデータ取得
        address = request.form['address']
        rent = request.form['rent']
        layout = request.form['layout']
        station = request.form['station']
        
        # 物件作成
        property_data = {
            'address': address,
            'rent': rent,
            'layout': layout,
            'station_info': station
        }
        
        # 物確実行
        checker = CloudPropertyChecker()
        
        itandi_result = checker.search_itandi(property_data)
        ierabu_result = checker.search_ierabu(property_data)
        suumo_result = checker.search_suumo(property_data)
        
        overall_found = any([
            itandi_result.get('found', False),
            ierabu_result.get('found', False),
            suumo_result.get('found', False)
        ])
        
        # 結果をテンプレートに渡す
        results = {
            'total': 1,
            'found': 1 if overall_found else 0,
            'rate': 100.0 if overall_found else 0.0,
            'property': SimpleProperty(address, rent, layout, station),
            'itandi': itandi_result,
            'ierabu': ierabu_result,
            'suumo': suumo_result,
            'overall_found': overall_found
        }
        
        return render_template_string(HTML_TEMPLATE, results=results)
    
    return render_template_string(HTML_TEMPLATE)

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