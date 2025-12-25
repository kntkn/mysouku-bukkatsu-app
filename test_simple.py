"""
緊急テスト用：超シンプルなFlaskアプリ
"""
from flask import Flask

app = Flask(__name__)

@app.route('/')
def test():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>緊急テスト</title>
</head>
<body>
    <h1>✅ アプリは正常動作中</h1>
    <p>この画面が表示されれば、サーバーは正常です。</p>
    <p>時刻: 2024-12-25 12:42</p>
    
    <form method="POST" action="/test-upload">
        <input type="file" name="test_file" accept=".pdf">
        <button type="submit">テスト送信</button>
    </form>
</body>
</html>
"""

@app.route('/test-upload', methods=['POST'])
def test_upload():
    return "✅ POST送信成功！ファイル処理も動作中"

if __name__ == '__main__':
    app.run()