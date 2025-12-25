# 推奨コマンド・操作ガイド

## セットアップ・環境構築
```bash
# 初回セットアップ（すべて自動実行）
python3 setup.py

# 手動セットアップ
pip install -r requirements.txt
playwright install chromium
```

## 開発・テスト
```bash
# ローカル開発（Streamlit版）
streamlit run app.py

# ローカル開発（Flask版）
python3 app.py

# 基本機能テスト
python3 test_basic.py

# 簡易テスト
python3 test_simple.py
```

## デプロイ
```bash
# Vercelへのデプロイ
vercel --prod

# デプロイ前の動作確認
vercel dev
```

## ファイル管理
```bash
# プロジェクトルートディレクトリ
cd /Users/kentohonda/mysouku-bukkatsu-app

# ログ確認
ls -la data/logs/

# アップロードファイル確認
ls -la data/uploads/

# 生成レポート確認
ls -la data/reports/
```

## Git操作
```bash
# 状態確認
git status

# 変更をステージング
git add .

# コミット
git commit -m "機能追加: 物確4ステップ実装"

# プッシュ
git push origin main
```

## デバッグ・トラブルシューティング
```bash
# Python環境確認
python3 --version
pip list

# Playwright状態確認
playwright --version

# 環境変数確認
cat .env

# ログファイル確認
tail -f data/logs/app.log

# Vercelログ確認
vercel logs
```

## データクリーンアップ
```bash
# アップロードファイル削除
rm -rf data/uploads/*

# 一時ファイル削除
rm -rf data/extracted/*

# ログローテーション
find data/logs/ -name "*.log" -mtime +7 -delete
```

## システムコマンド（macOS）
```bash
# ファイル検索
find . -name "*.py" -type f

# テキスト検索
grep -r "物確" . --include="*.py"

# ディスク使用量確認
du -sh .

# プロセス確認
ps aux | grep python3

# ポート使用確認
lsof -i :5000  # Flask
lsof -i :8501  # Streamlit
```