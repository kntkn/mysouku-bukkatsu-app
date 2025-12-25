# プロジェクト概要

## プロジェクトの目的
マイソクPDFから物件情報を自動抽出し、ITANDI・いえらぶBBで物確（物件確認）を自動実行するWebアプリケーション。

### 主要機能
- **PDF解析**: マイソクPDFから物件情報（物件番号、住所、賃料、間取り、駅情報等）を自動抽出
- **物確自動化**: ITANDI・いえらぶBBでの自動物確実行
- **レポート生成**: Excel/HTML/CSV/JSON形式での結果出力
- **Webインターフェース**: StreamlitベースのWebUI

### 現在の問題
- Vercel上でのデプロイ時にエラーが発生
- 複雑な依存関係によるサーバーレス環境での動作不安定
- 緊急対応として最小機能のtest_simple.pyでテスト済み

### 解決策
app_fixed.pyで簡素化された依存関係のない実装を作成済み。
現在はtest_simple.pyがデプロイされているが、本格機能のapp_fixed.pyへの切り替えが必要。

## テック スタック

### フロントエンド
- **Flask**: Webアプリケーションフレームワーク
- **HTML/CSS/JavaScript**: UI実装

### バックエンド（Python）
- **Flask**: メインWebフレームワーク
- **pdfplumber/PyPDF2**: PDF処理
- **requests/beautifulsoup4**: Web scraping
- **python-dotenv**: 環境変数管理
- **pillow**: 画像処理

### デプロイ・インフラ
- **Vercel**: サーバーレスデプロイプラットフォーム
- **GitHub**: ソースコード管理
- **Python 3.9+**: 実行環境

### 開発・自動化ツール
- **Playwright**: ブラウザ自動化（ローカル版）
- **Streamlit**: 開発時のWebUI（ローカル版）