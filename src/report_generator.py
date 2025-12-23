"""
物確レポート生成モジュール
"""
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import asdict
import json

class ReportGenerator:
    """物確結果のレポート生成クラス"""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_comprehensive_report(self, 
                                   properties: List,
                                   itandi_results: List = None,
                                   ierabu_results: List = None) -> Dict[str, str]:
        """包括的な物確レポートを生成"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        reports = {}
        
        # 1. サマリーレポート（Excel）
        excel_path = self._generate_excel_report(properties, itandi_results, ierabu_results, timestamp)
        reports["excel"] = str(excel_path)
        
        # 2. 詳細レポート（HTML）
        html_path = self._generate_html_report(properties, itandi_results, ierabu_results, timestamp)
        reports["html"] = str(html_path)
        
        # 3. JSONレポート（API用）
        json_path = self._generate_json_report(properties, itandi_results, ierabu_results, timestamp)
        reports["json"] = str(json_path)
        
        # 4. CSVレポート（軽量版）
        csv_path = self._generate_csv_report(properties, itandi_results, ierabu_results, timestamp)
        reports["csv"] = str(csv_path)
        
        return reports
    
    def _generate_excel_report(self, properties, itandi_results, ierabu_results, timestamp) -> Path:
        """Excel形式の詳細レポートを生成"""
        excel_path = self.output_dir / f"物確レポート_{timestamp}.xlsx"
        
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            
            # シート1: サマリー
            summary_data = self._create_summary_data(properties, itandi_results, ierabu_results)
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='サマリー', index=False)
            
            # シート2: 物件詳細
            if properties:
                properties_data = []
                for prop in properties:
                    prop_dict = asdict(prop) if hasattr(prop, '__dict__') else prop
                    properties_data.append(prop_dict)
                
                properties_df = pd.DataFrame(properties_data)
                properties_df.to_excel(writer, sheet_name='物件詳細', index=False)
            
            # シート3: ITANDI結果
            if itandi_results:
                itandi_data = []
                for result in itandi_results:
                    result_dict = asdict(result) if hasattr(result, '__dict__') else result
                    itandi_data.append(result_dict)
                
                itandi_df = pd.DataFrame(itandi_data)
                itandi_df.to_excel(writer, sheet_name='ITANDI結果', index=False)
            
            # シート4: いえらぶBB結果
            if ierabu_results:
                ierabu_data = []
                for result in ierabu_results:
                    result_dict = asdict(result) if hasattr(result, '__dict__') else result
                    ierabu_data.append(result_dict)
                
                ierabu_df = pd.DataFrame(ierabu_data)
                ierabu_df.to_excel(writer, sheet_name='いえらぶBB結果', index=False)
        
        return excel_path
    
    def _generate_html_report(self, properties, itandi_results, ierabu_results, timestamp) -> Path:
        """HTML形式のビジュアルレポートを生成"""
        html_path = self.output_dir / f"物確レポート_{timestamp}.html"
        
        # サマリー統計を計算
        total_properties = len(properties) if properties else 0
        itandi_found = len([r for r in (itandi_results or []) if getattr(r, 'found', False)])
        ierabu_found = len([r for r in (ierabu_results or []) if getattr(r, 'found', False)])
        
        html_content = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>物確レポート - {timestamp}</title>
    <style>
        body {{ font-family: 'Hiragino Sans', 'Yu Gothic', Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f5f5f5; padding: 20px; margin-bottom: 30px; border-radius: 8px; }}
        .summary {{ display: flex; justify-content: space-around; margin-bottom: 30px; }}
        .summary-card {{ background-color: #fff; border: 1px solid #ddd; padding: 20px; border-radius: 8px; text-align: center; min-width: 120px; }}
        .summary-card h3 {{ margin: 0; color: #333; }}
        .summary-card .number {{ font-size: 2em; font-weight: bold; color: #2196F3; }}
        .section {{ margin-bottom: 30px; }}
        .section h2 {{ color: #333; border-bottom: 2px solid #2196F3; padding-bottom: 10px; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #f5f5f5; font-weight: bold; }}
        .status-vacant {{ background-color: #e8f5e8; color: #2e7d32; }}
        .status-occupied {{ background-color: #ffebee; color: #c62828; }}
        .status-unknown {{ background-color: #fff3e0; color: #ef6c00; }}
        .found {{ color: #2e7d32; font-weight: bold; }}
        .not-found {{ color: #c62828; font-weight: bold; }}
        .footer {{ margin-top: 50px; padding: 20px; background-color: #f5f5f5; border-radius: 8px; text-align: center; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏠 マイソク物確レポート</h1>
        <p>生成日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}</p>
    </div>
    
    <div class="summary">
        <div class="summary-card">
            <h3>総物件数</h3>
            <div class="number">{total_properties}</div>
        </div>
        <div class="summary-card">
            <h3>ITANDI発見</h3>
            <div class="number">{itandi_found}</div>
        </div>
        <div class="summary-card">
            <h3>いえらぶBB発見</h3>
            <div class="number">{ierabu_found}</div>
        </div>
        <div class="summary-card">
            <h3>成功率</h3>
            <div class="number">{((itandi_found + ierabu_found) / (total_properties * 2) * 100) if total_properties > 0 else 0:.1f}%</div>
        </div>
    </div>
"""
        
        # ITANDI結果テーブル
        if itandi_results:
            html_content += self._generate_result_table("ITANDI", itandi_results)
        
        # いえらぶBB結果テーブル
        if ierabu_results:
            html_content += self._generate_result_table("いえらぶBB", ierabu_results)
        
        # 物件詳細テーブル
        if properties:
            html_content += self._generate_property_table(properties)
        
        html_content += """
    <div class="footer">
        <p>このレポートは マイソク物確自動化アプリ によって自動生成されました。</p>
    </div>
</body>
</html>
"""
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return html_path
    
    def _generate_result_table(self, site_name: str, results: List) -> str:
        """結果テーブルのHTMLを生成"""
        html = f"""
    <div class="section">
        <h2>📊 {site_name} 検索結果</h2>
        <table>
            <thead>
                <tr>
                    <th>物件ID</th>
                    <th>発見</th>
                    <th>空室状況</th>
                    <th>表示賃料</th>
                    <th>URL</th>
                    <th>備考</th>
                </tr>
            </thead>
            <tbody>
"""
        
        for result in results:
            found_class = "found" if getattr(result, 'found', False) else "not-found"
            found_text = "✓ 発見" if getattr(result, 'found', False) else "✗ 未発見"
            
            status = getattr(result, 'availability_status', 'unknown')
            status_class = f"status-{status}"
            status_text = {
                'vacant': '🟢 空室',
                'occupied': '🔴 満室',
                'unknown': '🟡 不明'
            }.get(status, '🟡 不明')
            
            listing_url = getattr(result, 'listing_url', '')
            url_link = f'<a href="{listing_url}" target="_blank">リンク</a>' if listing_url else '-'
            
            html += f"""
                <tr>
                    <td>{getattr(result, 'property_id', '')}</td>
                    <td class="{found_class}">{found_text}</td>
                    <td class="{status_class}">{status_text}</td>
                    <td>{getattr(result, 'rent_displayed', '') or getattr(result, 'contact_info', '')}</td>
                    <td>{url_link}</td>
                    <td>{getattr(result, 'notes', '') or getattr(result, 'error_message', '')}</td>
                </tr>
"""
        
        html += """
            </tbody>
        </table>
    </div>
"""
        return html
    
    def _generate_property_table(self, properties: List) -> str:
        """物件詳細テーブルのHTMLを生成"""
        html = """
    <div class="section">
        <h2>🏢 物件詳細</h2>
        <table>
            <thead>
                <tr>
                    <th>物件ID</th>
                    <th>住所</th>
                    <th>賃料</th>
                    <th>間取り</th>
                    <th>面積</th>
                    <th>駅情報</th>
                    <th>徒歩</th>
                    <th>築年数</th>
                </tr>
            </thead>
            <tbody>
"""
        
        for prop in properties:
            prop_dict = asdict(prop) if hasattr(prop, '__dict__') else prop
            
            html += f"""
                <tr>
                    <td>{prop_dict.get('property_id', '')}</td>
                    <td>{prop_dict.get('address', '')}</td>
                    <td>{prop_dict.get('rent', '')}</td>
                    <td>{prop_dict.get('layout', '')}</td>
                    <td>{prop_dict.get('area', '')}</td>
                    <td>{prop_dict.get('station_info', '')}</td>
                    <td>{prop_dict.get('walk_time', '')}分</td>
                    <td>{prop_dict.get('age', '')}</td>
                </tr>
"""
        
        html += """
            </tbody>
        </table>
    </div>
"""
        return html
    
    def _generate_json_report(self, properties, itandi_results, ierabu_results, timestamp) -> Path:
        """JSON形式のレポートを生成（API連携用）"""
        json_path = self.output_dir / f"物確レポート_{timestamp}.json"
        
        report_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_properties": len(properties) if properties else 0,
                "itandi_results_count": len(itandi_results) if itandi_results else 0,
                "ierabu_results_count": len(ierabu_results) if ierabu_results else 0
            },
            "properties": [asdict(prop) if hasattr(prop, '__dict__') else prop for prop in (properties or [])],
            "itandi_results": [asdict(result) if hasattr(result, '__dict__') else result for result in (itandi_results or [])],
            "ierabu_results": [asdict(result) if hasattr(result, '__dict__') else result for result in (ierabu_results or [])]
        }
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        return json_path
    
    def _generate_csv_report(self, properties, itandi_results, ierabu_results, timestamp) -> Path:
        """CSV形式のシンプルレポートを生成"""
        csv_path = self.output_dir / f"物確レポート_{timestamp}.csv"
        
        # 結合データを作成
        combined_data = []
        
        if properties:
            for prop in properties:
                prop_dict = asdict(prop) if hasattr(prop, '__dict__') else prop
                
                # 対応するITANDI結果を検索
                itandi_result = None
                if itandi_results:
                    for result in itandi_results:
                        if getattr(result, 'property_id', '') == prop_dict.get('property_id', ''):
                            itandi_result = result
                            break
                
                # 対応するいえらぶBB結果を検索
                ierabu_result = None
                if ierabu_results:
                    for result in ierabu_results:
                        if getattr(result, 'property_id', '') == prop_dict.get('property_id', ''):
                            ierabu_result = result
                            break
                
                combined_data.append({
                    "物件ID": prop_dict.get('property_id', ''),
                    "住所": prop_dict.get('address', ''),
                    "賃料": prop_dict.get('rent', ''),
                    "間取り": prop_dict.get('layout', ''),
                    "ITANDI発見": "✓" if itandi_result and getattr(itandi_result, 'found', False) else "✗",
                    "ITANDI空室状況": getattr(itandi_result, 'availability_status', '') if itandi_result else '',
                    "いえらぶBB発見": "✓" if ierabu_result and getattr(ierabu_result, 'found', False) else "✗",
                    "いえらぶBB空室状況": getattr(ierabu_result, 'availability_status', '') if ierabu_result else '',
                })
        
        if combined_data:
            df = pd.DataFrame(combined_data)
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        
        return csv_path
    
    def _create_summary_data(self, properties, itandi_results, ierabu_results) -> List[Dict[str, Any]]:
        """サマリーデータを作成"""
        total_properties = len(properties) if properties else 0
        itandi_found = len([r for r in (itandi_results or []) if getattr(r, 'found', False)])
        ierabu_found = len([r for r in (ierabu_results or []) if getattr(r, 'found', False)])
        
        itandi_vacant = len([r for r in (itandi_results or []) if getattr(r, 'availability_status', '') == 'vacant'])
        ierabu_vacant = len([r for r in (ierabu_results or []) if getattr(r, 'availability_status', '') == 'vacant'])
        
        return [
            {"項目": "総物件数", "値": total_properties},
            {"項目": "ITANDI発見数", "値": itandi_found},
            {"項目": "ITANDI空室数", "値": itandi_vacant},
            {"項目": "いえらぶBB発見数", "値": ierabu_found},
            {"項目": "いえらぶBB空室数", "値": ierabu_vacant},
            {"項目": "総発見率", "値": f"{((itandi_found + ierabu_found) / (total_properties * 2) * 100) if total_properties > 0 else 0:.1f}%"},
        ]