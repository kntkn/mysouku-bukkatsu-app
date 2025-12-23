# マイソク物確自動化アプリ

## 概要
マイソクPDFから物件情報を自動抽出し、ITANDI・いえらぶBBで物確（物件確認）を自動実行するWebアプリケーション

## 機能
1. **PDFアップロード**: 複数PDFファイル、統合PDFファイル対応
2. **物件情報抽出**: PDFからテキスト抽出、物件情報の構造化
3. **自動物確**: ITANDI → いえらぶBB → その他サイトの順で確認
4. **結果レポート**: 物確状況の一覧表示、詳細表示

## 技術スタック
- **フロントエンド**: Streamlit
- **PDF処理**: pdfplumber, PyPDF2
- **Web自動化**: Playwright
- **バックエンド**: Python 3.x
- **データ処理**: pandas, openpyxl

## ディレクトリ構造
```
mysouku-bukkatsu-app/
├── app.py                 # Streamlit メインアプリ
├── requirements.txt       # 依存パッケージ
├── config/
│   ├── credentials.py     # ログイン情報管理
│   └── settings.py        # アプリ設定
├── src/
│   ├── pdf_analyzer.py    # PDF解析
│   ├── property_extractor.py  # 物件情報抽出
│   ├── itandi_checker.py  # ITANDI物確
│   ├── ierabu_checker.py  # いえらぶBB物確
│   └── report_generator.py # レポート生成
├── data/
│   ├── uploads/           # アップロードPDF
│   ├── extracted/         # 抽出データ
│   └── reports/           # 物確レポート
└── tests/                 # テストファイル
```

## 物確フロー
1. **PDF → テキスト抽出** 
2. **物件情報パース** (物件番号、住所、賃料等)
3. **ITANDI検索** → 結果記録
4. **いえらぶBB検索** → 結果記録
5. **結果統合・レポート生成**

## 使用方法
```bash
# 依存関係インストール
pip install -r requirements.txt

# Playwrightブラウザインストール
playwright install

# アプリ起動
streamlit run app.py
```

## 物確サイト
- **ITANDI**: https://itandibb.com/
- **いえらぶBB**: https://bb.ielove.jp/