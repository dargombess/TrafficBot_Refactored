"""
Browser Setup & Configuration
Setup Selenium browser dengan stealth features
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager
import zipfile
import os

class BrowserSetup:
    """Setup dan konfigurasi browser"""
    
    @staticmethod
    def create_driver(proxy: str = None, fingerprint: dict = None, 
                      headless: bool = False, visibility: str = "stealth"):
        """
        Create Selenium WebDriver dengan stealth config
        
        Args:
            proxy: Proxy string (format: IP:PORT atau IP:PORT:USER:PASS)
            fingerprint: Fingerprint dict dari FingerprintManager
            headless: Mode headless
            visibility: Mode visibility (stealth, ghost, normal)
        
        Returns:
            WebDriver instance
        """
        options = Options()
        
        # Basic options
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # User agent
        if fingerprint and 'user_agent' in fingerprint:
            options.add_argument(f'--user-agent={fingerprint["user_agent"]}')
        
        # Headless mode
        if headless:
            options.add_argument("--headless=new")
        
        # Visibility mode
        if visibility == "stealth":
            options.add_argument("--window-size=100,100")
            options.add_argument("--window-position=-100,-100")
        elif visibility == "ghost":
            options.add_argument("--window-size=1,1")
            options.add_argument("--window-position=-9999,-9999")
        else:  # normal
            options.add_argument("--window-size=1024,768")
        
        # Proxy setup
        has_auth = False
        if proxy:
            proxy_parts = proxy.split(':')
            if len(proxy_parts) == 4:  # IP:PORT:USER:PASS
                has_auth = True
                plugin_path = BrowserSetup._create_proxy_auth_plugin(
                    proxy_parts[0], proxy_parts[1], 
                    proxy_parts[2], proxy_parts[3]
                )
                options.add_extension(plugin_path)
            else:  # IP:PORT
                options.add_argument(f'--proxy-server={proxy}')
        
        # Create driver
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
            # Apply stealth
            stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
            )
            
            # Cleanup proxy plugin if used
            if has_auth and 'plugin_path' in locals():
                try:
                    os.remove(plugin_path)
                except:
                    pass
            
            return driver
        
        except Exception as e:
            print(f"Error creating driver: {e}")
            raise
    
    @staticmethod
    def _create_proxy_auth_plugin(host, port, username, password):
        """
        Create Chrome extension untuk proxy authentication
        
        Returns:
            Path ke plugin ZIP file
        """
        plugin_path = f"proxy_auth_plugin_{os.getpid()}.zip"
        
        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version":"22.0.0"
        }
        """
        
        background_js = f"""
        var config = {{
            mode: "fixed_servers",
            rules: {{
                singleProxy: {{
                    scheme: "http",
                    host: "{host}",
                    port: parseInt({port})
                }},
                bypassList: ["localhost"]
            }}
        }};
        
        chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});
        
        function callbackFn(details) {{
            return {{
                authCredentials: {{
                    username: "{username}",
                    password: "{password}"
                }}
            }};
        }}
        
        chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {{urls: ["<all_urls>"]}},
            ['blocking']
        );
        """
        
        # Create ZIP
        with zipfile.ZipFile(plugin_path, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        
        return plugin_path
    
    @staticmethod
    def set_window_visibility(driver, mode: str):
        """
        Set window visibility mode
        
        Args:
            driver: WebDriver instance
            mode: stealth, ghost, atau normal
        """
        try:
            if mode == "stealth":
                driver.set_window_size(100, 100)
                driver.set_window_position(-100, -100)
            elif mode == "ghost":
                driver.set_window_size(1, 1)
                driver.set_window_position(-9999, -9999)
            else:  # normal
                driver.set_window_size(1024, 768)
                driver.set_window_position(100, 100)
        except Exception as e:
            print(f"Error setting window visibility: {e}")

# Global helper
browser_setup = BrowserSetup()
