"""
マイソク物確自動化アプリ - Vercel版（ライト）
PDF解析・レポート機能のみ（ブラウザ自動化は無効）
"""
import streamlit as st
import pandas as pd
import time
import os
from pathlib import Path
import sys
import tempfile

# プロジェクトのsrcディレクトリをパスに追加
sys.path.append(str(Path(__file__).parent / "src"))
sys.path.append(str(Path(__file__).parent))

from src.pdf_analyzer import PDFAnalyzer
from src.property_extractor import PropertyExtractor
from src.report_generator import ReportGenerator
from config.settings import STREAMLIT_CONFIG, PDF_CONFIG

# Streamlit設定
st.set_page_config(**STREAMLIT_CONFIG)

# セッション状態の初期化
if 'properties' not in st.session_state:
    st.session_state.properties = []
if 'extracted_file' not in st.session_state:
    st.session_state.extracted_file = None

def create_temp_directories():
    """一時ディレクトリを作成"""
    if 'temp_dirs' not in st.session_state:
        st.session_state.temp_dirs = {
            'reports': tempfile.mkdtemp(prefix='reports_')
        }

def main():
    """メイン関数"""
    create_temp_directories()
    
    st.title("🏠 マイソク解析アプリ（クラウド版）")
    st.markdown("---")
    
    # 注意書き
    st.info("💡 **クラウド版の制限**: PDF解析・レポート生成のみ利用可能です。物確機能をご利用の場合は、ローカル版をダウンロードしてご利用ください。")
    
    # サイドバー
    with st.sidebar:
        st.header("📋 操作メニュー")
        
        # 処理状況
        st.subheader("処理状況")
        if st.session_state.properties:
            st.success(f"✅ 物件抽出: {len(st.session_state.properties)}件")
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
            st.experimental_rerun()
    
    # メインコンテンツ
    tab1, tab2, tab3 = st.tabs(["📄 PDF処理", "📊 結果確認", "📋 レポート"])
    
    with tab1:
        st.header("📄 マイソクPDF処理")
        
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
                        layout_df = pd.DataFrame(
                            list(layout_counts.items()), 
                            columns=['間取り', '件数']
                        )
                        st.bar_chart(layout_df.set_index('間取り'))
    
    with tab3:
        st.header("📋 レポート生成・ダウンロード")
        
        if not st.session_state.properties:
            st.warning("⚠️ まず PDF処理を完了してください")
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
                                
                                report_files = report_generator.generate_comprehensive_report(
                                    st.session_state.properties,
                                    [],  # 物確結果なし
                                    []   # 物確結果なし
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