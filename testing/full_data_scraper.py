#!/usr/bin/env python3
"""
🧪 Advanced Google Maps Scraper - Full Data Extraction
यह script maximum data निकालने के लिए है।

Features:
- Scroll until no new results (maximum data from single search)
- Area-wise search for complete coverage
- Duplicate detection and removal
- Progress tracking with delays

Usage:
    python3 full_data_scraper.py
"""

import sys
import os
import time
import random
import json
import hashlib

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend', 'python'))

from core.browser import BrowserManager
from core.search import GoogleMapsSearch
from core.extractor import DataExtractor


# ===============================
# COMMON AREAS FOR INDIAN CITIES
# ===============================
CITY_AREAS = {
    "lucknow": [
        "", # Main search first
        "gomti nagar", "hazratganj", "aliganj", "indira nagar", 
        "rajajipuram", "alambagh", "chowk", "aminabad",
        "mahanagar", "vikas nagar", "jankipuram", "faizabad road",
        "kanpur road", "sitapur road", "aashiana", "chinhat"
    ],
    "delhi": [
        "",
        "connaught place", "karol bagh", "dwarka", "rohini",
        "pitampura", "janakpuri", "rajouri garden", "laxmi nagar",
        "preet vihar", "saket", "vasant kunj", "greater kailash",
        "defence colony", "hauz khas", "nehru place", "south extension"
    ],
    "mumbai": [
        "",
        "andheri", "bandra", "juhu", "malad", "goregaon",
        "borivali", "kandivali", "powai", "thane", "navi mumbai",
        "dadar", "worli", "lower parel", "byculla", "colaba"
    ],
    "default": [
        "", # Just main search if city not in list
    ]
}


def print_banner():
    """Banner print करता है"""
    print("\n" + "="*70)
    print("🌍 GOOGLE MAPS LEAD GENERATOR - FULL DATA MODE")
    print("="*70)
    print("📌 यह script maximum possible data extract करती है")
    print("📌 Multiple areas search करके complete coverage देती है")
    print("="*70 + "\n")


def print_delay(seconds, message=""):
    """Delay को screen पर show करता है"""
    print(f"\n⏳ {message}")
    for i in range(int(seconds), 0, -1):
        print(f"   ⏰ Waiting... {i} seconds remaining", end="\r")
        time.sleep(1)
    print(f"   ✅ Wait complete!                    ")


def human_delay(min_sec=2, max_sec=5, message="Human-like delay"):
    """Random human-like delay with visual feedback"""
    delay = random.uniform(min_sec, max_sec)
    print_delay(delay, f"{message} ({delay:.1f}s)")
    return delay


def get_user_input(prompt, default=None):
    """User से input लेता है"""
    if default:
        user_input = input(f"👉 {prompt} [{default}]: ").strip()
        return user_input if user_input else default
    else:
        while True:
            user_input = input(f"👉 {prompt}: ").strip()
            if user_input:
                return user_input
            print("   ❌ This field is required!")


def get_yes_no(prompt):
    """Yes/No input लेता है"""
    while True:
        response = input(f"👉 {prompt} (y/n): ").strip().lower()
        if response in ['y', 'yes', 'हाँ', 'ha']:
            return True
        elif response in ['n', 'no', 'नहीं', 'nahi']:
            return False
        print("   ❌ Please enter 'y' for Yes or 'n' for No")


def get_hash(business):
    """Business का unique hash बनाता है (duplicate detection के लिए)"""
    # Name + first 20 chars of address = unique identifier
    key = f"{business.get('name', '')}{business.get('address', '')[:20]}"
    return hashlib.md5(key.encode()).hexdigest()


def scroll_until_end(page, search_obj, max_scrolls=100):
    """
    जब तक नए results आ रहे हैं तब तक scroll करता है।
    Returns: Total cards found
    """
    prev_count = 0
    same_count = 0
    scroll_num = 0
    
    print("\n   📜 Scrolling for ALL results...")
    
    while scroll_num < max_scrolls and same_count < 5:
        # Current cards count
        cards = search_obj.get_cards()
        curr_count = len(cards)
        
        if curr_count == prev_count:
            same_count += 1
        else:
            same_count = 0
            print(f"   📊 Found {curr_count} results (+{curr_count - prev_count} new)")
        
        prev_count = curr_count
        
        # Scroll
        try:
            page.evaluate("""
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
        except:
            pass
        
        # Check for end indicator
        try:
            end_text = page.locator("span:has-text('end of list'), span:has-text(\"You've reached the end\")").first
            if end_text.is_visible(timeout=500):
                print("   🏁 Reached end of list!")
                break
        except:
            pass
        
        # Delay
        delay = random.uniform(1.5, 2.5)
        time.sleep(delay)
        scroll_num += 1
    
    final_count = len(search_obj.get_cards())
    print(f"   ✅ Scroll complete! Total: {final_count} results")
    return final_count


def save_results(data, filename):
    """Results को JSON file में save करता है"""
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return filepath


def main():
    """Main interactive function"""
    
    print_banner()
    
    # Step 1: Country input
    print("📍 STEP 1: Country Select करें")
    print("-" * 40)
    country = get_user_input("Enter Country Name", "India")
    print(f"   ✅ Country: {country}\n")
    
    # Step 2: City input
    print("🏙️ STEP 2: City Enter करें")
    print("-" * 40)
    city = get_user_input("Enter City Name").lower()
    print(f"   ✅ City: {city}\n")
    
    # Step 3: Business type input
    print("🏢 STEP 3: Business Type Enter करें")
    print("-" * 40)
    print("   Examples: gym, restaurant, hotel, hospital, school, salon")
    business_type = get_user_input("Enter Business Type").lower()
    print(f"   ✅ Business Type: {business_type}\n")
    
    # Get areas for this city
    areas = CITY_AREAS.get(city, CITY_AREAS["default"])
    
    print("\n" + "="*70)
    print(f"🔍 SEARCH STRATEGY:")
    print(f"   📍 City: {city.title()}")
    print(f"   🏢 Type: {business_type}")
    print(f"   🗺️ Areas to search: {len(areas)} areas")
    print("="*70)
    
    if len(areas) > 1:
        print("\n   Areas: " + ", ".join([a if a else "Main City" for a in areas[:8]]))
        if len(areas) > 8:
            print(f"          ... and {len(areas) - 8} more")
    
    # Mode selection
    print("\n📋 SELECT MODE:")
    print("   1️⃣  Quick Mode - Single search (20-60 results)")
    print("   2️⃣  Full Mode  - All areas search (Maximum results)")
    
    mode = get_user_input("Enter mode (1 or 2)", "1")
    full_mode = (mode == "2")
    
    if full_mode:
        print(f"\n   ✅ Full Mode selected - Will search {len(areas)} areas")
    else:
        print("   ✅ Quick Mode selected - Single search")
        areas = [""]  # Only main search
    
    # Confirmation
    if not get_yes_no("\nक्या आप search शुरू करना चाहते हैं?"):
        print("\n❌ Search cancelled by user.")
        return
    
    browser_manager = None
    all_businesses = []
    seen_hashes = set()
    
    try:
        # Launch browser
        print("\n" + "-"*70)
        print("🚀 Launching Browser...")
        print("-"*70)
        
        human_delay(1, 2, "Browser initializing")
        
        browser_manager = BrowserManager()
        browser_manager.config["headless"] = True
        page = browser_manager.launch()
        
        print("   ✅ Browser launched!\n")
        
        search = GoogleMapsSearch(page)
        extractor = DataExtractor(page)
        
        # Search each area
        for area_idx, area in enumerate(areas):
            # Build query
            if area:
                query = f"{business_type} in {area} {city}"
            else:
                query = f"{business_type} in {city}"
            
            print("\n" + "="*70)
            print(f"🔍 AREA {area_idx + 1}/{len(areas)}: {area if area else 'Main City'}")
            print(f"   Query: {query}")
            print("="*70)
            
            # Search
            human_delay(2, 4, "Navigating to Google Maps")
            
            if not search.search_direct_url(query):
                print("   ❌ Search failed for this area, skipping...")
                continue
            
            print("   ✅ Search completed!")
            
            # Scroll until end
            total_in_area = scroll_until_end(page, search)
            
            # Get cards
            cards = search.get_cards()
            print(f"\n   📊 Found {len(cards)} results in {area if area else 'main'} area")
            
            if not cards:
                print("   ⚠️ No results in this area")
                human_delay(2, 3, "Moving to next area")
                continue
            
            # Ask to extract (only for quick mode or first area)
            if area_idx == 0 or not full_mode:
                if not get_yes_no(f"   क्या आप {len(cards)} records extract करना चाहते हैं?"):
                    if full_mode:
                        continue
                    else:
                        print("\n❌ Extraction cancelled.")
                        return
            
            # Extract data from this area
            print(f"\n   📥 Extracting data from {len(cards)} results...")
            
            new_count = 0
            duplicate_count = 0
            
            for idx, card in enumerate(cards):
                # Progress indicator
                if (idx + 1) % 5 == 0 or idx == 0:
                    print(f"\n   📍 Processing {idx + 1}/{len(cards)} in {area if area else 'main'}...")
                
                try:
                    # Basic info
                    business = extractor._extract_from_card(card, idx)
                    
                    if not business or not business.get("name"):
                        continue
                    
                    # Check duplicate
                    biz_hash = get_hash(business)
                    if biz_hash in seen_hashes:
                        duplicate_count += 1
                        continue
                    
                    seen_hashes.add(biz_hash)
                    
                    # Get details
                    human_delay(1.5, 3, f"Getting details for {business['name'][:30]}...")
                    business = extractor.extract_details_from_panel(card, business)
                    business["area"] = area if area else "main"
                    
                    all_businesses.append(business)
                    new_count += 1
                    
                    # Show progress
                    print(f"      ✅ {business['name'][:40]}...")
                    print(f"         📞 {business.get('phone', 'N/A')} | ⭐ {business.get('rating', 'N/A')}")
                    
                    # Longer delay every 10 records (anti-detection)
                    if new_count % 10 == 0:
                        human_delay(5, 10, "⚠️ Taking a break to avoid detection")
                    
                except Exception as e:
                    print(f"      ❌ Error: {e}")
                    continue
            
            print(f"\n   📊 Area Summary: {new_count} new, {duplicate_count} duplicates")
            print(f"   📊 Total collected so far: {len(all_businesses)}")
            
            # Delay between areas
            if area_idx < len(areas) - 1:
                human_delay(5, 10, "🔄 Taking break before next area")
        
        # Final Summary
        print("\n" + "="*70)
        print("✅ EXTRACTION COMPLETE!")
        print("="*70)
        print(f"📊 Total Unique Records: {len(all_businesses)}")
        print(f"🔍 Areas Searched: {len(areas)}")
        print("="*70)
        
        # Save results
        if all_businesses:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"{business_type}_{city}_FULL_{timestamp}.json"
            filepath = save_results({
                "query": f"{business_type} in {city}",
                "city": city,
                "country": country,
                "business_type": business_type,
                "areas_searched": len(areas),
                "total_unique": len(all_businesses),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "data": all_businesses
            }, filename)
            
            print(f"\n💾 Data saved to: {filepath}")
            
            # Show sample
            print("\n📋 SAMPLE DATA (First 5 records):")
            print("-"*70)
            for biz in all_businesses[:5]:
                print(f"\n   📌 {biz.get('name', 'N/A')}")
                print(f"      📍 Area: {biz.get('area', 'N/A')}")
                print(f"      ⭐ Rating: {biz.get('rating', 'N/A')}")
                print(f"      📞 Phone: {biz.get('phone', 'N/A')}")
        
        print("\n" + "="*70)
        print("🎉 THANK YOU FOR USING LEAD GENERATOR!")
        print("="*70 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n❌ Interrupted by user (Ctrl+C)")
        
        # Save partial results
        if all_businesses:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"{business_type}_{city}_PARTIAL_{timestamp}.json"
            filepath = save_results({
                "status": "partial",
                "total": len(all_businesses),
                "data": all_businesses
            }, filename)
            print(f"💾 Partial data saved to: {filepath}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if browser_manager:
            print("\n🔄 Closing browser...")
            human_delay(1, 2, "Cleanup")
            browser_manager.close()
            print("   ✅ Browser closed.\n")


if __name__ == "__main__":
    main()
