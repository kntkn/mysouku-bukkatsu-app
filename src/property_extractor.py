"""
物件情報抽出・正規化モジュール
抽出された生データを物確用に最適化
"""
import re
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class PropertyInfo:
    """物件情報データクラス"""
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
    
    def to_search_keywords(self) -> List[str]:
        """物確検索用キーワードリストを生成"""
        keywords = []
        
        # 住所から検索キーワード抽出
        if self.address:
            # 区までの住所を抽出（例：東京都新宿区）
            address_match = re.search(r"([^市区町村]+[市区町村])", self.address)
            if address_match:
                keywords.append(address_match.group(1))
            
            # 町名を抽出（例：歌舞伎町）
            town_match = re.search(r"([^0-9\-]+)[0-9\-]", self.address)
            if town_match:
                keywords.append(town_match.group(1))
        
        # 駅名を抽出
        if self.station_info:
            station_match = re.search(r"([^「」\n\r]+)[」】]", self.station_info)
            if station_match:
                keywords.append(station_match.group(1))
        
        # 賃料を検索用に正規化
        if self.rent:
            rent_num = re.search(r"([0-9,\.]+)", self.rent)
            if rent_num:
                keywords.append(rent_num.group(1))
        
        # 間取りを追加
        if self.layout:
            keywords.append(self.layout)
        
        return keywords

class PropertyExtractor:
    """物件情報を抽出・正規化するクラス"""
    
    def __init__(self):
        self.normalization_rules = self._init_normalization_rules()
    
    def _init_normalization_rules(self) -> Dict[str, Dict]:
        """正規化ルールを初期化"""
        return {
            "address": {
                "remove_patterns": [r"\s+", r"（[^）]*）"],  # 余分な空白、括弧内文字を除去
                "replace_patterns": {
                    "ー": "-",
                    "−": "-",
                    "番地": "",
                    "号室": "",
                }
            },
            "station": {
                "remove_patterns": [r"[「」『』]"],
                "replace_patterns": {
                    "駅前": "駅",
                    "駅徒歩": "駅",
                }
            },
            "rent": {
                "remove_patterns": [r"[,，、]"],
                "standardize": True
            }
        }
    
    def normalize_properties(self, raw_properties: List[Dict[str, str]]) -> List[PropertyInfo]:
        """生の物件データを正規化してPropertyInfoオブジェクトに変換"""
        normalized_properties = []
        
        for i, raw_prop in enumerate(raw_properties):
            try:
                # PropertyInfoオブジェクトを作成
                prop = PropertyInfo(
                    property_id=self._generate_property_id(raw_prop, i),
                    address=self._normalize_address(raw_prop.get("address", "")),
                    rent=self._normalize_rent(raw_prop.get("rent", "")),
                    layout=self._normalize_layout(raw_prop.get("layout", "")),
                    area=self._normalize_area(raw_prop.get("area", "")),
                    station_info=self._normalize_station(raw_prop.get("station", "")),
                    walk_time=raw_prop.get("walk_time", ""),
                    age=raw_prop.get("age", ""),
                    management_fee=raw_prop.get("management_fee", ""),
                    source_file=raw_prop.get("source_file", ""),
                    raw_text=raw_prop.get("raw_text", "")
                )
                
                normalized_properties.append(prop)
                
            except Exception as e:
                print(f"物件 {i} の正規化中にエラー: {e}")
                continue
        
        return normalized_properties
    
    def _generate_property_id(self, raw_prop: Dict[str, str], index: int) -> str:
        """物件IDを生成"""
        # 元の物件番号がある場合はそれを使用
        if raw_prop.get("property_number"):
            return raw_prop["property_number"]
        
        # ない場合は自動生成
        source_prefix = ""
        if raw_prop.get("source_file"):
            source_prefix = raw_prop["source_file"][:3]
        
        return f"{source_prefix}_{index+1:03d}"
    
    def _normalize_address(self, address: str) -> str:
        """住所を正規化"""
        if not address:
            return ""
        
        normalized = address
        
        # 不要パターンの除去
        for pattern in self.normalization_rules["address"]["remove_patterns"]:
            normalized = re.sub(pattern, "", normalized)
        
        # 置換ルールの適用
        for old, new in self.normalization_rules["address"]["replace_patterns"].items():
            normalized = normalized.replace(old, new)
        
        return normalized.strip()
    
    def _normalize_station(self, station_info: str) -> str:
        """駅情報を正規化"""
        if not station_info:
            return ""
        
        normalized = station_info
        
        # 不要パターンの除去
        for pattern in self.normalization_rules["station"]["remove_patterns"]:
            normalized = re.sub(pattern, "", normalized)
        
        # 置換ルールの適用
        for old, new in self.normalization_rules["station"]["replace_patterns"].items():
            normalized = normalized.replace(old, new)
        
        return normalized.strip()
    
    def _normalize_rent(self, rent: str) -> str:
        """賃料を正規化"""
        if not rent:
            return ""
        
        normalized = rent
        
        # カンマの除去
        for pattern in self.normalization_rules["rent"]["remove_patterns"]:
            normalized = re.sub(pattern, "", normalized)
        
        return normalized.strip()
    
    def _normalize_layout(self, layout: str) -> str:
        """間取りを正規化"""
        if not layout:
            return ""
        
        # 標準的な間取り形式に正規化（例：1K、2DK、3LDK）
        normalized = layout.upper().strip()
        
        # 全角数字を半角に変換
        normalized = normalized.translate(str.maketrans("０１２３４５６７８９", "0123456789"))
        
        return normalized
    
    def _normalize_area(self, area: str) -> str:
        """面積を正規化"""
        if not area:
            return ""
        
        # 数値部分を抽出
        area_match = re.search(r"([0-9]+\.?[0-9]*)", area)
        if area_match:
            return f"{area_match.group(1)}㎡"
        
        return area
    
    def create_search_combinations(self, properties: List[PropertyInfo]) -> List[Dict[str, str]]:
        """物確検索用の組み合わせを作成"""
        search_combinations = []
        
        for prop in properties:
            keywords = prop.to_search_keywords()
            
            # 基本的な検索組み合わせ
            combinations = [
                # 住所 + 賃料
                [kw for kw in keywords if any(x in kw for x in ["区", "市", "万円"])],
                # 駅名 + 間取り
                [kw for kw in keywords if any(x in kw for x in ["駅", "K", "DK", "LDK"])],
                # 住所 + 間取り
                [kw for kw in keywords if any(x in kw for x in ["区", "市", "K", "DK", "LDK"])],
            ]
            
            # 空でない組み合わせのみを追加
            for combo in combinations:
                if combo:
                    search_combinations.append({
                        "property_id": prop.property_id,
                        "keywords": " ".join(combo),
                        "original_address": prop.address,
                        "original_rent": prop.rent
                    })
        
        return search_combinations
    
    def filter_valid_properties(self, properties: List[PropertyInfo]) -> List[PropertyInfo]:
        """有効な物件のみをフィルタリング"""
        valid_properties = []
        
        for prop in properties:
            # 最低限の情報があるかチェック
            if (prop.address or prop.station_info) and (prop.rent or prop.layout):
                valid_properties.append(prop)
            else:
                print(f"無効な物件をスキップ: {prop.property_id}")
        
        return valid_properties