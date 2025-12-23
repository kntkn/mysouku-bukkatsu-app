"""
マイソク物確自動化アプリ セットアップスクリプト
"""
import subprocess
import sys
from pathlib import Path

def install_requirements():
    """依存関係をインストール"""
    print("📦 依存関係をインストール中...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 依存関係のインストール完了")
    except subprocess.CalledProcessError as e:
        print(f"❌ 依存関係のインストールに失敗: {e}")
        return False
    
    return True

def install_playwright():
    """Playwrightブラウザをインストール"""
    print("🌐 Playwrightブラウザをインストール中...")
    
    try:
        subprocess.check_call(["playwright", "install", "chromium"])
        print("✅ Playwrightブラウザのインストール完了")
    except subprocess.CalledProcessError as e:
        print(f"❌ Playwrightブラウザのインストールに失敗: {e}")
        return False
    
    return True

def create_directories():
    """必要なディレクトリを作成"""
    print("📁 ディレクトリを作成中...")
    
    directories = [
        "data",
        "data/uploads",
        "data/extracted", 
        "data/reports",
        "data/logs"
    ]
    
    for dir_name in directories:
        dir_path = Path(dir_name)
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"   📂 {dir_name}")
    
    print("✅ ディレクトリ作成完了")

def setup_environment():
    """環境設定ファイルを作成"""
    print("⚙️ 環境設定を準備中...")
    
    env_file = Path(".env")
    if not env_file.exists():
        # .env.exampleから.envを作成
        example_file = Path(".env.example")
        if example_file.exists():
            with open(example_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("📝 .envファイルを作成しました")
            print("   必要に応じて設定値を編集してください")
        else:
            print("⚠️ .env.exampleが見つかりません")
    else:
        print("✅ .envファイルは既に存在します")

def main():
    """セットアップメイン処理"""
    print("🏠 マイソク物確自動化アプリ セットアップ")
    print("=" * 50)
    
    # 1. ディレクトリ作成
    create_directories()
    
    # 2. 環境設定
    setup_environment()
    
    # 3. 依存関係インストール
    if not install_requirements():
        print("❌ セットアップに失敗しました")
        return
    
    # 4. Playwrightブラウザインストール
    if not install_playwright():
        print("⚠️ Playwrightブラウザのインストールに失敗しましたが、続行します")
    
    print("\n" + "=" * 50)
    print("🎉 セットアップ完了!")
    print("\n📋 次のステップ:")
    print("1. アプリを起動: streamlit run app.py")
    print("2. ブラウザで http://localhost:8501 にアクセス")
    print("3. マイソクPDFをアップロードして物確開始")
    print("\n💡 ヒント:")
    print("- .envファイルで設定をカスタマイズできます")
    print("- data/logsフォルダでログを確認できます")

if __name__ == "__main__":
    main()