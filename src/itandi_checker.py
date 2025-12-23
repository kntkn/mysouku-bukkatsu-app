"""
ITANDI物確自動化モジュール
"""
import asyncio
import re
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Browser, Page
from dataclasses import dataclass
from config.credentials import CredentialsManager
from config.settings import PLAYWRIGHT_CONFIG, BUKKATSU_CONFIG

@dataclass
class ITANDISearchResult:
    """ITANDI検索結果"""
    property_id: str
    found: bool
    availability_status: str  # "vacant", "occupied", "unknown"
    listing_url: str
    rent_displayed: str
    notes: str
    error_message: str = ""

class ITANDIChecker:
    """ITANDI物確自動化クラス"""
    
    def __init__(self):
        self.credentials = CredentialsManager().get_credentials("itandi")
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
    
    async def __aenter__(self):
        """非同期コンテキストマネージャー開始"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=PLAYWRIGHT_CONFIG["headless"],
            slow_mo=PLAYWRIGHT_CONFIG["slow_mo"]
        )
        self.page = await self.browser.new_page()
        
        # タイムアウト設定
        self.page.set_default_timeout(PLAYWRIGHT_CONFIG["timeout"])
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """非同期コンテキストマネージャー終了"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def login(self) -> bool:
        """ITANDIにログイン"""
        try:
            print("ITANDIにログイン中...")
            
            # ログインページにアクセス
            await self.page.goto(self.credentials.login_url, wait_until="domcontentloaded")
            
            # ログインフォームの待機
            await self.page.wait_for_selector('input[type="email"], input[name="email"], #email', timeout=10000)
            
            # メールアドレス入力
            email_selectors = ['input[type="email"]', 'input[name="email"]', '#email', '#username']
            email_filled = False
            
            for selector in email_selectors:
                try:
                    await self.page.fill(selector, self.credentials.username)
                    email_filled = True
                    break
                except:
                    continue
            
            if not email_filled:
                raise Exception("メールアドレス入力フィールドが見つかりません")
            
            # パスワード入力
            password_selectors = ['input[type="password"]', 'input[name="password"]', '#password']
            password_filled = False
            
            for selector in password_selectors:
                try:
                    await self.page.fill(selector, self.credentials.password)
                    password_filled = True
                    break
                except:
                    continue
            
            if not password_filled:
                raise Exception("パスワード入力フィールドが見つかりません")
            
            # ログインボタンをクリック
            login_selectors = ['button[type="submit"]', 'input[type="submit"]', 'button:has-text("ログイン")', 'input[value*="ログイン"]']
            
            for selector in login_selectors:
                try:
                    await self.page.click(selector)
                    break
                except:
                    continue
            
            # ログイン完了まで待機
            await self.page.wait_for_load_state("networkidle", timeout=15000)
            
            # ログイン成功の確認（URLの変化やダッシュボードの表示で判定）
            current_url = self.page.url
            if "login" not in current_url.lower() or "dashboard" in current_url.lower():
                print("ITANDIログイン成功")
                return True
            else:
                print("ログインに失敗した可能性があります")
                return False
                
        except Exception as e:
            print(f"ITANDIログインエラー: {e}")
            return False
    
    async def search_property(self, search_keywords: str) -> ITANDISearchResult:
        """物件を検索"""
        result = ITANDISearchResult(
            property_id="",
            found=False,
            availability_status="unknown",
            listing_url="",
            rent_displayed="",
            notes="",
        )
        
        try:
            print(f"ITANDI検索: {search_keywords}")
            
            # 検索ページに移動
            search_selectors = ['input[type="search"]', 'input[name="search"]', '#search', '.search-input']
            search_filled = False
            
            # まず検索ボックスを探す
            for selector in search_selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=5000)
                    await self.page.fill(selector, search_keywords)
                    search_filled = True
                    break
                except:
                    continue
            
            if not search_filled:
                # 検索ページのURLに直接アクセスを試みる
                search_url = "https://itandibb.com/search"
                await self.page.goto(search_url)
                await self.page.wait_for_load_state("domcontentloaded")
                
                # 再度検索ボックスを探す
                for selector in search_selectors:
                    try:
                        await self.page.wait_for_selector(selector, timeout=5000)
                        await self.page.fill(selector, search_keywords)
                        search_filled = True
                        break
                    except:
                        continue
            
            if not search_filled:
                result.error_message = "検索ボックスが見つかりません"
                return result
            
            # 検索実行
            search_button_selectors = ['button[type="submit"]', 'button:has-text("検索")', '.search-button', '#search-btn']
            
            for selector in search_button_selectors:
                try:
                    await self.page.click(selector)
                    break
                except:
                    continue
            else:
                # ボタンがない場合はEnterキーで検索
                await self.page.keyboard.press('Enter')
            
            # 検索結果の読み込み待機
            await self.page.wait_for_load_state("networkidle", timeout=10000)
            
            # 検索結果の解析
            await self._analyze_search_results(result)
            
        except Exception as e:
            result.error_message = f"検索エラー: {str(e)}"
            print(f"ITANDI検索エラー: {e}")
        
        return result
    
    async def _analyze_search_results(self, result: ITANDISearchResult):
        """検索結果を解析"""
        try:
            # 物件リストの要素を探す
            property_selectors = [
                '.property-item', '.listing-item', '.search-result-item',
                '.property-card', '.listing-card', '[class*="property"]',
                '[class*="listing"]', '[class*="result"]'
            ]
            
            property_elements = []
            for selector in property_selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    if elements:
                        property_elements = elements
                        break
                except:
                    continue
            
            if not property_elements:
                # "検索結果なし"の表示をチェック
                no_results_texts = ["検索結果がありません", "物件が見つかりません", "該当する物件", "0件"]
                page_content = await self.page.content()
                
                for text in no_results_texts:
                    if text in page_content:
                        result.found = False
                        result.notes = "検索結果なし"
                        return
                
                result.error_message = "検索結果の解析ができませんでした"
                return
            
            # 最初の物件の詳細を取得
            first_property = property_elements[0]
            
            # 物件URLを取得
            try:
                link_element = await first_property.query_selector('a')
                if link_element:
                    href = await link_element.get_attribute('href')
                    if href:
                        if href.startswith('/'):
                            result.listing_url = f"https://itandibb.com{href}"
                        else:
                            result.listing_url = href
            except:
                pass
            
            # 賃料情報を取得
            try:
                rent_selectors = ['.rent', '.price', '[class*="rent"]', '[class*="price"]']
                for selector in rent_selectors:
                    rent_element = await first_property.query_selector(selector)
                    if rent_element:
                        rent_text = await rent_element.inner_text()
                        if rent_text and any(char.isdigit() for char in rent_text):
                            result.rent_displayed = rent_text.strip()
                            break
            except:
                pass
            
            # 空室状況の判定
            property_text = await first_property.inner_text()
            
            if any(keyword in property_text for keyword in ["空室", "募集中", "入居可"]):
                result.availability_status = "vacant"
            elif any(keyword in property_text for keyword in ["満室", "入居中", "成約"]):
                result.availability_status = "occupied"
            else:
                result.availability_status = "unknown"
            
            result.found = True
            result.notes = f"検索結果: {len(property_elements)}件"
            
        except Exception as e:
            result.error_message = f"結果解析エラー: {str(e)}"
    
    async def check_multiple_properties(self, search_combinations: List[Dict[str, str]]) -> List[ITANDISearchResult]:
        """複数物件の物確を実行"""
        results = []
        
        # ログイン
        if not await self.login():
            # ログインに失敗した場合、全ての結果にエラーを設定
            for combo in search_combinations:
                error_result = ITANDISearchResult(
                    property_id=combo["property_id"],
                    found=False,
                    availability_status="unknown",
                    listing_url="",
                    rent_displayed="",
                    notes="",
                    error_message="ログインに失敗しました"
                )
                results.append(error_result)
            return results
        
        # 各物件の検索
        for i, combo in enumerate(search_combinations):
            print(f"物件 {i+1}/{len(search_combinations)}: {combo['property_id']}")
            
            result = await self.search_property(combo["keywords"])
            result.property_id = combo["property_id"]
            results.append(result)
            
            # リクエスト間隔を空ける
            if i < len(search_combinations) - 1:
                await asyncio.sleep(BUKKATSU_CONFIG["wait_time"])
        
        return results

# 非同期ラッパー関数
async def check_properties_itandi(search_combinations: List[Dict[str, str]]) -> List[ITANDISearchResult]:
    """ITANDI物確の実行（外部から呼び出し用）"""
    async with ITANDIChecker() as checker:
        return await checker.check_multiple_properties(search_combinations)