"""
Search Module - Google Maps सर्च लॉजिक
Google Maps पर सर्च करना और results scroll करना।
"""

import time
import random
import re


class GoogleMapsSearch:
    """Google Maps पर search करने की class"""
    
    # Fallback selectors (Google अक्सर class names बदलता है)
    RESULT_PANEL_SELECTORS = [
        "div[role='feed']",
        ".m6QErb.DxyBCb.kA9KIf.dS8AEf",
        ".m6QErb",
    ]
    
    CARD_SELECTORS = [
        ".Nv2PK",
        "div[role='article']",
        "a.hfpxzc",
    ]
    
    def __init__(self, page, config=None):
        """
        Search module initialize करता है।
        
        Args:
            page: Playwright page object
            config: Configuration dictionary (optional)
        """
        self.page = page
        self.config = config or {}
    
    def navigate_to_maps(self):
        """Google Maps homepage पर जाता है"""
        try:
            self.page.goto("https://www.google.com/maps", wait_until="networkidle")
            time.sleep(2)
            
            # Consent dialog handle करें (अगर आए)
            self._handle_consent_dialog()
            
            print("[INFO] Navigated to Google Maps")
            return True
            
        except Exception as e:
            print(f"[ERROR] Navigation failed: {e}")
            return False
    
    def _handle_consent_dialog(self):
        """Google consent dialog को dismiss करता है"""
        try:
            # "Accept all" या "Reject all" button ढूंढें
            accept_buttons = [
                "button:has-text('Accept all')",
                "button:has-text('Reject all')",
                "text='Accept all'",
                "[aria-label='Accept all']",
            ]
            
            for selector in accept_buttons:
                try:
                    btn = self.page.locator(selector).first
                    if btn.is_visible(timeout=2000):
                        btn.click()
                        time.sleep(1)
                        print("[INFO] Consent dialog handled")
                        return
                except:
                    continue
                    
        except Exception:
            pass  # No consent dialog, continue
    
    
    def get_total_count(self):
        """
        Total result count dhoondne ki koshish karta hai.
        """
        try:
            # 1. Look for explicit text patterns in the entire side panel or body
            # We use evaluate to get text content efficiently
            text_content = self.page.evaluate("""() => {
                const panel = document.querySelector("div[role='feed']") || document.body;
                return panel.innerText;
            }""")
            
            # Patterns to look for
            # 1. "1-20 of 120 results"
            # 2. "Found 120 results"
            # 3. "120 results" (risky, matches other numbers)
            
            # High confidence patterns
            patterns = [
                r"(\d+)\s+results",
                r"Results\s+\d+\s*-\s*\d+\s+of\s+(\d+)",
                r"Found\s+(\d+)\s+results"
            ]
            
            for pattern in patterns:
                matches = re.search(pattern, text_content, re.IGNORECASE)
                if matches:
                    # Extracts the last group which should be the total
                    count = int(matches.groups()[-1])
                    print(f"[INFO] Found total count in text: {count}")
                    return count
            
            return 0
            
        except Exception as e:
            print(f"[WARN] Error finding total count: {e}")
            return 0

            
    def load_all_results(self, max_scrolls=100):
        """
        Saare results load karne ke liye end tak scroll karta hai.
        Extract karne se pehle ise call karein taki total count pata chale.
        
        Args:
            max_scrolls: Safety limit
            
        Returns:
            int: Total cards loaded
        """
        print("[INFO] Scrolling to load ALL results...")
        return self.scroll_until_end(max_scrolls=max_scrolls, stop_after_no_change=5)

    def search(self, query):
        """
        Google Maps पर search करता है।
        
        Args:
            query: Search query (e.g., "gym in lucknow")
            
        Returns:
            bool: Success or failure
        """
        try:
            # Search box ढूंढें
            search_box = self.page.locator("#searchboxinput")
            
            # Clear और type करें
            search_box.fill("")
            time.sleep(0.5)
            
            # Human-like typing
            for char in query:
                search_box.type(char, delay=random.randint(50, 150))
            
            time.sleep(1)
            
            # Search button click करें
            search_button = self.page.locator("#searchbox-searchbutton")
            search_button.click()
            
            # Results load होने का wait करें
            time.sleep(3)
            self.page.wait_for_load_state("networkidle", timeout=30000)
            
            print(f"[INFO] Search completed for: {query}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Search failed: {e}")
            return False
    
    def search_direct_url(self, query):
        """
        Direct URL से Google Maps search करता है।
        
        Args:
            query: Search query
            
        Returns:
            bool: Success or failure
        """
        try:
            # URL encode
            encoded_query = query.replace(" ", "+")
            url = f"https://www.google.com/maps/search/{encoded_query}"
            
            print(f"[INFO] Navigating to: {url}")
            
            # Use longer timeout and domcontentloaded for faster response
            self.page.goto(url, wait_until="domcontentloaded", timeout=60000)
            print("[INFO] Page loaded (domcontentloaded)")
            
            # Wait for page to stabilize
            time.sleep(4)
            
            # Consent handle करें
            self._handle_consent_dialog()
            
            # Try to wait for results panel with multiple fallbacks
            waited = False
            for selector in self.RESULT_PANEL_SELECTORS:
                try:
                    self.page.wait_for_selector(selector, timeout=15000)
                    print(f"[INFO] Found result panel with selector: {selector}")
                    waited = True
                    break
                except:
                    continue
            
            if not waited:
                # Just wait a bit more without specific selector
                time.sleep(3)
                print("[INFO] No specific panel found, continuing anyway")
            
            print(f"[INFO] Direct search completed for: {query}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Direct search failed: {e}")
            # Try alternative method
            print("[INFO] Trying alternative navigation method...")
            return self._search_alternative(query)
    
    def _search_alternative(self, query):
        """
        Alternative search method - goes to maps.google.com first, then searches.
        
        Args:
            query: Search query
            
        Returns:
            bool: Success or failure
        """
        try:
            # First navigate to Google Maps home
            self.page.goto("https://maps.google.com", timeout=30000)
            time.sleep(3)
            
            # Handle consent
            self._handle_consent_dialog()
            time.sleep(2)
            
            # Use the search method
            return self.search(query)
            
        except Exception as e:
            print(f"[ERROR] Alternative search also failed: {e}")
            return False
    
    def _get_result_panel(self):
        """Result panel element ढूंढता है"""
        for selector in self.RESULT_PANEL_SELECTORS:
            try:
                panel = self.page.locator(selector).first
                if panel.is_visible(timeout=2000):
                    return panel
            except:
                continue
        return None
    
    def get_cards(self):
        """
        सभी business cards ढूंढता है।
        
        Returns:
            list: Card elements की list
        """
        cards = []
        for selector in self.CARD_SELECTORS:
            try:
                found = self.page.locator(selector).all()
                if found:
                    cards = found
                    break
            except:
                continue
        
        print(f"[INFO] Found {len(cards)} cards")
        return cards
    
    def scroll_results(self, times=5):
        """
        Result panel को कई बार scroll करता है।
        
        Args:
            times: कितनी बार scroll करना है
            
        Returns:
            int: Total cards found
        """
        panel = self._get_result_panel()
        if not panel:
            print("[WARN] Result panel not found")
            return 0
        
        for i in range(times):
            try:
                # Panel के अंदर scroll करें
                self.page.evaluate("""
                    (selector) => {
                        const panel = document.querySelector(selector);
                        if (panel) {
                            panel.scrollBy(0, 1000);
                        }
                    }
                """, self.RESULT_PANEL_SELECTORS[0])
                
                # Human-like delay
                delay = random.uniform(1.5, 3.0)
                time.sleep(delay)
                
                print(f"[INFO] Scroll {i+1}/{times} completed")
                
            except Exception as e:
                print(f"[WARN] Scroll error: {e}")
        
        return len(self.get_cards())
    
    def scroll_until_end(self, max_scrolls=50, stop_after_no_change=3):
        """
        जब तक नए results आ रहे हैं तब तक scroll करता है।
        
        Args:
            max_scrolls: Maximum scrolls
            stop_after_no_change: कितने scroll के बाद रुकना है (अगर count न बदले)
            
        Returns:
            int: Total cards found
        """
        prev_count = 0
        same_count = 0
        scroll_num = 0
        
        while scroll_num < max_scrolls and same_count < stop_after_no_change:
            # Current cards count
            cards = self.get_cards()
            curr_count = len(cards)
            
            if curr_count == prev_count:
                same_count += 1
                print(f"[INFO] No new cards (same count: {same_count}/{stop_after_no_change})")
            else:
                same_count = 0
            
            prev_count = curr_count
            
            # Scroll करें
            try:
                self.page.evaluate("""
                    () => {
                        const selectors = ["div[role='feed']", ".m6QErb"];
                        for (const sel of selectors) {
                            const panel = document.querySelector(sel);
                            if (panel) {
                                panel.scrollBy(0, 800);
                                break;
                            }
                        }
                    }
                """)
            except Exception as e:
                print(f"[WARN] Scroll error: {e}")
            
            # Check for "end of list" indicator
            try:
                end_indicator = self.page.locator("span:has-text('end of list')").first
                if end_indicator.is_visible(timeout=500):
                    print("[INFO] Reached end of list")
                    break
            except:
                pass
            
            # Human-like delay
            delay = random.uniform(1.5, 3.0)
            time.sleep(delay)
            
            scroll_num += 1
            print(f"[INFO] Scroll {scroll_num}: {curr_count} cards found")
        
        final_cards = self.get_cards()
        print(f"[INFO] Scroll complete. Total cards: {len(final_cards)}")
        return len(final_cards)
