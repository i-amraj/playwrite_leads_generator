"""
Extractor Module - डेटा पार्सिंग और Extraction
Google Maps से business details निकालता है।
"""

import re
import time
import random
import json
import os


class DataExtractor:
    """Google Maps से data extract करने की class"""
    
    def __init__(self, page, selectors_path=None, country="India"):
        """
        Extractor initialize करता है।
        
        Args:
            page: Playwright page object
            selectors_path: selectors.json का path (optional)
            country: Search country for phone normalization checking
        """
        self.page = page
        self.selectors = self._load_selectors(selectors_path)
        self.country = country or "India"

    def clean_phone_number(self, phone_text):
        """
        Phone number ko clean aur normalize karta hai.
        Goal: Strictly "+<CountryCode><Number>" (No spaces, no dashes)
        Example: +9779846891579
        """
        if not phone_text:
            return ""
            
        # 1. Remove invisible chars
        clean = re.sub(r'[\u202a\u202c\u200e\u200f]', '', phone_text)
        
        # 2. Country mappings
        codes = {
            "india": "+91",
            "nepal": "+977"
        }
        country_key = self.country.lower()
        default_code = codes.get(country_key, "+91")
        
        # 3. Extract all digits
        digits_only = re.sub(r'\D', '', clean)
        
        # 4. Check for existing country code in digits
        raw_code = default_code.replace("+", "")
        
        # Determine strict final number
        final_number = ""
        
        if digits_only.startswith(raw_code):
            # Already has code embedded
            final_number = "+" + digits_only
        elif digits_only.startswith("0") and len(digits_only) > 5:
             # Starts with 0 (e.g. 098...) -> Remove 0 and add code
             final_number = default_code + digits_only[1:]
        else:
             # Assume pure number -> Add code
             final_number = default_code + digits_only
             
        # Double check for double plus or other issues (though logic above prevents it)
        # Just to be safe if input was weird
        return final_number

    
    def _load_selectors(self, selectors_path):
        """Selectors config load करता है"""
        default_selectors = {
            "result_item": ".Nv2PK",
            "title": ".qBF1Pd",
            "rating": ".MW4etd",
            "review_count": ".UY7F9",
            "address": ".W4Efsd",
            "phone": "",
            "website": ""
        }
        
        if selectors_path is None:
            selectors_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "config", "selectors.json"
            )
        
        try:
            if os.path.exists(selectors_path):
                with open(selectors_path, 'r') as f:
                    loaded = json.load(f)
                    default_selectors.update(loaded)
        except Exception as e:
            print(f"[WARN] Selectors load error: {e}")
        
        return default_selectors
    
    def extract_basic_info_from_cards(self, cards, limit=None):
        """
        Cards से basic info extract करता है (बिना click किए)।
        
        Args:
            cards: Card elements की list
            limit: Maximum cards to process
            
        Returns:
            list: Basic business info की list
        """
        businesses = []
        cards_to_process = cards[:limit] if limit else cards
        
        for idx, card in enumerate(cards_to_process):
            try:
                business = self._extract_from_card(card, idx)
                if business and business.get("name"):
                    businesses.append(business)
                    print(f"[INFO] Extracted basic: {business.get('name', 'Unknown')[:30]}...")
            except Exception as e:
                print(f"[WARN] Card {idx} extraction error: {e}")
                continue
        
        return businesses
    
    def _extract_from_card(self, card, index):
        """
        Single card से basic data extract करता है।
        
        Args:
            card: Card element
            index: Card index
            
        Returns:
            dict: Business basic info
        """
        business = {
            "index": index,
            "name": "",
            "rating": "",
            "review_count": "",
            "category": "",
            "address": "",
            "phone": "",
            "website": "",
            "place_id": "",
        }
        
        try:
            # Name extract करें
            try:
                name_el = card.locator(".qBF1Pd, .fontHeadlineSmall").first
                if name_el.is_visible(timeout=500):
                    business["name"] = name_el.inner_text().strip()
            except:
                # Alternative: aria-label से
                try:
                    aria = card.get_attribute("aria-label")
                    if aria:
                        business["name"] = aria.strip()
                except:
                    pass
            
            # Rating extract करें
            try:
                rating_el = card.locator(".MW4etd").first
                if rating_el.is_visible(timeout=500):
                    business["rating"] = rating_el.inner_text().strip()
            except:
                pass
            
            # Review count extract करें
            try:
                review_el = card.locator(".UY7F9").first
                if review_el.is_visible(timeout=500):
                    text = review_el.inner_text()
                    # Extract number from "(123)"
                    match = re.search(r'\(?([\d,]+)\)?', text)
                    if match:
                        business["review_count"] = match.group(1).replace(",", "")
            except:
                pass
            
            # Additional info (address, category) - ye text elements se milega
            try:
                info_els = card.locator(".W4Efsd").all()
                for el in info_els:
                    text = el.inner_text().strip()
                    if text:
                        # Category usually comes first, then address
                        if not business["category"] and not any(c.isdigit() for c in text[:5]):
                            business["category"] = text.split("·")[0].strip()
                        elif "·" in text:
                            parts = text.split("·")
                            for part in parts:
                                part = part.strip()
                                if any(c.isdigit() for c in part):
                                    business["address"] = part
            except:
                pass
                
        except Exception as e:
            print(f"[WARN] Card extraction error: {e}")
        
        return business
    
    def extract_details_from_panel(self, card, business):
        """
        Card पर click करके detail panel से पूरी info extract करता है।
        
        Args:
            card: Card element जिस पर click करना है
            business: Existing business dict जिसे update करना है
            
        Returns:
            dict: Complete business info
        """
        try:
            # Card पर click करें
            card.click()
            
            # Simple wait - networkidle causes timeouts
            time.sleep(3)
            
            # Wait for URL to change (indicates detail panel loaded)
            try:
                self.page.wait_for_url("**/place/**", timeout=5000)
            except:
                # URL might not change for some cards, that's okay
                time.sleep(2)
            
            # Place ID URL से extract करें
            try:
                url = self.page.url
                # Pattern: !1s0x... या place_id parameter
                match = re.search(r'!1s(0x[a-fA-F0-9]+:[a-fA-F0-9]+)', url)
                if match:
                    business["place_id"] = match.group(1)
                else:
                    # Alternative pattern
                    match2 = re.search(r'/place/[^/]+/@[^/]+/data=!3m1!4b1!4m[^!]+!3m[^!]+!1s([^!]+)', url)
                    if match2:
                        business["place_id"] = match2.group(1)
            except:
                pass
            
            # Phone number extract करें
            try:
                phone_buttons = [
                    "button[data-item-id^='phone']",
                    "[data-tooltip='Copy phone number']",
                    "a[href^='tel:']",
                ]
                
                for selector in phone_buttons:
                    try:
                        phone_el = self.page.locator(selector).first
                        if phone_el.is_visible(timeout=1000):
                            # href से phone number
                            href = phone_el.get_attribute("href")
                            if href and href.startswith("tel:"):
                                raw_phone = href.replace("tel:", "").strip()
                                business["phone"] = self.clean_phone_number(raw_phone)
                                break
                            # text से
                            text = phone_el.inner_text()
                            if text:
                                # Remove newlines and clean
                                raw_phone = text.replace("\n", "").strip()
                                business["phone"] = self.clean_phone_number(raw_phone)
                                break
                    except:
                        continue
                
                # Alternative: aria-label से ढूंढें
                if not business["phone"]:
                    try:
                        phone_region = self.page.locator("[aria-label*='Phone']").first
                        if phone_region.is_visible(timeout=500):
                            text = phone_region.inner_text()
                            # Phone number pattern
                            match = re.search(r'[\+\d][\d\s\-]+\d', text)
                            if match:
                                business["phone"] = self.clean_phone_number(match.group().strip())
                    except:
                        pass
                        
            except Exception as e:
                print(f"[WARN] Phone extraction error: {e}")
            
            # Website extract करें
            try:
                website_buttons = [
                    "a[data-item-id='authority']",
                    "[data-tooltip='Open website']",
                    "a[href^='http']:not([href*='google'])",
                ]
                
                for selector in website_buttons:
                    try:
                        web_el = self.page.locator(selector).first
                        if web_el.is_visible(timeout=1000):
                            href = web_el.get_attribute("href")
                            if href and "google" not in href:
                                business["website"] = href
                                break
                    except:
                        continue
                        
            except Exception as e:
                print(f"[WARN] Website extraction error: {e}")
            
            # Full Address extract करें
            try:
                address_buttons = [
                    "button[data-item-id='address']",
                    "[data-tooltip='Copy address']",
                ]
                
                for selector in address_buttons:
                    try:
                        addr_el = self.page.locator(selector).first
                        if addr_el.is_visible(timeout=1000):
                            aria = addr_el.get_attribute("aria-label")
                            if aria:
                                # "Address: 123 Main St" -> "123 Main St"
                                address = aria.replace("Address:", "").strip()
                                if address:
                                    business["address"] = address
                                    break
                    except:
                        continue
                        
            except Exception as e:
                print(f"[WARN] Address extraction error: {e}")
            
            print(f"[INFO] Details extracted for: {business.get('name', 'Unknown')[:30]}")
            
        except Exception as e:
            print(f"[WARN] Detail extraction failed: {e}")
        
        return business
    
    def extract_all_with_details(self, cards, limit=None):
        """
        सभी cards से complete details extract करता है।
        
        Args:
            cards: Card elements की list
            limit: Maximum cards to process
            
        Returns:
            list: Complete business data की list
        """
        businesses = []
        cards_to_process = cards[:limit] if limit else cards
        total = len(cards_to_process)
        
        for idx, card in enumerate(cards_to_process):
            try:
                print(f"\n[INFO] Processing {idx + 1}/{total}...")
                
                # Basic info
                business = self._extract_from_card(card, idx)
                
                if business and business.get("name"):
                    # Click करके details लें
                    business = self.extract_details_from_panel(card, business)
                    businesses.append(business)
                    
                    # Human-like delay
                    delay = random.uniform(1.5, 3.0)
                    time.sleep(delay)
                    
            except Exception as e:
                print(f"[ERROR] Processing card {idx}: {e}")
                continue
        
        print(f"\n[INFO] Total businesses extracted: {len(businesses)}")
        return businesses
