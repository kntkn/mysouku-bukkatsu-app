"""
マイソク物確自動化アプリ 基本テスト
"""
import sys
from pathlib import Path
import tempfile
import io

# プロジェクトパスを追加
sys.path.append(str(Path(__file__).parent / "src"))
sys.path.append(str(Path(__file__).parent))

def test_pdf_analyzer():
    """PDF解析機能のテスト"""
    print("📄 PDF解析機能テスト開始...")
    
    try:
        from src.pdf_analyzer import PDFAnalyzer
        
        # テスト用のダミーPDFテキスト
        test_text = """
        物件No: P-001
        所在地: 東京都新宿区歌舞伎町1-1-1
        賃料: 12.5万円
        間取り: 1K
        面積: 25.0㎡
        JR山手線「新宿」駅 徒歩5分
        築15年
        管理費: 5,000円
        """
        
        analyzer = PDFAnalyzer()
        
        # テキストから物件情報抽出
        properties = analyzer.extract_property_info(test_text)
        
        if properties:
            print(f"✅ 物件情報抽出成功: {len(properties)}件")
            for prop in properties:
                print(f"   - 物件番号: {prop.get('property_number', '')}")
                print(f"   - 住所: {prop.get('address', '')}")
                print(f"   - 賃料: {prop.get('rent', '')}")
        else:
            print("⚠️ 物件情報を抽出できませんでした")
        
        print("✅ PDF解析機能テスト完了\n")
        return True
        
    except Exception as e:
        print(f"❌ PDF解析機能テストエラー: {e}\n")
        return False

def test_property_extractor():
    """物件情報抽出・正規化機能のテスト"""
    print("🔧 物件情報抽出・正規化機能テスト開始...")
    
    try:
        from src.property_extractor import PropertyExtractor
        
        # テストデータ
        raw_properties = [
            {
                'property_number': 'P-001',
                'address': '東京都新宿区歌舞伎町1-1-1',
                'rent': '12.5万円',
                'layout': '1K',
                'area': '25.0㎡',
                'station': 'JR山手線「新宿」駅',
                'walk_time': '5',
                'age': '築15年',
                'management_fee': '5,000円',
                'source_file': 'test.pdf',
                'raw_text': 'テストデータ'
            }
        ]
        
        extractor = PropertyExtractor()
        
        # 正規化
        normalized_properties = extractor.normalize_properties(raw_properties)
        valid_properties = extractor.filter_valid_properties(normalized_properties)
        
        if valid_properties:
            print(f"✅ 物件正規化成功: {len(valid_properties)}件")
            prop = valid_properties[0]
            print(f"   - 物件ID: {prop.property_id}")
            print(f"   - 住所: {prop.address}")
            print(f"   - 賃料: {prop.rent}")
            
            # 検索キーワード生成
            search_combinations = extractor.create_search_combinations(valid_properties)
            print(f"   - 検索キーワード: {len(search_combinations)}組合")
            
        else:
            print("⚠️ 有効な物件がありませんでした")
        
        print("✅ 物件情報抽出・正規化機能テスト完了\n")
        return True
        
    except Exception as e:
        print(f"❌ 物件情報抽出・正規化機能テストエラー: {e}\n")
        return False

def test_credentials():
    """ログイン情報管理機能のテスト"""
    print("🔑 ログイン情報管理機能テスト開始...")
    
    try:
        from config.credentials import CredentialsManager
        
        manager = CredentialsManager()
        
        # 利用可能サイトの確認
        sites = manager.get_all_sites()
        print(f"✅ 利用可能サイト: {', '.join(sites)}")
        
        # ITANDI情報取得
        itandi_creds = manager.get_credentials("itandi")
        print(f"✅ ITANDI ログイン: {itandi_creds.username}")
        
        # いえらぶBB情報取得
        ierabu_creds = manager.get_credentials("ierabu")
        print(f"✅ いえらぶBB ログイン: {ierabu_creds.username}")
        
        print("✅ ログイン情報管理機能テスト完了\n")
        return True
        
    except Exception as e:
        print(f"❌ ログイン情報管理機能テストエラー: {e}\n")
        return False

def test_report_generator():
    """レポート生成機能のテスト"""
    print("📊 レポート生成機能テスト開始...")
    
    try:
        from src.report_generator import ReportGenerator
        from dataclasses import dataclass
        
        # テストデータクラス
        @dataclass
        class TestProperty:
            property_id: str
            address: str
            rent: str
            layout: str
            area: str
            station_info: str
            walk_time: str
            age: str
            management_fee: str
            source_file: str
            raw_text: str
        
        @dataclass
        class TestResult:
            property_id: str
            found: bool
            availability_status: str
            listing_url: str
            rent_displayed: str
            notes: str
            error_message: str = ""
        
        # テストデータ作成
        test_properties = [
            TestProperty(
                property_id="P-001",
                address="東京都新宿区歌舞伎町1-1-1",
                rent="12.5万円",
                layout="1K",
                area="25.0㎡",
                station_info="JR山手線「新宿」駅",
                walk_time="5",
                age="築15年",
                management_fee="5,000円",
                source_file="test.pdf",
                raw_text="テストデータ"
            )
        ]
        
        test_itandi_results = [
            TestResult(
                property_id="P-001",
                found=True,
                availability_status="vacant",
                listing_url="https://example.com",
                rent_displayed="12.5万円",
                notes="テスト結果"
            )
        ]
        
        # 一時ディレクトリでテスト
        with tempfile.TemporaryDirectory() as temp_dir:
            report_generator = ReportGenerator(temp_dir)
            
            report_files = report_generator.generate_comprehensive_report(
                test_properties,
                test_itandi_results,
                []
            )
            
            print(f"✅ レポート生成成功: {len(report_files)}種類")
            for report_type, file_path in report_files.items():
                print(f"   - {report_type}: {Path(file_path).name}")
        
        print("✅ レポート生成機能テスト完了\n")
        return True
        
    except Exception as e:
        print(f"❌ レポート生成機能テストエラー: {e}\n")
        return False

def main():
    """メインテスト関数"""
    print("🏠 マイソク物確自動化アプリ 基本テスト")
    print("=" * 60)
    
    test_results = []
    
    # 各機能のテスト
    test_results.append(test_pdf_analyzer())
    test_results.append(test_property_extractor())
    test_results.append(test_credentials())
    test_results.append(test_report_generator())
    
    # 結果サマリー
    print("=" * 60)
    print("📋 テスト結果サマリー")
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"✅ 成功: {passed}/{total}")
    
    if passed == total:
        print("🎉 すべてのテストが成功しました！")
        print("\n🚀 アプリケーションを起動:")
        print("   streamlit run app.py")
        return True
    else:
        print("⚠️ 一部のテストが失敗しました")
        print("   エラー内容を確認して修正してください")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)