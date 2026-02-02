
import sys
import os
import time
import re
from playwright.sync_api import sync_playwright

def inspect_count():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        query = "gym in lucknow"
        print(f"Searching for: {query}")
        
        # Navigate
        page.goto(f"https://www.google.com/maps/search/{query.replace(' ', '+')}", wait_until="domcontentloaded")
        
        # Wait for load
        try:
            page.wait_for_selector("div[role='feed']", timeout=15000)
        except:
            print("Feed not found immediately, waiting...")
            time.sleep(5)
            
        # Get all text
        content = page.content()
        
        # Try to find specific indicators
        # Often "Results 1 - 20 of 120" is not visible in modern Gmaps 2024 UI.
        # Sometimes it is valid to just check the JS store or network, but that's hard.
        # Let's look for any text causing numbers.
        
        # Commonly, Gmaps doesn't show total count easily anymore.
        # However, checking for specific patterns.
        
        # Look for "Found X results"
        texts = page.evaluate("() => document.body.innerText")
        
        print("--- PAGE TEXT SNIPPET ---")
        print(texts[:1000])
        print("-------------------------")
        
        browser.close()

if __name__ == "__main__":
    inspect_count()
