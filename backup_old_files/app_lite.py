"""
マイソク物確自動化アプリ - クラウド版
PDF解析・物確検索機能（スクレイピングベース）
"""
import streamlit as st
import time
import os
from pathlib import Path
import sys
import tempfile

# プロジェクトのsrcディレクトリをパスに追加
sys.path.append(str(Path(__file__).parent / "src"))
sys.path.append(str(Path(__file__).parent))

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    from src.pdf_analyzer import PDFAnalyzer
    from src.property_extractor import PropertyExtractor
    from src.report_generator import ReportGenerator
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

from src.cloud_checker import CloudPropertyChecker

# 簡易設定
STREAMLIT_CONFIG = {
    "page_title": "マイソク物確自動化アプリ",
    "page_icon": "🏠",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Streamlit設定
st.set_page_config(**STREAMLIT_CONFIG)

# セッション状態の初期化
if 'properties' not in st.session_state:
    st.session_state.properties = []
if 'extracted_file' not in st.session_state:
    st.session_state.extracted_file = None
if 'bukkatsu_results' not in st.session_state:
    st.session_state.bukkatsu_results = []

def create_temp_directories():
    """一時ディレクトリを作成"""
    if 'temp_dirs' not in st.session_state:
        try:
            st.session_state.temp_dirs = {
                'reports': tempfile.mkdtemp(prefix='reports_')
            }
        except Exception:
            # フォールバック: 現在ディレクトリを使用
            st.session_state.temp_dirs = {
                'reports': '.'
            }

def main():
    """メイン関数"""
    create_temp_directories()
    
    st.title("🏠 マイソク物確自動化アプリ（クラウド版）")
    st.markdown("---")
    
    # 機能説明
    st.info("💡 **クラウド版機能**: PDF解析・レポート生成・物確検索（Web検索ベース）が利用可能です。")
    
    # サイドバー
    with st.sidebar:
        st.header("📋 操作メニュー")
        
        # 処理状況
        st.subheader("処理状況")
        if st.session_state.properties:
            st.success(f"✅ 物件抽出: {len(st.session_state.properties)}件")
            if st.session_state.bukkatsu_results:
                found_count = sum(1 for r in st.session_state.bukkatsu_results if r.get('overall_found'))
                st.success(f"✅ 物確完了: {found_count}/{len(st.session_state.bukkatsu_results)}件発見")
            else:
                st.info("🔍 物確実行待ち")
        else:
            st.info("📄 PDFをアップロードしてください")
        
        # ローカル版ダウンロード案内
        st.subheader("🏠 完全版ダウンロード")
        st.markdown("""
        **物確機能付き完全版**  
        [GitHub リポジトリ](https://github.com/YOUR_USERNAME/mysouku-bukkatsu-app)  
        
        完全版では以下が利用可能：
        - ITANDI物確
        - いえらぶBB物確  
        - 自動ログイン
        - ブラウザ自動化
        """)
        
        # リセットボタン
        if st.button("🔄 リセット", type="secondary"):
            st.session_state.properties = []
            st.session_state.extracted_file = None
            st.session_state.bukkatsu_results = []
            st.experimental_rerun()
    
    # メインコンテンツ
    tab1, tab2, tab3, tab4 = st.tabs(["📄 PDF処理", "🔍 物確実行", "📊 結果確認", "📋 レポート"])
    
    with tab1:
        st.header("📄 マイソクPDF処理")
        
        if not PDF_AVAILABLE:
            st.error("❌ PDF処理機能は現在利用できません（依存関係不足）")
            st.info("💡 代替案: 手動で物件情報を入力して物確機能をテストできます")
            
            # 手動入力フォーム
            with st.expander("🖊️ 手動物件入力（テスト用）"):
                with st.form("manual_input"):
                    col1, col2 = st.columns(2)
                    with col1:
                        address = st.text_input("住所", value="東京都渋谷区")
                        rent = st.text_input("賃料", value="15万円")
                    with col2:
                        layout = st.text_input("間取り", value="1K")
                        station = st.text_input("最寄り駅", value="渋谷駅徒歩5分")
                    
                    if st.form_submit_button("➕ テスト物件追加"):
                        # 簡易プロパティクラス
                        class TestProperty:
                            def __init__(self, address, rent, layout, station):
                                self.property_id = f"TEST_{len(st.session_state.properties)+1:03d}"
                                self.address = address
                                self.rent = rent
                                self.layout = layout
                                self.station_info = station
                                self.area = ""
                                self.age = ""
                                self.management_fee = ""
                                self.walk_time = ""
                                self.source_file = "手動入力"
                        
                        test_prop = TestProperty(address, rent, layout, station)
                        st.session_state.properties.append(test_prop)
                        st.success(f"✅ テスト物件を追加しました: {address}")
                        st.experimental_rerun()
            return
        
        # ファイルアップロード
        uploaded_files = st.file_uploader(
            "マイソクPDFファイルをアップロード",
            type=["pdf"],
            accept_multiple_files=True,
            help="複数のPDFファイルを同時にアップロードできます"
        )
        
        if uploaded_files:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.info(f"📁 {len(uploaded_files)}個のPDFファイルがアップロードされました")
                for file in uploaded_files:
                    st.write(f"• {file.name} ({file.size:,} bytes)")
            
            with col2:
                if st.button("🔄 PDF解析実行", type="primary", use_container_width=True):
                    with st.spinner("PDF解析中..."):
                        try:
                            # PDF解析
                            analyzer = PDFAnalyzer()
                            raw_properties = analyzer.analyze_multiple_pdfs(uploaded_files)
                            
                            if raw_properties:
                                # 物件情報正規化
                                extractor = PropertyExtractor()
                                normalized_properties = extractor.normalize_properties(raw_properties)
                                valid_properties = extractor.filter_valid_properties(normalized_properties)
                                
                                # セッション状態に保存
                                st.session_state.properties = valid_properties
                                
                                st.success(f"✅ {len(valid_properties)}件の物件情報を抽出しました")
                                
                                # プレビュー表示
                                if valid_properties:
                                    preview_data = []
                                    for prop in valid_properties[:5]:  # 最初の5件のみ表示
                                        preview_data.append({
                                            "物件ID": prop.property_id,
                                            "住所": prop.address[:50] + "..." if len(prop.address) > 50 else prop.address,
                                            "賃料": prop.rent,
                                            "間取り": prop.layout,
                                            "駅": prop.station_info[:30] + "..." if len(prop.station_info) > 30 else prop.station_info
                                        })
                                    
                                    st.subheader("📋 抽出データプレビュー")
                                    st.dataframe(preview_data, use_container_width=True)
                                    
                                    if len(valid_properties) > 5:
                                        st.info(f"プレビューは最初の5件のみ表示しています。全{len(valid_properties)}件")
                            else:
                                st.warning("⚠️ PDFから物件情報を抽出できませんでした")
                                
                        except Exception as e:
                            st.error(f"❌ PDF解析エラー: {str(e)}")
    
    with tab2:
        st.header("🔍 物確実行")
        
        if not st.session_state.properties:
            st.warning("⚠️ まずPDF処理を完了してください")
        else:
            st.subheader("📋 抽出済み物件")
            st.info(f"✅ {len(st.session_state.properties)}件の物件が抽出済みです")
            
            # 物確実行ボタン
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write("**対象サイト**: ITANDI、いえらぶBB、SUUMO")
                st.write("**実行方式**: Web検索ベース（クラウド版）")
            
            with col2:
                if st.button("🚀 物確実行", type="primary", use_container_width=True):
                    with st.spinner("物確実行中..."):
                        try:
                            checker = CloudPropertyChecker()
                            
                            # 物確実行
                            st.session_state.bukkatsu_results = checker.perform_bukkatsu_check(
                                st.session_state.properties
                            )
                            
                            st.success(f"✅ {len(st.session_state.bukkatsu_results)}件の物確が完了しました！")
                            
                        except Exception as e:
                            st.error(f"❌ 物確エラー: {str(e)}")
            
            # 物確結果プレビュー
            if st.session_state.bukkatsu_results:
                st.subheader("📊 物確結果プレビュー")
                
                # サマリー
                total_results = len(st.session_state.bukkatsu_results)
                found_count = sum(1 for r in st.session_state.bukkatsu_results if r.get('overall_found'))
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("総確認数", total_results)
                with col2:
                    st.metric("発見件数", found_count)
                with col3:
                    st.metric("発見率", f"{found_count/total_results*100:.1f}%")
                
                # 結果テーブル
                result_data = []
                for result in st.session_state.bukkatsu_results[:5]:  # 最初の5件
                    prop = result['property']
                    result_data.append({
                        "物件ID": prop.property_id,
                        "住所": prop.address[:30] + "..." if len(prop.address) > 30 else prop.address,
                        "ITANDI": "✅" if result['itandi'].get('found') else "❌",
                        "いえらぶBB": "✅" if result['ierabu'].get('found') else "❌", 
                        "SUUMO": "✅" if result['suumo'].get('found') else "❌",
                        "総合": "✅ 発見" if result.get('overall_found') else "❌ 未発見"
                    })
                
                st.dataframe(result_data, use_container_width=True)
                
                if len(st.session_state.bukkatsu_results) > 5:
                    st.info(f"プレビューは最初の5件のみ表示しています。全{len(st.session_state.bukkatsu_results)}件")

    with tab3:
        st.header("📊 抽出結果確認")
        
        if not st.session_state.properties:
            st.warning("⚠️ まずPDF処理を完了してください")
        else:
            # サマリーカード表示
            col1, col2, col3, col4 = st.columns(4)
            
            total_properties = len(st.session_state.properties)
            
            with col1:
                st.metric("総物件数", total_properties)
            with col2:
                rent_properties = len([p for p in st.session_state.properties if p.rent])
                st.metric("賃料情報有", rent_properties)
            with col3:
                address_properties = len([p for p in st.session_state.properties if p.address])
                st.metric("住所情報有", address_properties)
            with col4:
                station_properties = len([p for p in st.session_state.properties if p.station_info])
                st.metric("駅情報有", station_properties)
            
            # 詳細データ表示
            st.subheader("📋 抽出データ詳細")
            
            if st.session_state.properties:
                detail_data = []
                for prop in st.session_state.properties:
                    detail_data.append({
                        "物件ID": prop.property_id,
                        "住所": prop.address,
                        "賃料": prop.rent,
                        "間取り": prop.layout,
                        "面積": prop.area,
                        "駅情報": prop.station_info,
                        "徒歩": f"{prop.walk_time}分" if prop.walk_time else "",
                        "築年数": prop.age,
                        "管理費": prop.management_fee,
                        "ファイル": prop.source_file
                    })
                
                st.dataframe(detail_data, use_container_width=True)
                
                # 統計情報
                st.subheader("📊 統計情報")
                
                # 間取り分布
                if any(prop.layout for prop in st.session_state.properties):
                    layout_counts = {}
                    for prop in st.session_state.properties:
                        if prop.layout:
                            layout_counts[prop.layout] = layout_counts.get(prop.layout, 0) + 1
                    
                    if layout_counts:
                        if PANDAS_AVAILABLE:
                            layout_df = pd.DataFrame(
                                list(layout_counts.items()), 
                                columns=['間取り', '件数']
                            )
                            st.bar_chart(layout_df.set_index('間取り'))
                        else:
                            # pandasなしでの表示
                            st.write("**間取り分布:**")
                            for layout, count in layout_counts.items():
                                st.write(f"- {layout}: {count}件")
    
    with tab4:
        st.header("📋 レポート生成・ダウンロード")
        
        if not st.session_state.properties:
            st.warning("⚠️ まず物件情報を用意してください")
        elif not PDF_AVAILABLE:
            st.error("❌ レポート生成機能は現在利用できません（依存関係不足）")
            
            # 簡易結果表示
            if st.session_state.bukkatsu_results:
                st.subheader("📊 物確結果サマリー")
                
                total = len(st.session_state.bukkatsu_results)
                found = sum(1 for r in st.session_state.bukkatsu_results if r.get('overall_found'))
                
                st.metric("総物件数", total)
                st.metric("発見件数", found) 
                st.metric("発見率", f"{found/total*100:.1f}%")
        else:
            st.subheader("📄 レポート形式選択")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                report_types = st.multiselect(
                    "生成するレポート形式",
                    ["Excel (詳細)", "HTML (ビジュアル)", "CSV (軽量)", "JSON (API用)"],
                    default=["Excel (詳細)", "CSV (軽量)"]
                )
            
            with col2:
                if st.button("📋 レポート生成", type="primary", use_container_width=True):
                    if not report_types:
                        st.warning("⚠️ 少なくとも1つのレポート形式を選択してください")
                    else:
                        with st.spinner("📋 レポート生成中..."):
                            try:
                                # レポート生成
                                report_generator = ReportGenerator(st.session_state.temp_dirs['reports'])
                                
                                # 物確結果をレポートに含める
                                itandi_results = []
                                ierabu_results = []
                                
                                if st.session_state.bukkatsu_results:
                                    for result in st.session_state.bukkatsu_results:
                                        if result['itandi'].get('found'):
                                            itandi_results.append(result)
                                        if result['ierabu'].get('found'):
                                            ierabu_results.append(result)
                                
                                report_files = report_generator.generate_comprehensive_report(
                                    st.session_state.properties,
                                    itandi_results,
                                    ierabu_results
                                )
                                
                                st.success("✅ レポート生成完了!")
                                
                                # ダウンロードボタン
                                format_mapping = {
                                    "Excel (詳細)": "excel",
                                    "HTML (ビジュアル)": "html", 
                                    "CSV (軽量)": "csv",
                                    "JSON (API用)": "json"
                                }
                                
                                for report_type in report_types:
                                    file_key = format_mapping.get(report_type)
                                    if file_key and file_key in report_files:
                                        file_path = report_files[file_key]
                                        if os.path.exists(file_path):
                                            with open(file_path, 'rb') as f:
                                                file_data = f.read()
                                            
                                            file_name = os.path.basename(file_path)
                                            st.download_button(
                                                f"📥 {report_type} ダウンロード",
                                                data=file_data,
                                                file_name=file_name,
                                                key=f"download_{file_key}"
                                            )
                                
                                # HTML プレビュー
                                if "HTML (ビジュアル)" in report_types and "html" in report_files:
                                    html_file = report_files["html"]
                                    if os.path.exists(html_file):
                                        with st.expander("👀 HTMLレポート プレビュー", expanded=False):
                                            with open(html_file, 'r', encoding='utf-8') as f:
                                                html_content = f.read()
                                            st.components.v1.html(html_content, height=600, scrolling=True)
                                
                            except Exception as e:
                                st.error(f"❌ レポート生成エラー: {str(e)}")

if __name__ == "__main__":
    main()