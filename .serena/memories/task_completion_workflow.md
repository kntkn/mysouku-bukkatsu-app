# タスク完了時のワークフロー

## 1. コード品質チェック

### Python コードチェック
```bash
# 構文チェック
python3 -m py_compile app_fixed.py

# インポートチェック
python3 -c "import app_fixed"
```

### 手動チェック項目
- [ ] 関数・クラス名がsnake_case/PascalCaseルールに従っている
- [ ] docstringが適切に記述されている
- [ ] エラーハンドリングが実装されている
- [ ] ログ出力が適切に設定されている

## 2. 動作テスト

### ローカルテスト
```bash
# 基本機能テスト
python3 test_basic.py

# Webアプリケーション起動テスト
python3 app_fixed.py
# ブラウザで http://localhost:5000 にアクセスして動作確認
```

### Vercel デプロイテスト
```bash
# vercel.jsonの設定確認
cat vercel.json

# ローカルVercel環境でのテスト
vercel dev
# ブラウザで http://localhost:3000 にアクセス

# 本番デプロイ
vercel --prod
```

## 3. Git 操作

### コミット前チェック
```bash
# 変更内容確認
git status
git diff

# ステージング
git add .

# コミット（わかりやすいメッセージ）
git commit -m "fix: Vercelデプロイエラー修正 - app_fixed.pyに切り替え"
```

### プッシュとデプロイ
```bash
# リモートへプッシュ
git push origin main

# Vercelの自動デプロイ確認
# https://mysouku-bukkatsu-app.vercel.app/ でアクセス確認
```

## 4. デプロイ後確認

### 機能確認項目
1. [ ] トップページが正常に表示される
2. [ ] PDF アップロード機能が動作する
3. [ ] 4ステップの物確プロセスが実行される
4. [ ] エラーレスポンスが適切に表示される
5. [ ] モバイルデバイスでも表示が崩れない

### エラーハンドリング確認
- [ ] 大容量ファイルアップロード時のエラー処理
- [ ] 無効なPDFファイル時のエラー処理
- [ ] サーバーエラー時の適切なレスポンス

## 5. ドキュメント更新

### README.md更新
- [ ] 新機能の説明を追加
- [ ] デプロイURLの確認・更新
- [ ] 使用方法の説明を最新化

### バージョン管理
```bash
# タグ作成（重要な変更の場合）
git tag -a v1.1.0 -m "物確4ステップ実装完了"
git push origin --tags
```

## 緊急時の対応

### ロールバック手順
```bash
# 前のバージョンに戻す（Git）
git reset --hard HEAD~1
git push --force origin main

# Vercelで前のデプロイメントに切り替え
vercel --prod
```

### エラー調査
```bash
# Vercelログ確認
vercel logs

# ローカルでの再現テスト
python3 app_fixed.py
```

## 完了チェックリスト

### 最終確認項目
- [ ] ローカルテストが全て通る
- [ ] Vercelデプロイが成功する
- [ ] 本番環境でのアクセステストが通る
- [ ] エラーハンドリングが適切に動作する
- [ ] GitHubにソースコードが正しく反映されている
- [ ] READMEが最新の状態に更新されている