"""
Stealth Module - Anti-detection और Stealth लॉजिक
Google द्वारा bot detection से बचने के लिए stealth techniques।
"""


def apply_stealth_settings(page):
    """
    Page पर stealth settings apply करता है।
    यह bot detection को bypass करने में मदद करता है।
    
    Args:
        page: Playwright page object
    """
    
    # Navigator webdriver property को hide करें
    stealth_js = """
    () => {
        // webdriver property को undefined करें
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });
        
        // Languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en', 'hi'],
        });
        
        // Plugins (empty array से बचें)
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });
        
        // Chrome object add करें
        window.chrome = {
            runtime: {},
        };
        
        // Permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        
        // Console.debug को override करें (DevTools detection से बचें)
        window.console.debug = () => null;
    }
    """
    
    try:
        page.add_init_script(stealth_js)
        print("[INFO] Stealth settings applied")
    except Exception as e:
        print(f"[WARN] Stealth settings error: {e}")


def random_mouse_movement(page, x_range=(100, 800), y_range=(100, 600)):
    """
    Random mouse movement (human-like behavior)
    
    Args:
        page: Playwright page object
        x_range: X coordinate range
        y_range: Y coordinate range
    """
    import random
    
    try:
        x = random.randint(x_range[0], x_range[1])
        y = random.randint(y_range[0], y_range[1])
        page.mouse.move(x, y)
    except Exception:
        pass  # Ignore mouse movement errors


def random_scroll(page, scroll_range=(100, 500)):
    """
    Random scroll amount
    
    Args:
        page: Playwright page object
        scroll_range: Scroll pixel range
    """
    import random
    
    try:
        scroll_amount = random.randint(scroll_range[0], scroll_range[1])
        page.evaluate(f"window.scrollBy(0, {scroll_amount})")
    except Exception:
        pass
