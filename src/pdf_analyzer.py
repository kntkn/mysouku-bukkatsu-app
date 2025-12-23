"""
PDF解析モジュール
マイソクPDFからテキストを抽出し、物件情報を構造化
"""
import io
import re
from pathlib import Path
from typing import List, Dict, Optional
import pdfplumber
import PyPDF2
import pandas as pd

class PDFAnalyzer:
    """PDFファイルを解析し、物件情報を抽出するクラス"""
    
    def __init__(self):
        self.property_patterns = self._init_patterns()
    
    def _init_patterns(self) -> Dict[str, str]:
        """物件情報抽出用の正規表現パターンを定義"""
        return {
            # 物件番号（例：P-001、物件№123、No.456）
            "property_number": r"(?:物件[№No\.]*|P-|№|No\.)\s*([A-Za-z0-9\-]+)",
            
            # 賃料（例：12.5万円、125,000円）
            "rent": r"(?:賃料|家賃)[:：]\s*([0-9,\.]+)\s*(?:万円|円)",
            
            # 住所（例：東京都新宿区...）
            "address": r"(?:所在地|住所)[:：]\s*([^\n\r]+)",
            
            # 駅（例：JR山手線「新宿」駅）
            "station": r"([^「」\n\r]*[線])?[「】]([^「」\n\r]+)[」】]\s*(?:駅|駅前)",
            
            # 徒歩分数（例：徒歩5分、徒歩10分）
            "walk_time": r"徒歩\s*([0-9]+)\s*分",
            
            # 間取り（例：1K、2DK、3LDK）
            "layout": r"([0-9]?[SLDK]+)",
            
            # 面積（例：25.5㎡、30.0m²）
            "area": r"([0-9]+\.?[0-9]*)\s*(?:㎡|m²|平米)",
            
            # 築年数（例：築15年、平成20年築）
            "age": r"(?:築\s*([0-9]+)\s*年|([平昭令和]*[0-9]+)\s*年\s*築)",
            
            # 管理費（例：管理費5,000円）
            "management_fee": r"(?:管理費|共益費)[:：]\s*([0-9,]+)\s*円",
        }
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """PDFファイルからテキストを抽出"""
        text = ""
        
        try:
            # pdfplumberを使用してテキスト抽出
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        
        except Exception as e:
            print(f"pdfplumberでの抽出に失敗: {e}")
            
            # PyPDF2をフォールバックとして使用
            try:
                pdf_file.seek(0)  # ファイルポインタをリセット
                reader = PyPDF2.PdfReader(pdf_file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            except Exception as e2:
                print(f"PyPDF2での抽出にも失敗: {e2}")
                return ""
        
        return text
    
    def extract_property_info(self, text: str) -> List[Dict[str, str]]:
        """テキストから物件情報を抽出"""
        properties = []
        
        # テキストを物件ごとに分割（空行や特定パターンで区切り）
        property_blocks = self._split_into_property_blocks(text)
        
        for i, block in enumerate(property_blocks):
            if not block.strip():
                continue
                
            property_info = self._extract_single_property(block, i + 1)
            if property_info:
                properties.append(property_info)
        
        return properties
    
    def _split_into_property_blocks(self, text: str) -> List[str]:
        """テキストを物件ブロックに分割"""
        # 物件番号パターンで分割
        property_pattern = r"(?=(?:物件[№No\.]*|P-|№|No\.)\s*[A-Za-z0-9\-]+)"
        blocks = re.split(property_pattern, text)
        
        # 空のブロックを除去
        blocks = [block.strip() for block in blocks if block.strip()]
        
        # 分割できなかった場合、全体を1つの物件として扱う
        if len(blocks) <= 1:
            blocks = [text]
        
        return blocks
    
    def _extract_single_property(self, text: str, property_index: int) -> Optional[Dict[str, str]]:
        """単一の物件ブロックから情報を抽出"""
        property_info = {
            "property_index": str(property_index),
            "raw_text": text[:500]  # 先頭500文字を保存
        }
        
        extracted_count = 0
        
        for field, pattern in self.property_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if field == "rent":
                    # 賃料の数値を正規化
                    rent_str = match.group(1).replace(",", "")
                    if "万" in match.group(0):
                        property_info[field] = f"{float(rent_str)}万円"
                    else:
                        property_info[field] = f"{rent_str}円"
                elif field == "age":
                    # 築年数の処理
                    if match.group(1):  # 築XX年形式
                        property_info[field] = f"築{match.group(1)}年"
                    else:  # 平成XX年築形式
                        property_info[field] = f"{match.group(2)}年築"
                else:
                    property_info[field] = match.group(1).strip()
                
                extracted_count += 1
            else:
                property_info[field] = ""
        
        # 最小限の情報が抽出できた場合のみ有効とする
        if extracted_count >= 2:  # 少なくとも2つの情報が抽出できた場合
            return property_info
        
        return None
    
    def save_extracted_data(self, properties: List[Dict[str, str]], output_path: str) -> str:
        """抽出データをCSVファイルに保存"""
        if not properties:
            return ""
        
        df = pd.DataFrame(properties)
        
        # 列順序を整理
        column_order = [
            "property_index", "property_number", "address", "rent", 
            "layout", "area", "station", "walk_time", "age", 
            "management_fee", "raw_text"
        ]
        
        # 存在する列のみ選択
        existing_columns = [col for col in column_order if col in df.columns]
        df = df[existing_columns]
        
        # CSVファイルに保存
        output_file = Path(output_path) / f"extracted_properties_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        return str(output_file)
    
    def analyze_multiple_pdfs(self, pdf_files: List) -> List[Dict[str, str]]:
        """複数のPDFファイルを解析"""
        all_properties = []
        
        for i, pdf_file in enumerate(pdf_files):
            print(f"PDF {i+1}/{len(pdf_files)} を処理中...")
            
            # ファイル名を記録
            file_name = getattr(pdf_file, 'name', f'file_{i+1}')
            
            # テキスト抽出
            text = self.extract_text_from_pdf(pdf_file)
            if not text.strip():
                print(f"  警告: {file_name} からテキストを抽出できませんでした")
                continue
            
            # 物件情報抽出
            properties = self.extract_property_info(text)
            
            # ファイル名を各物件に追加
            for prop in properties:
                prop["source_file"] = file_name
            
            all_properties.extend(properties)
            print(f"  {len(properties)}件の物件情報を抽出")
        
        return all_properties