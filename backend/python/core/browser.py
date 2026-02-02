"""
Browser Module - ब्राउज़र लॉन्च और मैनेजमेंट
Playwright browser को launch और manage करता है।
"""

import random
import json
import os
from playwright.sync_api import sync_playwright
from .stealth import apply_stealth_settings


# User Agents की सूची (फ़िंगरप्रिंट रोटेशन के लिए)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]


class BrowserManager:
    """Playwright Browser को manage करने की class"""
    
    def __init__(self, config_path=None):
        """
        Browser Manager को initialize करता है।
        
        Args:
            config_path: settings.json का path (optional)
        """
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
        # Config load करें
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "config", "settings.json"
            )
        
        self.config = self._load_config(config_path)
    
    def _load_config(self, config_path):
        """Config file load करता है"""
        default_config = {
            "headless": False,  # Testing के लिए visible browser
            "timeout": 60000,
            "max_retries": 3,
            "delay_min": 2000,
            "delay_max": 5000,
            "user_agent_rotate": True
        }
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    loaded = json.load(f)
                    default_config.update(loaded)
        except Exception as e:
            print(f"[WARN] Config load error: {e}, using defaults")
        
        return default_config
    
    def launch(self):
        """
        Browser launch करता है।
        
        Returns:
            page: Playwright page object
        """
        try:
            self.playwright = sync_playwright().start()
            
            # Random user agent चुनें
            user_agent = random.choice(USER_AGENTS) if self.config.get("user_agent_rotate", True) else USER_AGENTS[0]
            
            # Random viewport
            viewports = [
                {"width": 1920, "height": 1080},
                {"width": 1366, "height": 768},
                {"width": 1536, "height": 864},
                {"width": 1440, "height": 900},
            ]
            viewport = random.choice(viewports)
            
            # Browser launch options
            self.browser = self.playwright.chromium.launch(
                headless=self.config.get("headless", False),
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                ]
            )
            
            # Context with stealth settings
            self.context = self.browser.new_context(
                user_agent=user_agent,
                viewport=viewport,
                locale="en-US",
                timezone_id="Asia/Kolkata",
            )
            
            # Timeouts set करें
            self.context.set_default_timeout(self.config.get("timeout", 60000))
            
            # New page
            self.page = self.context.new_page()
            
            # Stealth settings apply करें
            apply_stealth_settings(self.page)
            
            print(f"[INFO] Browser launched (headless={self.config.get('headless')})")
            return self.page
            
        except Exception as e:
            self.close()
            raise Exception(f"Browser launch failed: {e}")
    
    def close(self):
        """Browser और resources को बंद करता है"""
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            print("[INFO] Browser closed")
        except Exception as e:
            print(f"[WARN] Error closing browser: {e}")
    
    def random_delay(self, min_ms=None, max_ms=None):
        """Random delay जोड़ता है (human-like behavior के लिए)"""
        import time
        min_delay = min_ms or self.config.get("delay_min", 2000)
        max_delay = max_ms or self.config.get("delay_max", 5000)
        delay = random.randint(min_delay, max_delay) / 1000.0
        time.sleep(delay)
        return delay
