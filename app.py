"""
マイソク物確自動化 - Streamlit メインアプリケーション
"""
import streamlit as st
import pandas as pd
import asyncio
import time
import os
from pathlib import Path
import sys

# プロジェクトのsrcディレクトリをパスに追加
sys.path.append(str(Path(__file__).parent / "src"))
sys.path.append(str(Path(__file__).parent))

from src.pdf_analyzer import PDFAnalyzer
from src.property_extractor import PropertyExtractor
from src.itandi_checker import check_properties_itandi
from src.ierabu_checker import check_properties_ierabu
from src.report_generator import ReportGenerator
from config.settings import STREAMLIT_CONFIG, PDF_CONFIG, DATA_DIR, UPLOAD_DIR, REPORTS_DIR

# Streamlit設定
st.set_page_config(**STREAMLIT_CONFIG)

# セッション状態の初期化
if 'properties' not in st.session_state:
    st.session_state.properties = []
if 'extracted_file' not in st.session_state:
    st.session_state.extracted_file = None
if 'bukkatsu_results' not in st.session_state:
    st.session_state.bukkatsu_results = {}

def create_directories():
    """必要なディレクトリを作成"""
    for dir_path in [DATA_DIR, UPLOAD_DIR, REPORTS_DIR]:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

async def run_bukkatsu_async(search_combinations):
    """非同期で物確を実行"""
    results = {}
    
    # ITANDI物確
    with st.spinner("ITANDI で物確実行中..."):
        try:
            itandi_results = await check_properties_itandi(search_combinations)
            results['itandi'] = itandi_results
            st.success(f"ITANDI: {len(itandi_results)}件の物確完了")
        except Exception as e:
            st.error(f"ITANDI物確エラー: {str(e)}")
            results['itandi'] = []
    
    # いえらぶBB物確
    with st.spinner("いえらぶBB で物確実行中..."):
        try:
            ierabu_results = await check_properties_ierabu(search_combinations)
            results['ierabu'] = ierabu_results
            st.success(f"いえらぶBB: {len(ierabu_results)}件の物確完了")
        except Exception as e:
            st.error(f"いえらぶBB物確エラー: {str(e)}")
            results['ierabu'] = []
    
    return results

def main():
    """メイン関数"""
    create_directories()
    
    st.title("🏠 マイソク物確自動化アプリ")
    st.markdown("---")
    
    # サイドバー
    with st.sidebar:
        st.header("📋 操作メニュー")
        
        # 処理状況
        st.subheader("処理状況")
        if st.session_state.properties:
            st.success(f"✅ 物件抽出: {len(st.session_state.properties)}件")
        else:
            st.info("📄 PDFをアップロードしてください")
        
        if st.session_state.bukkatsu_results:
            for site, results in st.session_state.bukkatsu_results.items():
                found_count = len([r for r in results if getattr(r, 'found', False)])
                st.success(f"✅ {site.upper()}: {found_count}/{len(results)}件発見")
        
        # 設定
        st.subheader("⚙️ 設定")
        headless_mode = st.checkbox("バックグラウンド実行", value=True, 
                                  help="ブラウザを表示せずに物確を実行")
        
        # リセットボタン
        if st.button("🔄 リセット", type="secondary"):
            st.session_state.properties = []
            st.session_state.extracted_file = None
            st.session_state.bukkatsu_results = {}
            st.experimental_rerun()
    
    # メインコンテンツ
    tab1, tab2, tab3, tab4 = st.tabs(["📄 PDF処理", "🔍 物確実行", "📊 結果確認", "📋 レポート"])
    
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
                                
                                # データ保存
                                extracted_file = analyzer.save_extracted_data(raw_properties, str(DATA_DIR / "extracted"))
                                st.session_state.extracted_file = extracted_file
                                
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
            st.info(f"📊 {len(st.session_state.properties)}件の物件で物確を実行します")
            
            # 検索キーワードプレビュー
            extractor = PropertyExtractor()
            search_combinations = extractor.create_search_combinations(st.session_state.properties)
            
            with st.expander("🔍 検索キーワード確認", expanded=False):
                preview_keywords = []
                for combo in search_combinations[:10]:  # 最初の10件
                    preview_keywords.append({
                        "物件ID": combo["property_id"],
                        "検索キーワード": combo["keywords"],
                        "元住所": combo["original_address"][:40] + "..." if len(combo["original_address"]) > 40 else combo["original_address"]
                    })
                
                if preview_keywords:
                    st.dataframe(preview_keywords, use_container_width=True)
                    if len(search_combinations) > 10:
                        st.info(f"プレビューは最初の10件のみ表示。全{len(search_combinations)}件で検索")
            
            # 物確サイト選択
            st.subheader("🌐 物確サイト選択")
            col1, col2 = st.columns(2)
            
            with col1:
                run_itandi = st.checkbox("ITANDI", value=True)
            with col2:
                run_ierabu = st.checkbox("いえらぶBB", value=True)
            
            if not (run_itandi or run_ierabu):
                st.warning("⚠️ 少なくとも1つのサイトを選択してください")
            else:
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    estimated_time = len(search_combinations) * 3  # 1物件3秒の見積もり
                    st.info(f"⏱️ 推定実行時間: 約{estimated_time // 60}分{estimated_time % 60}秒")
                
                with col2:
                    if st.button("🚀 物確実行", type="primary", use_container_width=True):
                        # プログレスバー
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        try:
                            # 非同期実行
                            status_text.text("🔄 物確処理開始...")
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            
                            results = {}
                            total_sites = (1 if run_itandi else 0) + (1 if run_ierabu else 0)
                            current_site = 0
                            
                            if run_itandi:
                                current_site += 1
                                progress_bar.progress(current_site / total_sites * 0.5)
                                status_text.text("🔍 ITANDI で物確実行中...")
                                
                                try:
                                    itandi_results = loop.run_until_complete(check_properties_itandi(search_combinations))
                                    results['itandi'] = itandi_results
                                    found_count = len([r for r in itandi_results if getattr(r, 'found', False)])
                                    st.success(f"✅ ITANDI: {found_count}/{len(itandi_results)}件発見")
                                except Exception as e:
                                    st.error(f"❌ ITANDI物確エラー: {str(e)}")
                                    results['itandi'] = []
                            
                            if run_ierabu:
                                current_site += 1
                                progress_bar.progress(current_site / total_sites * 0.5 + 0.25)
                                status_text.text("🔍 いえらぶBB で物確実行中...")
                                
                                try:
                                    ierabu_results = loop.run_until_complete(check_properties_ierabu(search_combinations))
                                    results['ierabu'] = ierabu_results
                                    found_count = len([r for r in ierabu_results if getattr(r, 'found', False)])
                                    st.success(f"✅ いえらぶBB: {found_count}/{len(ierabu_results)}件発見")
                                except Exception as e:
                                    st.error(f"❌ いえらぶBB物確エラー: {str(e)}")
                                    results['ierabu'] = []
                            
                            # 結果保存
                            st.session_state.bukkatsu_results = results
                            
                            progress_bar.progress(1.0)
                            status_text.text("✅ 物確処理完了!")
                            
                            # サマリー表示
                            total_found = 0
                            total_checked = 0
                            
                            for site, site_results in results.items():
                                found = len([r for r in site_results if getattr(r, 'found', False)])
                                total_found += found
                                total_checked += len(site_results)
                            
                            if total_checked > 0:
                                success_rate = (total_found / total_checked) * 100
                                st.metric("成功率", f"{success_rate:.1f}%", f"{total_found}/{total_checked}件")
                            
                        except Exception as e:
                            st.error(f"❌ 物確処理エラー: {str(e)}")
                            status_text.text("❌ 処理中にエラーが発生しました")
                        
                        finally:
                            try:
                                loop.close()
                            except:
                                pass
    
    with tab3:
        st.header("📊 物確結果確認")
        
        if not st.session_state.bukkatsu_results:
            st.warning("⚠️ まず物確を実行してください")
        else:
            # サマリーカード表示
            col1, col2, col3, col4 = st.columns(4)
            
            total_properties = len(st.session_state.properties)
            total_found = 0
            total_checked = 0
            
            for results in st.session_state.bukkatsu_results.values():
                found = len([r for r in results if getattr(r, 'found', False)])
                total_found += found
                total_checked += len(results)
            
            with col1:
                st.metric("総物件数", total_properties)
            with col2:
                st.metric("総発見件数", total_found)
            with col3:
                st.metric("総確認件数", total_checked)
            with col4:
                success_rate = (total_found / total_checked * 100) if total_checked > 0 else 0
                st.metric("成功率", f"{success_rate:.1f}%")
            
            # サイト別結果表示
            for site, results in st.session_state.bukkatsu_results.items():
                st.subheader(f"📊 {site.upper()} 結果")
                
                if results:
                    result_data = []
                    for result in results:
                        status_icon = {
                            'vacant': '🟢',
                            'occupied': '🔴', 
                            'unknown': '🟡'
                        }.get(getattr(result, 'availability_status', 'unknown'), '🟡')
                        
                        result_data.append({
                            "物件ID": getattr(result, 'property_id', ''),
                            "発見": "✅" if getattr(result, 'found', False) else "❌",
                            "空室状況": f"{status_icon} {getattr(result, 'availability_status', 'unknown')}",
                            "表示賃料": getattr(result, 'rent_displayed', '') or getattr(result, 'contact_info', ''),
                            "備考": getattr(result, 'notes', '') or getattr(result, 'error_message', '')
                        })
                    
                    st.dataframe(result_data, use_container_width=True)
                else:
                    st.info("結果がありません")
    
    with tab4:
        st.header("📋 レポート生成・ダウンロード")
        
        if not st.session_state.bukkatsu_results:
            st.warning("⚠️ まず物確を実行してください")
        else:
            st.subheader("📄 レポート形式選択")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                report_types = st.multiselect(
                    "生成するレポート形式",
                    ["Excel (詳細)", "HTML (ビジュアル)", "CSV (軽量)", "JSON (API用)"],
                    default=["Excel (詳細)", "HTML (ビジュアル)"]
                )
            
            with col2:
                if st.button("📋 レポート生成", type="primary", use_container_width=True):
                    if not report_types:
                        st.warning("⚠️ 少なくとも1つのレポート形式を選択してください")
                    else:
                        with st.spinner("📋 レポート生成中..."):
                            try:
                                # レポート生成
                                report_generator = ReportGenerator(str(REPORTS_DIR))
                                
                                itandi_results = st.session_state.bukkatsu_results.get('itandi', [])
                                ierabu_results = st.session_state.bukkatsu_results.get('ierabu', [])
                                
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