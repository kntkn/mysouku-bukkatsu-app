"""
ログイン情報管理モジュール
"""
import os
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class SiteCredentials:
    """物確サイトのログイン情報"""
    site_name: str
    login_url: str
    username: str
    password: str
    search_url: str = ""

class CredentialsManager:
    """ログイン情報を管理するクラス"""
    
    def __init__(self):
        self.credentials = self._load_credentials()
    
    def _load_credentials(self) -> Dict[str, SiteCredentials]:
        """ログイン情報を読み込み"""
        return {
            "itandi": SiteCredentials(
                site_name="ITANDI",
                login_url="https://itandi-accounts.com/login?client_id=itandi_bb&redirect_uri=https%3A%2F%2Fitandibb.com%2Fitandi_accounts_callback&response_type=code&state=d154b03411a94f026786ebb7ab9277ff252cbe88572cbb02261df041314b89d0",
                username="info@fun-t.jp",
                password="funt0406",
                search_url="https://itandibb.com/"
            ),
            "ierabu": SiteCredentials(
                site_name="いえらぶBB",
                login_url="https://bb.ielove.jp/ielovebb/login/index",
                username="goto@fun-t.jp", 
                password="funt040600",
                search_url="https://bb.ielove.jp/"
            )
        }
    
    def get_credentials(self, site_name: str) -> SiteCredentials:
        """指定サイトのログイン情報を取得"""
        if site_name not in self.credentials:
            raise ValueError(f"サイト '{site_name}' のログイン情報が見つかりません")
        return self.credentials[site_name]
    
    def get_all_sites(self) -> List[str]:
        """利用可能なサイト名のリストを取得"""
        return list(self.credentials.keys())