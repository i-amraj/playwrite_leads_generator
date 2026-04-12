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
        self.page = page
        self.selectors = self._load_selectors(selectors_path)
        self.country = country or "India"

    def clean_phone_number(self, phone_text):
        if not phone_text:
            return ""
        clean = re.sub(r'[\u202a\u202c\u200e\u200f]', '', phone_text)
        codes = {"india": "+91", "nepal": "+977"}
        country_key = self.country.lower()
        default_code = codes.get(country_key, "+91")
        digits_only = re.sub(r'\D', '', clean)
        raw_code = default_code.replace("+", "")
        if digits_only.startswith(raw_code):
            return "+" + digits_only
        elif digits_only.startswith("0") and len(digits_only) > 5:
             return default_code + digits_only[1:]
        else:
             return default_code + digits_only
    
    def _load_selectors(self, selectors_path):
        default_selectors = {
            "result_item": ".Nv2PK", "title": ".qBF1Pd", "rating": ".MW4etd",
            "review_count": ".UY7F9", "address": ".W4Efsd", "phone": "", "website": ""
        }
        if selectors_path is None:
            selectors_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "selectors.json")
        try:
            if os.path.exists(selectors_path):
                with open(selectors_path, 'r') as f:
                    loaded = json.load(f)
                    default_selectors.update(loaded)
        except Exception as e:
            print(f"[WARN] Selectors load error: {e}")
        return default_selectors
    
    def extract_basic_info_from_cards(self, cards, limit=None):
        businesses = []
        cards_to_process = cards[:limit] if limit else cards
        for idx, card in enumerate(cards_to_process):
            try:
                business = self._extract_from_card(card, idx)
                if business and business.get("name"):
                    businesses.append(business)
            except Exception as e:
                print(f"[WARN] Card {idx} extraction error: {e}")
        return businesses
    
    def _extract_from_card(self, card, index):
        business = {
            "index": index, "name": "", "rating": "", "review_count": "",
            "category": "", "address": "", "phone": "", "website": "", "place_id": ""
        }
        try:
            name_el = card.locator(".qBF1Pd, .fontHeadlineSmall").first
            if name_el.is_visible(timeout=500):
                business["name"] = name_el.inner_text().strip()
            
            rating_el = card.locator(".MW4etd").first
            if rating_el.is_visible(timeout=500):
                business["rating"] = rating_el.inner_text().strip()
            
            review_el = card.locator(".UY7F9").first
            if review_el.is_visible(timeout=500):
                text = review_el.inner_text()
                match = re.search(r'\(?([\d,]+)\)?', text)
                if match:
                    business["review_count"] = match.group(1).replace(",", "")
            
            info_els = card.locator(".W4Efsd").all()
            for el in info_els:
                text = el.inner_text().strip()
                if text:
                    if not business["category"] and not any(c.isdigit() for c in text[:5]):
                        business["category"] = text.split("·")[0].strip()
                    elif "·" in text:
                        parts = text.split("·")
                        for part in parts:
                            part = part.strip()
                            if any(c.isdigit() for c in part):
                                business["address"] = part
        except Exception as e:
            pass
        return business
    
    def extract_details_from_panel(self, card, business):
        """Card click logic with correct indentation"""
        try:
            # 1. Target Name
            target_name = ""
            try:
                target_name = card.locator(".qBF1Pd, .fontHeadlineSmall").first.inner_text().strip()
            except:
                pass

            # 2. Card ko view me laao aur Click karo
            card.scroll_into_view_if_needed()
            card.click(position={"x": 10, "y": 10})

            # 3. Wait for Panel to Update (Pehle se tez check karenge)
            start_wait = time.time()
            max_wait = 10
            while time.time() - start_wait < max_wait:
                try:
                    # Side panel ka title check karein
                    panel_title = self.page.locator("h1.fontHeadlineLarge").first.inner_text().strip()
                    if target_name.lower() in panel_title.lower():
                        break # Jaise hi match hua, turant loop se bahar!
                except:
                    pass
                time.sleep(0.1) # Har 0.1 second me check karo (Super Fast)

            # 4. Global loading bar (Sirf tab ruko jab zaroori ho)
            try:
                if self.page.locator(".H9Lqpe").is_visible():
                    self.page.wait_for_selector(".H9Lqpe", state="hidden", timeout=2000) 
            except:
                pass

            # 5. Side panel scroll (Details load karne ke liye)
            self.page.mouse.wheel(0, 600) 
            time.sleep(0.5) # Sirf 0.5s rukainge scroll ke baad

            # 5. Extract Details
            # Phone
            try:
                phone_locators = [
                    self.page.locator("button[data-item-id^='phone']").last,
                    self.page.locator("[data-tooltip='Copy phone number']").last,
                    self.page.locator("a[href^='tel:']").last
                ]
                for loc in phone_locators:
                    if loc.is_visible(timeout=1000):
                        text = loc.inner_text() or loc.get_attribute("href")
                        if text:
                            business["phone"] = self.clean_phone_number(text)
                            break
            except: pass

            # Website
            try:
                web_loc = self.page.locator("a[data-item-id='authority']").last
                if web_loc.is_visible(timeout=1000):
                    business["website"] = web_loc.get_attribute("href")
            except: pass

            # Address
            try:
                addr_loc = self.page.locator("button[data-item-id='address']").last
                if addr_loc.is_visible(timeout=1000):
                    business["address"] = addr_loc.get_attribute("aria-label").replace("Address:", "").strip()
            except: pass

            # Place ID
            try:
                url = self.page.url
                match = re.search(r'!1s(0x[a-f0-9]+:[a-f0-9]+)', url)
                if match: business["place_id"] = match.group(1)
            except: pass

            print(f"[EXTRACTOR] Details done for: {business['name']}")

        except Exception as e:
            print(f"[ERROR] Detail extraction error: {e}")
            
        return business
    
    def extract_all_with_details(self, cards, limit=None):
        businesses = []
        cards_to_process = cards[:limit] if limit else cards
        total = len(cards_to_process)
        for idx, card in enumerate(cards_to_process):
            try:
                print(f"[INFO] {idx+1}/{total} processing...")
                business = self._extract_from_card(card, idx)
                if business and business.get("name"):
                    business = self.extract_details_from_panel(card, business)
                    businesses.append(business)
                    # Sabse kam delay taaki Google block na kare, par speed bani rahe
                    time.sleep(0.2) 

            except Exception as e:
                print(f"[ERROR] Card {idx}: {e}")
        return businesses
