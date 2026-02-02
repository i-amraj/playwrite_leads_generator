#!/usr/bin/env python3
"""
🧪 Interactive Google Maps Scraper - Testing Version
यह script terminal पर interactive mode में run होती है।

Usage:
    python3 interactive_scraper.py
"""

import sys
import os
import time
import random
import json
import re

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend', 'python'))

from core.browser import BrowserManager
from core.search import GoogleMapsSearch
from core.extractor import DataExtractor


def print_banner():
    """Banner print करता है"""
    print("\n" + "="*60)
    print("🌍 GOOGLE MAPS LEAD GENERATOR - INTERACTIVE MODE")
    print("="*60)
    print("📌 यह testing version है - data verify करने के लिए")
    print("="*60 + "\n")


def print_delay(seconds, message=""):
    """
    Delay को screen पर show करता है (countdown style)
    """
    print(f"\n⏳ {message}")
    for i in range(int(seconds), 0, -1):
        print(f"   ⏰ Waiting... {i} seconds remaining", end="\r")
        time.sleep(1)
    print(f"   ✅ Wait complete!                    ")


def human_delay(min_sec=2, max_sec=5, message="Human-like delay"):
    """
    Random human-like delay with visual feedback
    """
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
    city = get_user_input("Enter City Name")
    print(f"   ✅ City: {city}\n")
    
    # Step 3: Business type input
    print("🏢 STEP 3: Business Type Enter करें")
    print("-" * 40)
    print("   Examples: gym, restaurant, hotel, hospital, school, salon")
    business_type = get_user_input("Enter Business Type")
    print(f"   ✅ Business Type: {business_type}\n")
    
    # Build search query
    query = f"{business_type} in {city}, {country}"
    
    print("\n" + "="*60)
    print(f"🔍 SEARCH QUERY: {query}")
    print("="*60)
    
    # Confirmation
    if not get_yes_no("क्या आप search शुरू करना चाहते हैं?"):
        print("\n❌ Search cancelled by user.")
        return
    
    browser_manager = None
    
    try:
        # Step 4: Launch browser
        print("\n" + "-"*60)
        print("🚀 STEP 4: Browser Launch हो रहा है...")
        print("-"*60)
        
        human_delay(1, 3, "Browser initializing")
        
        browser_manager = BrowserManager()
        browser_manager.config["headless"] = True  # Headless mode for testing
        page = browser_manager.launch()
        
        print("   ✅ Browser launched successfully!\n")
        
        # Step 5: Search
        print("-"*60)
        print(f"🔍 STEP 5: Searching for '{query}'...")
        print("-"*60)
        
        human_delay(2, 4, "Preparing search")
        
        search = GoogleMapsSearch(page)
        if not search.search_direct_url(query):
            raise Exception("Search failed!")
        
        print("   ✅ Search completed!\n")
        
        # Step 6: Scroll and count
        print("-"*60)
        print("📜 STEP 6: Scrolling for more results...")
        print("-"*60)
        
        # Scroll with visible delays
        for i in range(5):
            print(f"\n   📜 Scroll {i+1}/5...")
            search.scroll_results(times=1)
            human_delay(1.5, 3, f"Loading more results (Scroll {i+1})")
        
        # Get total count
        cards = search.get_cards()
        total_count = len(cards)
        
        print("\n" + "="*60)
        print(f"📊 TOTAL RESULTS FOUND: {total_count} {business_type}(s)")
        print("="*60)
        
        # Step 7: Ask to extract
        print(f"\n🎯 {city} में कुल {total_count} {business_type} मिले!")
        
        if total_count == 0:
            print("❌ No results found. Try different search terms.")
            return
        
        if not get_yes_no(f"क्या आप सभी {total_count} records extract करना चाहते हैं?"):
            print("\n❌ Extraction cancelled by user.")
            return
        
        # Step 8: Extract data
        print("\n" + "-"*60)
        print("📥 STEP 7: Extracting detailed data...")
        print("-"*60)
        print("⚠️  This will take time due to human-like delays\n")
        
        extractor = DataExtractor(page)
        businesses = []
        
        for idx, card in enumerate(cards):
            print(f"\n{'='*50}")
            print(f"📍 Processing {idx + 1}/{total_count}...")
            print(f"{'='*50}")
            
            try:
                # Extract basic info
                business = extractor._extract_from_card(card, idx)
                
                if business and business.get("name"):
                    print(f"   📌 Name: {business['name'][:50]}...")
                    
                    # Human delay before clicking
                    human_delay(2, 4, "Preparing to get details")
                    
                    # Extract details
                    business = extractor.extract_details_from_panel(card, business)
                    
                    # Show extracted data
                    print(f"   ⭐ Rating: {business.get('rating', 'N/A')}")
                    print(f"   📞 Phone: {business.get('phone', 'N/A')}")
                    print(f"   🌐 Website: {business.get('website', 'N/A')[:40]}..." if business.get('website') else "   🌐 Website: N/A")
                    print(f"   📍 Address: {business.get('address', 'N/A')[:50]}..." if business.get('address') else "   📍 Address: N/A")
                    
                    businesses.append(business)
                    print(f"   ✅ Extracted successfully!")
                    
                    # Human delay after extraction
                    human_delay(2, 5, "Moving to next record")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
                human_delay(1, 2, "Recovering from error")
                continue
        
        # Step 9: Summary and Save
        print("\n" + "="*60)
        print("✅ EXTRACTION COMPLETE!")
        print("="*60)
        print(f"📊 Total Records Extracted: {len(businesses)}")
        print(f"❌ Failed Records: {total_count - len(businesses)}")
        print("="*60)
        
        # Save results
        if businesses:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"{business_type}_{city}_{timestamp}.json"
            filepath = save_results({
                "query": query,
                "total_found": total_count,
                "total_extracted": len(businesses),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "data": businesses
            }, filename)
            
            print(f"\n💾 Data saved to: {filepath}")
            
            # Show sample data
            print("\n📋 SAMPLE DATA (First 3 records):")
            print("-"*60)
            for biz in businesses[:3]:
                print(f"\n   📌 {biz.get('name', 'N/A')}")
                print(f"      ⭐ Rating: {biz.get('rating', 'N/A')}")
                print(f"      📞 Phone: {biz.get('phone', 'N/A')}")
                print(f"      🌐 Website: {biz.get('website', 'N/A')}")
        
        print("\n" + "="*60)
        print("🎉 THANK YOU FOR USING LEAD GENERATOR!")
        print("="*60 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n❌ Interrupted by user (Ctrl+C)")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        
    finally:
        if browser_manager:
            print("\n🔄 Closing browser...")
            human_delay(1, 2, "Cleanup")
            browser_manager.close()
            print("   ✅ Browser closed.\n")


if __name__ == "__main__":
    main()
