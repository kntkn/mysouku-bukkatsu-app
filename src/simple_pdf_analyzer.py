"""
軽量PDF解析クラス - マイソクから物件情報を抽出
"""
import re
import io
try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

class SimplePDFAnalyzer:
    """軽量PDFアナライザー"""
    
    def extract_text_from_pdf(self, pdf_file):
        """PDFからテキストを抽出"""
        text = ""
        
        try:
            # pdfplumberを優先使用
            if PDFPLUMBER_AVAILABLE:
                with pdfplumber.open(pdf_file) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            
            # フォールバック: PyPDF2
            elif PYPDF2_AVAILABLE:
                pdf_file.seek(0)  # ファイルポインターをリセット
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            
            else:
                raise Exception("PDF処理ライブラリが利用できません")
                
        except Exception as e:
            raise Exception(f"PDF読み取りエラー: {str(e)}")
        
        return text
    
    def extract_property_info(self, text):
        """テキストから物件情報を抽出"""
        properties = []
        
        # マイソクの基本パターンを定義
        patterns = {
            'rent': [
                r'賃料[\s:：]*([0-9,]+(?:\.[0-9]+)?(?:万円|円))',
                r'家賃[\s:：]*([0-9,]+(?:\.[0-9]+)?(?:万円|円))',
                r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?万円)',
                r'(\d+(?:,\d{3})*円)'
            ],
            'address': [
                r'所在地[\s:：]*([^\n]+(?:市|区|町|村)[^\n]*)',
                r'住所[\s:：]*([^\n]+(?:市|区|町|村)[^\n]*)',
                r'((?:東京都|神奈川県|千葉県|埼玉県|大阪府|京都府|兵庫県|愛知県)[^\n]+)',
                r'([^\n]*(?:市|区|町|村)[^\n]*丁目[^\n]*)'
            ],
            'layout': [
                r'間取り[\s:：]*([0-9]?[RLDK]+)',
                r'タイプ[\s:：]*([0-9]?[RLDK]+)',
                r'([0-9]?[RLDK]+)',
                r'(\d[SLDK]+\d*)',
                r'(ワンルーム|1R|1K|1DK|1LDK|2K|2DK|2LDK|3K|3DK|3LDK|4K|4DK|4LDK)'
            ],
            'station': [
                r'交通[\s:：]*([^\n]*駅[^\n]*)',
                r'最寄り?駅?[\s:：]*([^\n]*駅[^\n]*)',
                r'アクセス[\s:：]*([^\n]*駅[^\n]*)',
                r'([^\n]*線[^\n]*駅[^\n]*分[^\n]*)',
                r'([^\n]*駅[^\n]*徒歩[^\n]*分[^\n]*)'
            ],
            'area': [
                r'専有面積[\s:：]*([0-9]+(?:\.[0-9]+)?(?:㎡|m2|平米))',
                r'面積[\s:：]*([0-9]+(?:\.[0-9]+)?(?:㎡|m2|平米))',
                r'([0-9]+(?:\.[0-9]+)?(?:㎡|m2))'
            ],
            'age': [
                r'築年数[\s:：]*([^\n]+)',
                r'築([0-9]+年)',
                r'(昭和|平成|令和)([0-9]+)年',
                r'築(\d+)年'
            ]
        }
        
        # 単一物件として抽出（複数物件対応は後で追加可能）
        property_info = {
            'property_id': 'MYSOUKU_001',
            'source_file': 'uploaded_pdf'
        }
        
        # 各パターンでマッチングを試行
        for field, field_patterns in patterns.items():
            for pattern in field_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    if field == 'address':
                        # 住所の後処理
                        addr = match.group(1).strip()
                        # 改行や余分な文字を除去
                        addr = re.sub(r'\s+', ' ', addr)
                        addr = re.sub(r'[（）()「」\[\]].*', '', addr)  # 括弧以降を除去
                        property_info[field] = addr[:100]  # 長すぎる場合は切り詰め
                    elif field == 'station':
                        # 駅情報の後処理
                        station = match.group(1).strip()
                        station = re.sub(r'\s+', ' ', station)
                        property_info[field] = station[:50]
                    else:
                        property_info[field] = match.group(1).strip()
                    break  # 最初にマッチしたパターンで確定
        
        # 必須フィールドの補完
        if 'rent' not in property_info:
            property_info['rent'] = '要相談'
        if 'address' not in property_info:
            property_info['address'] = '住所不明'
        if 'layout' not in property_info:
            property_info['layout'] = '間取り不明'
        if 'station' not in property_info:
            property_info['station'] = '駅情報不明'
        if 'area' not in property_info:
            property_info['area'] = ''
        if 'age' not in property_info:
            property_info['age'] = ''
        
        properties.append(property_info)
        return properties
    
    def analyze_pdf(self, pdf_file):
        """PDFファイルを解析して物件情報を返す"""
        try:
            # PDFからテキスト抽出
            text = self.extract_text_from_pdf(pdf_file)
            
            if not text or text.strip() == "":
                raise Exception("PDFからテキストを抽出できませんでした")
            
            # 物件情報抽出
            properties = self.extract_property_info(text)
            
            if not properties:
                raise Exception("物件情報を抽出できませんでした")
            
            return {
                'success': True,
                'properties': properties,
                'extracted_text': text[:500] + "..." if len(text) > 500 else text  # デバッグ用
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'properties': []
            }

class PropertyData:
    """物件データクラス"""
    def __init__(self, data):
        self.property_id = data.get('property_id', 'UNKNOWN')
        self.address = data.get('address', '')
        self.rent = data.get('rent', '')
        self.layout = data.get('layout', '')
        self.station_info = data.get('station', '')
        self.area = data.get('area', '')
        self.age = data.get('age', '')
        self.source_file = data.get('source_file', '')