#!/usr/bin/env python3
"""
Google Maps Lead Generator - Main Entry Point
यह script terminal से run होगी और JSON output देगी।

Usage:
    python main.py --keyword "gym" --location "lucknow" --limit 20
    python main.py --keyword "restaurant" --location "delhi" --limit 10 --details
    
Arguments:
    --keyword    : Business type (gym, restaurant, hotel, etc.)
    --location   : City/Area name
    --limit      : Number of results to scrape (default: 10)
    --details    : If set, extract full details (phone, website) by clicking each card
    --headless   : Run browser in headless mode (no UI)
    --output     : Output file path for JSON (optional)
"""

import argparse
import json
import sys
import os
import time
import traceback

# Ensure we can import from core/ and config/
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.browser import BrowserManager
from core.search import GoogleMapsSearch
from core.extractor import DataExtractor


def create_response(success, message="", data=None, error=None):
    """Standard JSON response format बनाता है"""
    return {
        "success": success,
        "message": message,
        "data": data or [],
        "error": error,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }


def save_to_file(data, filepath):
    """Data को JSON file में save करता है"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[INFO] Data saved to: {filepath}", file=sys.stderr)
        return True
    except Exception as e:
        print(f"[ERROR] Save failed: {e}", file=sys.stderr)
        return False


def main():
    """Main function - CLI entry point"""
    
    # Argument parser setup
    parser = argparse.ArgumentParser(
        description="Google Maps Lead Generator - Scrape business data from Google Maps",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py --keyword "gym" --location "lucknow"
    python main.py --keyword "restaurant" --location "delhi" --limit 20
    python main.py --keyword "hotel" --location "mumbai" --details --headless
        """
    )
    
    parser.add_argument(
        "--keyword", 
        required=True, 
        help="Business type to search (e.g., gym, restaurant, hotel)"
    )
    parser.add_argument(
        "--location", 
        required=True, 
        help="City or area to search in (e.g., lucknow, delhi)"
    )
    parser.add_argument(
        "--limit", 
        type=int, 
        default=10, 
        help="Maximum number of results to scrape (default: 10)"
    )
    parser.add_argument(
        "--details", 
        action="store_true", 
        help="Extract full details (phone, website) by clicking each card"
    )
    parser.add_argument(
        "--headless", 
        action="store_true", 
        help="Run browser without UI (headless mode)"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        default=None, 
        help="Output file path for JSON (optional, also prints to stdout)"
    )
    parser.add_argument(
        "--scroll-times",
        type=int,
        default=5,
        help="Number of times to scroll before extracting (default: 5)"
    )
    
    parser.add_argument(
        "--country", 
        type=str, 
        default="India", 
        help="Country name for phone number formatting (default: India)"
    )
    
    args = parser.parse_args()
    
    # Search query बनाएं
    query = f"{args.keyword} in {args.location}"
    
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"🚀 Google Maps Lead Generator", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)
    print(f"📍 Query: {query}", file=sys.stderr)
    print(f"🌍 Country: {args.country}", file=sys.stderr)
    print(f"📊 Limit: {args.limit}", file=sys.stderr)
    print(f"🔍 Details: {'Yes' if args.details else 'No'}", file=sys.stderr)
    print(f"👻 Headless: {'Yes' if args.headless else 'No'}", file=sys.stderr)
    print(f"{'='*60}\n", file=sys.stderr)
    
    browser_manager = None
    
    try:
        # 1. Browser launch करें
        print("[STEP 1/5] Launching browser...", file=sys.stderr)
        browser_manager = BrowserManager()
        
        # Override headless setting if specified
        if args.headless:
            browser_manager.config["headless"] = True
        
        # Pass country locale if possible or just use in extractor
        # browser_manager could set locale based on country but defaulting to EN-US/System is fine for now
        
        page = browser_manager.launch()
        
        # 2. Google Maps पर search करें
        print(f"[STEP 2/5] Searching for: {query}...", file=sys.stderr)
        search = GoogleMapsSearch(page)
        
        if not search.search_direct_url(query):
            raise Exception("Search failed - could not navigate to Google Maps")
        
        # 3. Results scroll करें
        print(f"[STEP 3/5] Checking available results...", file=sys.stderr)
        
        # Method A: Text detection
        total_available = search.get_total_count()
        known_total = False
        
        if total_available > 0:
            print(f"[INFO] Detected total available results via text: {total_available}", file=sys.stderr)
            known_total = True
        else:
            print("[INFO] Total count text not found, will estimate by scrolling", file=sys.stderr)
            
        print(f"[STEP 3.5] Scrolling results...", file=sys.stderr)
        
        # Initialize loop variables
        loaded_count = len(search.get_cards())
        max_scrolls = args.scroll_times
        
        # If user didn't specify high scroll times but wants "total", we should try to scroll reasonable amount
        # User said: "sare result nikal payenge 20 20 krke" -> implies we need to KNOW the total first.
        # If we didn't find text, scrolling IS the only way.
        # We'll scroll up to 20 times automatically if detailed total is needed, unless specified otherwise.
        
        if not known_total and max_scrolls <= 5:
             # Bump up auto-scroll to try and find end of list for small datasets
             # Gmaps usually has ~120 results max. 50 scrolls (50*20 results potentially) is plenty.
             max_scrolls = 50
        
        # Scroll loop
        final_count = search.scroll_until_end(max_scrolls=max_scrolls, stop_after_no_change=4)
        
        # Recalculate total available
        if not known_total:
            total_available = final_count
            
        print(f"[INFO] Final loaded count: {final_count}. Estimated Total: {total_available}", file=sys.stderr)

        
        # 4. Cards extract करें
        print("[STEP 4/5] Getting business cards...", file=sys.stderr)
        cards = search.get_cards()
        
        if not cards:
            print("[WARN] No business cards found", file=sys.stderr)
            response = create_response(
                success=True,
                message="No businesses found for this search",
                data=[]
            )
            print(json.dumps(response, ensure_ascii=False, indent=2))
            return
        
        print(f"[INFO] Found {len(cards)} cards", file=sys.stderr)
        
        # 5. Data extract करें
        print(f"[STEP 5/5] Extracting data (limit: {args.limit})...", file=sys.stderr)
        
        # Pass country argument here
        extractor = DataExtractor(page, country=args.country)
        
        if args.details:
            # Click करके full details extract करें
            businesses = extractor.extract_all_with_details(cards, limit=args.limit)
        else:
            # Basic info only (faster)
            businesses = extractor.extract_basic_info_from_cards(cards, limit=args.limit)
        
        # Response बनाएं
        response = create_response(
            success=True,
            message=f"Successfully extracted {len(businesses)} businesses for '{query}'",
            data=businesses
        )
        # Add total_found metadata specifically
        # If we detected text, use that. Else use what we found by scrolling.
        response['total_found'] = total_available
        
        # Output file में save करें (if specified)
        if args.output:
            save_to_file(response, args.output)
        
        # JSON stdout पर print करें
        print("\n" + "="*60, file=sys.stderr)
        print("✅ EXTRACTION COMPLETE", file=sys.stderr)
        print("="*60, file=sys.stderr)
        print(f"📊 Total Businesses: {len(businesses)}", file=sys.stderr)
        print(f"🔢 Total Available: {response['total_found']}", file=sys.stderr)
        print("="*60 + "\n", file=sys.stderr)

        
        # Final JSON output
        print(json.dumps(response, ensure_ascii=False, indent=2))
        
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user", file=sys.stderr)
        response = create_response(
            success=False,
            message="Scraping interrupted by user",
            error="KeyboardInterrupt"
        )
        print(json.dumps(response, ensure_ascii=False))
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        
        response = create_response(
            success=False,
            message="Scraping failed",
            error=str(e)
        )
        print(json.dumps(response, ensure_ascii=False))
        
    finally:
        # Browser cleanup
        if browser_manager:
            print("\n[INFO] Closing browser...", file=sys.stderr)
            browser_manager.close()



if __name__ == "__main__":
    main()
