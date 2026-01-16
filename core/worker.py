"""
Bot Worker - The Brain of Traffic Bot
Menjalankan semua task dengan human-like behavior + CAPTCHA DETECTION
"""

import time
import random
import os
import json
import zipfile
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bot_config import config
from utils.logger import logger

class BotWorker:
    """Worker untuk menjalankan single bot task dengan full features + captcha detection"""
    
    def __init__(self, worker_id: int):
        """
        Initialize worker
        
        Args:
            worker_id: ID unik untuk worker ini
        """
        self.worker_id = worker_id
        self.driver = None
        self.is_running = False
        self.proxy = None
        self.proxy_host = None
        self.proxy_port = None
        self.proxy_user = None
        self.proxy_pass = None
        self.has_auth = False
        self.is_hidden = True
        self.fingerprint_data = None
        self.captcha_detected_count = 0
    
    def parse_proxy(self, proxy_str: str):
        """
        Parse proxy string
        
        Args:
            proxy_str: Proxy dalam format IP:PORT atau IP:PORT:USER:PASS
        """
        if not proxy_str:
            return
        
        parts = proxy_str.split(':')
        if len(parts) == 2:
            # IP:PORT
            self.proxy_host = parts[0]
            self.proxy_port = parts[1]
            self.has_auth = False
        elif len(parts) == 4:
            # IP:PORT:USER:PASS
            self.proxy_host = parts[0]
            self.proxy_port = parts[1]
            self.proxy_user = parts[2]
            self.proxy_pass = parts[3]
            self.has_auth = True
    
    def create_proxy_extension(self) -> str:
        """
        Create Chrome extension for proxy authentication
        
        Returns:
            Path ke extension zip file
        """
        if not self.has_auth:
            return None
        
        try:
            manifest_json = """
            {
                "version": "1.0.0",
                "manifest_version": 3,
                "name": "Chrome Proxy",
                "permissions": ["proxy", "tabs", "unlimitedStorage", "storage", "webRequest", "webRequestAuthProvider"],
                "host_permissions": ["<all_urls>"],
                "background": {
                    "service_worker": "background.js"
                }
            }
            """
            
            background_js = f"""
            var config = {{
                mode: "fixed_servers",
                rules: {{
                    singleProxy: {{
                        scheme: "http",
                        host: "{self.proxy_host}",
                        port: parseInt({self.proxy_port})
                    }},
                    bypassList: ["localhost"]
                }}
            }};
            
            chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});
            
            chrome.webRequest.onAuthRequired.addListener(
                function(details) {{
                    return {{
                        authCredentials: {{
                            username: "{self.proxy_user}",
                            password: "{self.proxy_pass}"
                        }}
                    }};
                }},
                {{urls: ["<all_urls>"]}},
                ["blocking"]
            );
            """
            
            plugin_file = f"proxy_auth_plugin_{self.worker_id}.zip"
            
            with zipfile.ZipFile(plugin_file, 'w') as zp:
                zp.writestr("manifest.json", manifest_json)
                zp.writestr("background.js", background_js)
            
            return plugin_file
            
        except Exception as e:
            logger.error(f"Worker {self.worker_id}: Error creating proxy extension - {e}")
            return None
    
    def load_fingerprint(self):
        """Load fingerprint based on config mode"""
        fp_mode = getattr(config, 'FINGERPRINT_MODE', 'Cortex')
        
        if fp_mode == 'JSON':
            json_folder = getattr(config, 'FINGERPRINT_FOLDER', '')
            if json_folder and os.path.exists(json_folder):
                try:
                    files = [f for f in os.listdir(json_folder) if f.endswith('.json')]
                    if files:
                        chosen_file = random.choice(files)
                        with open(os.path.join(json_folder, chosen_file), 'r', encoding='utf-8') as f:
                            self.fingerprint_data = json.load(f)
                        logger.info(f"Worker {self.worker_id}: Loaded fingerprint from {chosen_file}")
                except Exception as e:
                    logger.error(f"Worker {self.worker_id}: Error loading fingerprint - {e}")
    
    def setup_driver(self, proxy: str = None):
        """
        Setup Chrome driver dengan full features + ADVANCED ANTI-DETECTION
        
        Args:
            proxy: Proxy string (optional)
            
        Returns:
            True jika sukses setup driver
        """
        try:
            # Parse proxy
            if proxy:
                self.proxy = proxy
                self.parse_proxy(proxy)
            
            # Load fingerprint
            self.load_fingerprint()
            
            options = Options()
            
            # ========== ADVANCED ANTI-DETECTION OPTIONS ==========
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-infobars")
            options.add_argument("--disable-notifications")
            options.add_argument("--disable-popup-blocking")
            options.add_argument("--no-first-run")
            options.add_argument("--no-service-autorun")
            options.add_argument("--password-store=basic")
            options.add_argument("--disable-web-security")
            options.add_argument("--allow-running-insecure-content")
            
            # Critical for bypassing bot detection
            options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # ========== USER AGENT STRATEGY ==========
            ua_mode = getattr(config, 'USER_AGENT_MODE', 'Mixed')
            
            if self.fingerprint_data:
                # Use fingerprint user agent
                ua = self.fingerprint_data.get('navigator', {}).get('userAgent')
                if ua:
                    options.add_argument(f'--user-agent={ua}')
            elif ua_mode == 'Mobile Only':
                options.add_experimental_option("mobileEmulation", {"deviceName": "iPhone 12 Pro"})
            elif ua_mode == 'Desktop Only':
                # Use realistic desktop UA
                options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
            else:
                # Mixed - random
                if random.random() < 0.7:  # 70% desktop
                    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
                else:  # 30% mobile
                    options.add_experimental_option("mobileEmulation", {"deviceName": "iPhone 12 Pro"})
            
            # ========== HEADLESS MODE ==========
            if getattr(config, 'HEADLESS', False):
                options.add_argument("--headless=new")
                options.add_argument("--disable-gpu")
            
            # ========== BROWSER VISIBILITY ==========
            visibility = getattr(config, 'BROWSER_VISIBILITY', 'stealth')
            if visibility == "stealth":
                options.add_argument("--window-position=-2400,-2400")
                options.add_argument("--window-size=100,100")
            elif visibility == "ghost":
                options.add_argument("--window-position=-9999,-9999")
                options.add_argument("--window-size=1,1")
            else:
                options.add_argument("--window-size=1024,768")
            
            # ========== PROXY SETUP ==========
            if self.proxy:
                if self.has_auth:
                    # Proxy dengan authentication (butuh extension)
                    plugin_file = self.create_proxy_extension()
                    if plugin_file:
                        options.add_extension(plugin_file)
                else:
                    # Proxy tanpa auth
                    proxy_type = getattr(config, 'PROXY_TYPE', 'http')
                    if proxy_type == 'auto':
                        proxy_type = 'http'
                    options.add_argument(f'--proxy-server={proxy_type}://{self.proxy_host}:{self.proxy_port}')
            
            # ========== ADGUARD (IMAGES CONTROL) ==========
            adguard_mode = getattr(config, 'ADGUARD_MODE', 'Dynamic')
            images_enabled = True
            
            if adguard_mode == 'Always OFF':
                images_enabled = True
            elif adguard_mode == 'Always ON':
                images_enabled = False
            
            if not images_enabled:
                prefs = {"profile.managed_default_content_settings.images": 2}
                options.add_experimental_option("prefs", prefs)
            
            # ========== FIX ERROR 193 - CHROMEDRIVER PATH ==========
            driver_path = os.path.join(os.getcwd(), "chromedriver.exe")
            
            if os.path.exists(driver_path):
                # Pakai manual ChromeDriver (RECOMMENDED!)
                logger.info(f"Worker {self.worker_id}: Using manual ChromeDriver")
                service = Service(driver_path)
                self.driver = webdriver.Chrome(service=service, options=options)
            else:
                # Fallback ke webdriver-manager
                logger.warning(f"Worker {self.worker_id}: ChromeDriver not found, using webdriver-manager...")
                
                try:
                    from webdriver_manager.chrome import ChromeDriverManager
                    service = Service(ChromeDriverManager().install())
                    self.driver = webdriver.Chrome(service=service, options=options)
                except Exception as e:
                    logger.error(f"Worker {self.worker_id}: Webdriver-manager failed - {e}")
                    logger.error("Download ChromeDriver: https://googlechromelabs.github.io/chrome-for-testing/")
                    return False
            
            # ========== INJECT ADVANCED STEALTH SCRIPTS ==========
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    // Hide webdriver
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    
                    // Add fake plugins
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });
                    
                    // Set languages
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-US', 'en']
                    });
                    
                    // Add chrome object
                    window.chrome = {
                        runtime: {},
                        loadTimes: function() {},
                        csi: function() {},
                        app: {}
                    };
                    
                    // Override permissions
                    const originalQuery = window.navigator.permissions.query;
                    window.navigator.permissions.query = (parameters) => (
                        parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                    );
                '''
            })
            
            # ========== APPLY SELENIUM-STEALTH ==========
            fp_mode = getattr(config, 'FINGERPRINT_MODE', 'Cortex')
            
            if fp_mode in ['Cortex', 'Pro']:
                try:
                    from selenium_stealth import stealth
                    stealth(self.driver,
                            languages=["en-US", "en"],
                            vendor="Google Inc.",
                            platform="Win32",
                            webgl_vendor="Intel Inc.",
                            renderer="Intel Iris OpenGL Engine",
                            fix_hairline=True)
                    logger.info(f"Worker {self.worker_id}: Stealth mode applied")
                except ImportError:
                    logger.warning(f"Worker {self.worker_id}: selenium-stealth not installed")
            
            # ========== WEBRTC PROTECTION ==========
            if getattr(config, 'WEBRTC_ENABLED', True):
                try:
                    self.driver.execute_cdp_cmd('Network.enable', {})
                    self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                        "userAgent": self.driver.execute_script("return navigator.userAgent")
                    })
                except:
                    pass
            
            # ========== TIMEZONE SYNC ==========
            if getattr(config, 'TIMEZONE_SYNC', True):
                try:
                    self.driver.execute_cdp_cmd('Emulation.setTimezoneOverride', {
                        'timezoneId': 'Asia/Jakarta'
                    })
                except:
                    pass
            
            self.is_running = True
            self.is_hidden = True
            
            logger.info(f"Worker {self.worker_id}: Browser setup successful!")
            return True
            
        except Exception as e:
            logger.error(f"Worker {self.worker_id}: Browser setup failed - {e}")
            return False
    
    def detect_captcha(self) -> bool:
        """
        Detect if captcha is present on current page
        
        Returns:
            True jika captcha terdeteksi
        """
        try:
            if not self.driver or not self.is_running:
                return False
            
            current_url = self.driver.current_url.lower()
            page_title = self.driver.title.lower()
            
            # ========== URL-BASED DETECTION ==========
            captcha_domains = [
                'appslime.com',
                'popzone',
                'captcha',
                'verify',
                'challenge',
                'protection',
                'cloudflare',
                'recaptcha',
                'hcaptcha',
                'funcaptcha'
            ]
            
            for domain in captcha_domains:
                if domain in current_url:
                    logger.warning(f"Worker {self.worker_id}: Captcha redirect detected ({domain})")
                    return True
            
            # ========== TITLE-BASED DETECTION ==========
            captcha_titles = [
                'captcha',
                'verification',
                'challenge',
                'just a moment',
                'checking your browser',
                'attention required'
            ]
            
            for title in captcha_titles:
                if title in page_title:
                    logger.warning(f"Worker {self.worker_id}: Captcha page title detected ({title})")
                    return True
            
            # ========== ELEMENT-BASED DETECTION ==========
            # Check for reCAPTCHA iframe
            recaptcha_frames = self.driver.find_elements(By.CSS_SELECTOR, "iframe[src*='recaptcha'], iframe[src*='google.com/recaptcha']")
            if recaptcha_frames:
                logger.warning(f"Worker {self.worker_id}: reCAPTCHA iframe detected")
                return True
            
            # Check for hCaptcha iframe
            hcaptcha_frames = self.driver.find_elements(By.CSS_SELECTOR, "iframe[src*='hcaptcha']")
            if hcaptcha_frames:
                logger.warning(f"Worker {self.worker_id}: hCaptcha iframe detected")
                return True
            
            # Check for Cloudflare challenge
            cloudflare_elements = self.driver.find_elements(By.CSS_SELECTOR, "#challenge-running, .challenge-running, #cf-wrapper")
            if cloudflare_elements:
                logger.warning(f"Worker {self.worker_id}: Cloudflare challenge detected")
                return True
            
            # ========== TEXT-BASED DETECTION ==========
            try:
                page_text = self.driver.page_source.lower()
                
                captcha_keywords = [
                    'i am not a robot',
                    'prove you are not a robot',
                    'verify you are human',
                    'complete the captcha',
                    'solve the puzzle',
                    'press and hold',
                    'click to verify',
                    'security check'
                ]
                
                for keyword in captcha_keywords:
                    if keyword in page_text:
                        logger.warning(f"Worker {self.worker_id}: Captcha text detected ({keyword})")
                        return True
            except:
                pass
            
            # No captcha detected
            return False
            
        except Exception as e:
            logger.debug(f"Worker {self.worker_id}: Captcha detection error - {e}")
            return False
    
    def human_scroll(self):
        """Scroll dengan behavior seperti manusia (WITH SAFETY CHECK)"""
        try:
            # Check if driver still valid
            if not self.driver or not self.is_running:
                return
            
            scroll_count = random.randint(
                getattr(config, 'SCROLL_MIN', 2),
                getattr(config, 'SCROLL_MAX', 5)
            )
            
            mouse_style = getattr(config, 'MOUSE_STYLE', 'Human Curves')
            
            for i in range(scroll_count):
                # Check setiap loop
                if not self.driver or not self.is_running:
                    break
                
                try:
                    if mouse_style == 'Human Curves':
                        # Smooth scroll dengan variasi
                        scroll_amount = random.randint(200, 600)
                        self.driver.execute_script(f"window.scrollBy({{top: {scroll_amount}, behavior: 'smooth'}});")
                        time.sleep(random.uniform(0.8, 2.5))
                    else:
                        # Direct jump
                        scroll_amount = random.randint(300, 800)
                        self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                        time.sleep(random.uniform(0.5, 1.5))
                    
                    # Random pause kadang-kadang
                    if random.random() < 0.3:
                        time.sleep(random.uniform(1, 3))
                except:
                    # Ignore error jika browser sudah close
                    break
            
            logger.debug(f"Worker {self.worker_id}: Scrolled {scroll_count} times")
            
        except Exception as e:
            # Don't log if just session closed
            if "invalid session id" not in str(e).lower() and "NoneType" not in str(e):
                logger.error(f"Worker {self.worker_id}: Scroll error - {e}")
    
    def simulate_reading(self):
        """Simulate reading dengan random delay"""
        try:
            if not self.driver or not self.is_running:
                return
            
            reading_time = random.uniform(
                getattr(config, 'DELAY_MIN', 5),
                getattr(config, 'DELAY_MAX', 15)
            )
            
            logger.debug(f"Worker {self.worker_id}: Reading for {reading_time:.1f}s")
            time.sleep(reading_time)
            
        except Exception as e:
            if "invalid session id" not in str(e).lower():
                logger.error(f"Worker {self.worker_id}: Reading simulation error - {e}")
    
    def execute_task(self, url: str, proxies: list = None) -> bool:
        """
        Execute single task dengan full human behavior + CAPTCHA DETECTION
        
        Args:
            url: Target URL
            proxies: List of available proxies
            
        Returns:
            True jika task berhasil
        """
        try:
            # Select proxy
            proxy = None
            if proxies and len(proxies) > 0:
                proxy = random.choice(proxies)
                logger.info(f"Worker {self.worker_id}: Selected proxy {proxy}")
            else:
                logger.info(f"Worker {self.worker_id}: Running without proxy")
            
            # Setup browser
            logger.info(f"Worker {self.worker_id}: Setting up browser...")
            if not self.setup_driver(proxy):
                return False
            
            # Visit URL
            logger.info(f"Worker {self.worker_id}: Visiting {url}")
            self.driver.get(url)
            
            # Wait for page load
            time.sleep(random.uniform(3, 5))
            
            # ========== CAPTCHA DETECTION CHECK ==========
            if self.detect_captcha():
                self.captcha_detected_count += 1
                logger.error(f"Worker {self.worker_id}: ⚠️ CAPTCHA DETECTED! Skipping task... (Total: {self.captcha_detected_count})")
                
                # Log URL that has captcha
                logger.error(f"Worker {self.worker_id}: Captcha URL: {self.driver.current_url}")
                
                # Mark as failed
                return False
            # ============================================
            
            # Log success - no captcha
            logger.info(f"Worker {self.worker_id}: ✓ No captcha detected, proceeding...")
            
            # Simulate reading
            self.simulate_reading()
            
            # Human-like scroll
            self.human_scroll()
            
            # Simulate CTR (click) berdasarkan target CTR
            target_ctr = getattr(config, 'TARGET_CTR', 8.0)
            if random.random() * 100 < target_ctr:
                try:
                    if not self.driver or not self.is_running:
                        return True
                    
                    # Try to find and click a link
                    links = self.driver.find_elements(By.TAG_NAME, "a")
                    if links:
                        clickable_links = [l for l in links if l.is_displayed()]
                        if clickable_links:
                            link = random.choice(clickable_links)
                            
                            # Scroll to element
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", link)
                            time.sleep(random.uniform(0.5, 1.5))
                            
                            # Click
                            link.click()
                            logger.info(f"Worker {self.worker_id}: Clicked a link (CTR simulation)")
                            time.sleep(random.uniform(2, 5))
                except:
                    pass
            
            # Random extra scroll
            if random.random() < 0.5:
                self.human_scroll()
            
            logger.success(f"Worker {self.worker_id}: Task completed successfully!")
            return True
            
        except Exception as e:
            # Don't log proxy connection errors (too verbose)
            if "ERR_PROXY_CONNECTION_FAILED" in str(e):
                logger.error(f"Worker {self.worker_id}: Proxy connection failed (proxy might be dead)")
            elif "invalid session id" not in str(e).lower():
                logger.error(f"Worker {self.worker_id}: Task failed - {e}")
            return False
        
        finally:
            # Cleanup
            self.stop()
    
    def stop(self):
        """Stop worker and cleanup"""
        self.is_running = False
        
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
        
        # Delete proxy extension file if exists
        if self.has_auth:
            try:
                plugin_file = f"proxy_auth_plugin_{self.worker_id}.zip"
                if os.path.exists(plugin_file):
                    os.remove(plugin_file)
            except:
                pass
