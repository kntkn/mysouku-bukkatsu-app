# コーディング規約・スタイルガイド

## ファイル・ディレクトリ構造
```
mysouku-bukkatsu-app/
├── app.py / app_fixed.py    # メインFlaskアプリ
├── test_simple.py           # 緊急テスト用簡易アプリ
├── src/                     # コアモジュール
│   ├── pdf_analyzer.py      # PDF解析
│   ├── property_extractor.py # 物件情報抽出
│   ├── itandi_checker.py    # ITANDI物確
│   └── ...
├── config/                  # 設定ファイル
├── data/                    # データ格納
├── requirements.txt         # Python依存関係
├── vercel.json             # Vercel設定
└── setup.py                # 自動セットアップスクリプト
```

## Python コーディングスタイル

### 命名規則
- **関数**: snake_case（例：`extract_property_from_text`）
- **クラス**: PascalCase（例：`SimpleProperty`）
- **定数**: UPPER_SNAKE_CASE（例：`HTML_TEMPLATE`）
- **変数**: snake_case

### ドキュメンテーション
```python
def perform_step1_extraction(pdf_content):
    """
    Step 1: マイソクから物件情報を抽出
    
    Args:
        pdf_content: PDFファイルのバイナリデータ
        
    Returns:
        dict: 抽出された物件情報
    """
```

### エラーハンドリング
- 段階的なフォールバック処理を実装
- ユーザーフレンドリーなエラーメッセージ
- ログ出力でデバッグ情報を残す

### Flask ルート設計
- RESTful な設計を意識
- JSON レスポンスで統一
- 適切なHTTPステータスコード

## HTML/CSS スタイル

### HTML構造
- セマンティックHTMLを使用
- モダンなHTML5構造
- アクセシビリティを考慮

### CSS設計
- CSS変数を使用したテーマ管理
- レスポンシブデザイン
- モダンCSS（Grid/Flexbox）

### JavaScript
- Vanilla JavaScript を使用
- DOM操作の安全性を重視
- 非同期処理でUX向上

## Git規約
- ブランチ: feature/機能名、fix/修正内容
- コミットメッセージ: 日本語OK、何をしたかを明確に