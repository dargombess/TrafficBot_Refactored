"""
Bot Worker - Individual Bot Instance V2.0
Advanced worker dengan AI enhancement, stealth technology, dan human behavior simulation
Total Lines: 1228+
"""

import time
import random
import os
import sys
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from urllib.parse import urlparse, urljoin
import threading
from queue import Queue
import re
import hashlib

# ==================== ADVANCED IMPORT SYSTEM ====================
# Setup comprehensive import system dengan fallback untuk semua dependencies
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grandparent_dir = os.path.dirname(parent_dir)

# Add semua possible paths untuk imports
for path in [current_dir, parent_dir, grandparent_dir]:
    if path not in sys.path:
        sys.path.insert(0, path)

print(f"🔧 [Worker] Initializing from: {current_dir}")
print(f"🔧 [Worker] Sys.path: {sys.path[:3]}...")

# ==================== LOGGER SETUP ====================
class AdvancedLogger:
    """Advanced logger dengan multiple handlers"""
    
    def __init__(self, worker_id: int):
        self.worker_id = worker_id
        self.logger = logging.getLogger(f"Worker_{worker_id}")
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s.%(msecs)03d - WORKER #%(worker_id)d - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler
        log_dir = os.path.join(parent_dir, 'logs', 'workers')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f'worker_{worker_id}.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Custom filter untuk worker ID
        old_factory = logging.getLogRecordFactory()
        
        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            record.worker_id = worker_id
            return record
        
        logging.setLogRecordFactory(record_factory)
    
    def info(self, msg):
        self.logger.info(msg)
    
    def warning(self, msg):
        self.logger.warning(msg)
    
    def error(self, msg):
        self.logger.error(msg)
    
    def debug(self, msg):
        self.logger.debug(msg)
    
    def critical(self, msg):
        self.logger.critical(msg)
    
    def success(self, msg):
        self.logger.info(f"✅ {msg}")
    
    def failure(self, msg):
        self.logger.error(f"❌ {msg}")

# ==================== CONFIG IMPORT ====================
try:
    from bot_config import config
    print("✅ [Worker] Config imported successfully")
    CONFIG_LOADED = True
except ImportError as e:
    print(f"❌ [Worker] Config import failed: {e}")
    # Create comprehensive fallback config
    class FallbackConfig:
        # Basic settings
        TASK_COUNT = 10
        MAX_WORKERS = 50
        
        # File paths
        FILE_ARTICLES = "artikel.txt"
        FILE_PROXIES = None
        USER_AGENT_FILE = os.path.join(parent_dir, 'data', 'user_agents.txt')
        
        # Behavior settings
        SHUFFLE_MODE = True
        MAX_URL_RETRIES = 3
        MIN_DELAY = 1.5
        MAX_DELAY = 4.0
        PAGE_READ_TIME_MIN = 15
        PAGE_READ_TIME_MAX = 45
        
        # Browser settings
        BROWSER_HEADLESS = False
        BROWSER_TYPE = "chrome"
        BROWSER_TIMEOUT = 30
        BROWSER_WINDOW_SIZE = "1920,1080"
        BROWSER_LANGUAGE = "en-US"
        CHROME_VERSION = "auto"
        CHROME_DRIVER_PATH = "auto"
        
        # AI settings
        AI_ENABLED = True
        AI_TRAINING_INTERVAL = 100
        AI_PREDICTION_ENABLED = True
        
        # Stealth settings
        RANDOM_USER_AGENT = True
        ENABLE_STEALTH = True
        FINGERPRINT_RANDOMIZATION = True
        CANVAS_FINGERPRINT_SPOOF = True
        WEBGL_FINGERPRINT_SPOOF = True
        AUDIO_CONTEXT_SPOOF = True
        RANDOM_TIMEZONE = True
        RANDOM_LOCALE = True
        FAKE_GEOLOCATION = True
        
        # Proxy settings
        USE_PROXY = False
        PROXY_TYPE = "http"
        PROXY_TIMEOUT = 10
        PROXY_MAX_RETRIES = 3
        PROXY_ROTATION_INTERVAL = 10
        
        # CAPTCHA settings
        CAPTCHA_SOLVER_ENABLED = False
        CAPTCHA_SERVICE = "2captcha"
        CAPTCHA_API_KEY = ""
        CAPTCHA_MAX_ATTEMPTS = 3
        
        # Performance settings
        MAX_MEMORY_USAGE = 512
        MAX_CPU_USAGE = 80
        AUTO_SCALING = True
        
        # Safety settings
        MAX_PAGES_PER_SESSION = 100
        MAX_SESSION_DURATION = 1800
        COOL_DOWN_PERIOD = 300
        ENABLE_BLACKLIST = True
        BLACKLIST_THRESHOLD = 5
        
        # Logging
        LOG_LEVEL = "INFO"
        LOG_TO_FILE = True
        LOG_TO_CONSOLE = True
        
        # Navigation behavior
        RANDOM_MOUSE_MOVEMENT = True
        RANDOM_SCROLLING = True
        CLICK_VARIATION = True
        DOUBLE_CLICK_CHANCE = 0.1
        RIGHT_CLICK_CHANCE = 0.05
        FILL_FORMS = False
        RANDOM_FORM_DATA = True
        SUBMIT_FORMS = False
    
    config = FallbackConfig()
    CONFIG_LOADED = False
    print("⚠️ [Worker] Using fallback config")

# ==================== DEPENDENCIES IMPORT ====================
# Selenium imports
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
    from selenium.webdriver.support.ui import WebDriverWait, Select
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.firefox.service import Service as FirefoxService
    from selenium.webdriver.edge.service import Service as EdgeService
    from selenium.common.exceptions import (
        TimeoutException, WebDriverException, NoSuchElementException,
        ElementNotInteractableException, ElementClickInterceptedException,
        StaleElementReferenceException, InvalidSelectorException,
        NoSuchWindowException, NoSuchFrameException, JavascriptException,
        SessionNotCreatedException, InvalidArgumentException,
        UnexpectedAlertPresentException, NoAlertPresentException
    )
    SELENIUM_AVAILABLE = True
    print("✅ [Worker] Selenium imported successfully")
except ImportError as e:
    SELENIUM_AVAILABLE = False
    print(f"❌ [Worker] Selenium import failed: {e}")

# Selenium stealth
try:
    from selenium_stealth import stealth
    STEALTH_AVAILABLE = True
    print("✅ [Worker] Selenium-stealth imported")
except ImportError:
    STEALTH_AVAILABLE = False
    print("⚠️ [Worker] Selenium-stealth not available")

# Webdriver manager
try:
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.firefox import GeckoDriverManager
    from webdriver_manager.microsoft import EdgeChromiumDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
    print("✅ [Worker] Webdriver-manager imported")
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False
    print("⚠️ [Worker] Webdriver-manager not available")

# Undetected chromedriver
try:
    import undetected_chromedriver as uc
    UNDETECTED_CHROMEDRIVER_AVAILABLE = True
    print("✅ [Worker] Undetected-chromedriver imported")
except ImportError:
    UNDETECTED_CHROMEDRIVER_AVAILABLE = False
    print("⚠️ [Worker] Undetected-chromedriver not available")

# AI Engine
try:
    from ai.intelligence_engine import ai_engine
    AI_AVAILABLE = True
    print("✅ [Worker] AI Engine imported")
except ImportError:
    AI_AVAILABLE = False
    print("⚠️ [Worker] AI Engine not available")

# Stealth modules
try:
    from stealth.behavior import HumanBehavior
    from stealth.browser import StealthBrowser
    from stealth.fingerprint import FingerprintManager
    STEALTH_MODULES_AVAILABLE = True
    print("✅ [Worker] Stealth modules imported")
except ImportError:
    STEALTH_MODULES_AVAILABLE = False
    print("⚠️ [Worker] Stealth modules not available")

# Utils
try:
    from utils.helpers import (
        read_file_lines, write_file_lines, load_json, save_json,
        generate_random_string, get_timestamp, format_duration, validate_url
    )
    UTILS_AVAILABLE = True
    print("✅ [Worker] Utils imported")
except ImportError:
    UTILS_AVAILABLE = False
    print("⚠️ [Worker] Utils not available")
    
    # Fallback utils
    def read_file_lines(file_path):
        if not os.path.exists(file_path):
            return []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        except:
            return []
    
    def validate_url(url):
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

# Additional dependencies
try:
    import psutil
    PSUTIL_AVAILABLE = True
    print("✅ [Worker] Psutil imported")
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️ [Worker] Psutil not available")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
    print("✅ [Worker] Numpy imported")
except ImportError:
    NUMPY_AVAILABLE = False
    print("⚠️ [Worker] Numpy not available")

try:
    from fake_useragent import UserAgent
    FAKE_USERAGENT_AVAILABLE = True
    print("✅ [Worker] Fake-useragent imported")
except ImportError:
    FAKE_USERAGENT_AVAILABLE = False
    print("⚠️ [Worker] Fake-useragent not available")

# ==================== HUMAN BEHAVIOR SIMULATION ====================
class AdvancedHumanBehavior:
    """Advanced human behavior simulation dengan AI enhancement"""
    
    def __init__(self, worker_id: int):
        self.worker_id = worker_id
        self.behavior_patterns = []
        self.last_actions = []
        self.mouse_trajectory = []
        self.scroll_patterns = []
        self.click_patterns = []
        self.reading_speed = random.uniform(200, 500)  # words per minute
        self.reaction_time = random.uniform(0.2, 0.8)  # seconds
        
        # Load behavior patterns dari AI jika available
        if AI_AVAILABLE:
            self._load_ai_patterns()
    
    def _load_ai_patterns(self):
        """Load behavior patterns dari AI engine"""
        try:
            if hasattr(ai_engine, 'get_behavior_patterns'):
                self.behavior_patterns = ai_engine.get_behavior_patterns()
        except:
            pass
    
    def generate_mouse_trajectory(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Generate human-like mouse trajectory"""
        trajectory = []
        x1, y1 = start_pos
        x2, y2 = end_pos
        
        # Human mouse movement is not straight
        num_points = random.randint(3, 8)
        for i in range(num_points):
            t = i / (num_points - 1) if num_points > 1 else 0
            # Bezier curve-like movement
            x = x1 + (x2 - x1) * t + random.randint(-10, 10)
            y = y1 + (y2 - y1) * t + random.randint(-10, 10)
            trajectory.append((int(x), int(y)))
        
        # Add some random jitter
        if random.random() > 0.7:
            trajectory.append((trajectory[-1][0] + random.randint(-5, 5), 
                             trajectory[-1][1] + random.randint(-5, 5)))
        
        return trajectory
    
    def simulate_scroll_behavior(self, driver, element=None):
        """Simulate human scrolling behavior"""
        try:
            scroll_actions = []
            
            # Random scroll patterns
            patterns = [
                self._scroll_smooth,      # Smooth scroll
                self._scroll_jerky,       # Jerky scroll (impatient)
                self._scroll_reading,     # Reading scroll
                self._scroll_searching,   # Searching scroll
            ]
            
            pattern = random.choice(patterns)
            scroll_actions = pattern(driver, element)
            
            self.scroll_patterns.append({
                'timestamp': time.time(),
                'pattern': pattern.__name__,
                'actions': len(scroll_actions)
            })
            
            # Keep only last 100 patterns
            if len(self.scroll_patterns) > 100:
                self.scroll_patterns.pop(0)
            
            return scroll_actions
            
        except Exception as e:
            print(f"[Behavior] Scroll simulation error: {e}")
            return []
    
    def _scroll_smooth(self, driver, element=None):
        """Smooth scrolling like careful reader"""
        actions = []
        total_scroll = random.randint(300, 1000)
        chunk_size = random.randint(50, 150)
        
        for i in range(0, total_scroll, chunk_size):
            driver.execute_script(f"window.scrollBy(0, {chunk_size})")
            actions.append(('scroll', chunk_size))
            time.sleep(random.uniform(0.1, 0.3))
        
        # Sometimes scroll back a bit
        if random.random() > 0.7:
            back_scroll = random.randint(50, 200)
            driver.execute_script(f"window.scrollBy(0, -{back_scroll})")
            actions.append(('scroll_back', back_scroll))
            time.sleep(random.uniform(0.2, 0.5))
        
        return actions
    
    def _scroll_jerky(self, driver, element=None):
        """Jerky scrolling like impatient user"""
        actions = []
        scrolls = random.randint(3, 8)
        
        for _ in range(scrolls):
            amount = random.randint(100, 400)
            direction = 1 if random.random() > 0.2 else -1
            driver.execute_script(f"window.scrollBy(0, {amount * direction})")
            actions.append(('jerk_scroll', amount * direction))
            time.sleep(random.uniform(0.05, 0.15))
        
        return actions
    
    def _scroll_reading(self, driver, element=None):
        """Reading-like scrolling with pauses"""
        actions = []
        sections = random.randint(2, 5)
        
        for section in range(sections):
            # Scroll to next section
            scroll_amount = random.randint(200, 500)
            driver.execute_script(f"window.scrollBy(0, {scroll_amount})")
            actions.append(('read_scroll', scroll_amount))
            
            # Pause for reading
            read_time = random.uniform(2.0, 8.0)
            time.sleep(read_time)
            actions.append(('read_pause', read_time))
            
            # Small adjustment scroll
            if random.random() > 0.5:
                adjust = random.randint(-50, 50)
                driver.execute_script(f"window.scrollBy(0, {adjust})")
                actions.append(('adjust', adjust))
        
        return actions
    
    def _scroll_searching(self, driver, element=None):
        """Searching-like scrolling (up and down)"""
        actions = []
        searches = random.randint(2, 4)
        
        for _ in range(searches):
            # Scroll down
            down = random.randint(300, 700)
            driver.execute_script(f"window.scrollBy(0, {down})")
            actions.append(('search_down', down))
            time.sleep(random.uniform(0.3, 0.8))
            
            # Scroll up a bit (like checking something)
            up = random.randint(-200, -50)
            driver.execute_script(f"window.scrollBy(0, {up})")
            actions.append(('search_up', up))
            time.sleep(random.uniform(0.2, 0.5))
        
        return actions
    
    def simulate_click_behavior(self, element, driver):
        """Simulate human-like click behavior"""
        try:
            click_type = self._determine_click_type()
            click_variation = self._add_click_variation()
            
            # Record click pattern
            self.click_patterns.append({
                'timestamp': time.time(),
                'type': click_type,
                'variation': click_variation,
                'element': element.tag_name if element else 'unknown'
            })
            
            # Keep only last 50 clicks
            if len(self.click_patterns) > 50:
                self.click_patterns.pop(0)
            
            # Execute click based on type
            if click_type == 'normal':
                self._normal_click(element, click_variation)
            elif click_type == 'double':
                self._double_click(element, click_variation)
            elif click_type == 'right':
                self._right_click(element, click_variation, driver)
            elif click_type == 'delayed':
                self._delayed_click(element, click_variation)
            
            # Random hover before/after click
            if random.random() > 0.3:
                time.sleep(random.uniform(0.1, 0.4))
            
            return True
            
        except Exception as e:
            print(f"[Behavior] Click simulation error: {e}")
            return False
    
    def _determine_click_type(self):
        """Determine type of click based on probabilities"""
        rand = random.random()
        if rand < getattr(config, 'RIGHT_CLICK_CHANCE', 0.05):
            return 'right'
        elif rand < getattr(config, 'DOUBLE_CLICK_CHANCE', 0.1) + getattr(config, 'RIGHT_CLICK_CHANCE', 0.05):
            return 'double'
        elif rand < 0.15:  # 15% chance for delayed click
            return 'delayed'
        else:
            return 'normal'
    
    def _add_click_variation(self):
        """Add random variation to click position"""
        if not getattr(config, 'CLICK_VARIATION', True):
            return {'x_offset': 0, 'y_offset': 0}
        
        return {
            'x_offset': random.randint(-3, 3),
            'y_offset': random.randint(-3, 3)
        }
    
    def _normal_click(self, element, variation):
        """Simulate normal click with possible miss"""
        try:
            # Sometimes miss slightly
            if random.random() > 0.8:  # 20% chance to miss
                offset_x = random.randint(-10, 10)
                offset_y = random.randint(-10, 10)
                actions = ActionChains(element.parent)
                actions.move_to_element_with_offset(element, offset_x, offset_y)
                actions.click()
                actions.perform()
            else:
                element.click()
            
            # Random delay after click
            time.sleep(random.uniform(0.1, 0.3))
            
        except:
            element.click()
    
    def _double_click(self, element, variation):
        """Simulate double click"""
        try:
            actions = ActionChains(element.parent)
            actions.double_click(element)
            actions.perform()
            
            # Variation in double click speed
            time.sleep(random.uniform(0.05, 0.15))
            
        except:
            element.click()
            time.sleep(0.1)
            element.click()
    
    def _right_click(self, element, variation, driver):
        """Simulate right click"""
        try:
            actions = ActionChains(driver)
            actions.context_click(element)
            actions.perform()
            
            # Usually close context menu with escape
            time.sleep(random.uniform(0.2, 0.5))
            actions.send_keys(Keys.ESCAPE)
            actions.perform()
            
        except:
            pass
    
    def _delayed_click(self, element, variation):
        """Simulate delayed click (hesitation)"""
        # Hover first
        time.sleep(random.uniform(0.3, 0.8))
        
        # Click
        element.click()
        
        # Post-click hesitation
        time.sleep(random.uniform(0.1, 0.4))
    
    def simulate_reading_behavior(self, content_length: int) -> float:
        """Simulate human reading time based on content length"""
        # Calculate reading time in seconds
        words = content_length / 5  # Approximate words
        base_time = (words / self.reading_speed) * 60
        
        # Add human variation
        variation = random.uniform(0.7, 1.3)  # 70-130% of base time
        total_time = base_time * variation
        
        # Ensure within config bounds
        min_time = getattr(config, 'PAGE_READ_TIME_MIN', 10)
        max_time = getattr(config, 'PAGE_READ_TIME_MAX', 30)
        
        return max(min_time, min(total_time, max_time))
    
    def simulate_typing_behavior(self, text: str, element):
        """Simulate human typing with errors and corrections"""
        try:
            # Clear field first
            element.clear()
            time.sleep(random.uniform(0.1, 0.3))
            
            # Type character by character with variations
            for i, char in enumerate(text):
                # Random typing speed
                delay = random.uniform(0.05, 0.2)
                
                # Occasionally make a mistake (5% chance)
                if random.random() < 0.05 and i > 0:
                    # Type wrong character
                    wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                    element.send_keys(wrong_char)
                    time.sleep(delay)
                    
                    # Backspace
                    element.send_keys(Keys.BACKSPACE)
                    time.sleep(random.uniform(0.1, 0.3))
                
                # Type correct character
                element.send_keys(char)
                time.sleep(delay)
                
                # Occasionally pause (10% chance)
                if random.random() < 0.1:
                    pause = random.uniform(0.3, 1.0)
                    time.sleep(pause)
            
            # Sometimes hesitate before submitting
            if random.random() < 0.3:
                time.sleep(random.uniform(0.5, 1.5))
            
        except Exception as e:
            # Fallback: type normally
            element.send_keys(text)

# ==================== ADVANCED BROWSER MANAGER ====================
class AdvancedBrowserManager:
    """Manage browser instances dengan advanced features"""
    
    def __init__(self, worker_id: int):
        self.worker_id = worker_id
        self.driver = None
        self.options = None
        self.capabilities = None
        self.profile = None
        self.extensions = []
        self.user_data_dir = None
        self.fingerprint = None
        
        # Performance tracking
        self.start_time = None
        self.memory_usage = []
        self.cpu_usage = []
        
        # Load stealth modules jika available
        if STEALTH_MODULES_AVAILABLE:
            self.stealth_browser = StealthBrowser(worker_id)
            self.fingerprint_manager = FingerprintManager()
        else:
            self.stealth_browser = None
            self.fingerprint_manager = None
    
    def create_chrome_options(self, proxy: Optional[str] = None) -> Any:
        """Create advanced Chrome options dengan semua stealth features"""
        if not SELENIUM_AVAILABLE:
            return None
        
        try:
            options = webdriver.ChromeOptions()
            
            # ========== BASIC OPTIONS ==========
            if getattr(config, 'BROWSER_HEADLESS', False):
                options.add_argument('--headless=new')  # New headless mode
            
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-web-security')
            options.add_argument('--allow-running-insecure-content')
            options.add_argument('--disable-features=IsolateOrigins,site-per-process')
            options.add_argument('--disable-site-isolation-trials')
            
            # ========== WINDOW & DISPLAY ==========
            window_size = getattr(config, 'BROWSER_WINDOW_SIZE', '1920,1080')
            options.add_argument(f'--window-size={window_size}')
            
            # Random window position
            if random.random() > 0.5:
                pos_x = random.randint(0, 100)
                pos_y = random.randint(0, 100)
                options.add_argument(f'--window-position={pos_x},{pos_y}')
            
            # ========== LANGUAGE & LOCALE ==========
            if getattr(config, 'RANDOM_LOCALE', True):
                locales = ['en-US', 'en-GB', 'en-AU', 'en-CA', 'en-NZ']
                locale = random.choice(locales)
            else:
                locale = getattr(config, 'BROWSER_LANGUAGE', 'en-US')
            
            options.add_argument(f'--lang={locale}')
            
            # ========== USER AGENT ==========
            if getattr(config, 'RANDOM_USER_AGENT', True):
                user_agent = self._get_random_user_agent()
                options.add_argument(f'user-agent={user_agent}')
            
            # ========== PROXY SETTINGS ==========
            if proxy and getattr(config, 'USE_PROXY', False):
                proxy_type = getattr(config, 'PROXY_TYPE', 'http')
                if proxy_type == 'socks5':
                    options.add_argument(f'--proxy-server=socks5://{proxy}')
                elif proxy_type == 'socks4':
                    options.add_argument(f'--proxy-server=socks4://{proxy}')
                else:
                    options.add_argument(f'--proxy-server=http://{proxy}')
                
                # Proxy authentication jika diperlukan
                if ':' in proxy and '@' in proxy:
                    # Format: username:password@host:port
                    pass
            
            # ========== STEALTH ARGUMENTS ==========
            options.add_argument('--disable-browser-side-navigation')
            options.add_argument('--disable-client-side-phishing-detection')
            options.add_argument('--disable-component-update')
            options.add_argument('--disable-default-apps')
            options.add_argument('--disable-popup-blocking')
            options.add_argument('--disable-translate')
            
            # Disable automation flags
            options.add_experimental_option("excludeSwitches", [
                "enable-automation",
                "enable-logging",
                "disable-background-networking",
                "disable-component-update",
                "disable-sync"
            ])
            
            options.add_experimental_option('useAutomationExtension', False)
            
            # ========== PREFERENCES ==========
            prefs = {
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_setting_values.geolocation": 2,
                "profile.default_content_setting_values.media_stream": 2,
                "profile.default_content_setting_values.camera": 2,
                "profile.default_content_setting_values.microphone": 2,
                "profile.managed_default_content_settings.images": 1,
                "profile.managed_default_content_settings.javascript": 1,
                "profile.managed_default_content_settings.plugins": 1,
                "profile.managed_default_content_settings.popups": 2,
                "download.default_directory": os.path.join(os.getcwd(), 'downloads'),
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True,
                "safebrowsing.disable_download_protection": True,
            }
            
            options.add_experimental_option("prefs", prefs)
            
            # ========== CAPABILITIES ==========
            caps = options.to_capabilities()
            
            # Modify capabilities untuk stealth
            caps['goog:chromeOptions']['args'].append('--disable-blink-features=AutomationControlled')
            
            # Add timezone jika random
            if getattr(config, 'RANDOM_TIMEZONE', True):
                timezones = ['America/New_York', 'Europe/London', 'Asia/Tokyo', 'Australia/Sydney']
                caps['goog:chromeOptions']['prefs']['intl.accept_languages'] = locale
                # Timezone would be set via CDP commands later
            
            self.options = options
            self.capabilities = caps
            
            return options
            
        except Exception as e:
            print(f"[BrowserManager] Error creating options: {e}")
            return None
    
    def _get_random_user_agent(self) -> str:
        """Get random user agent dari berbagai sources"""
        try:
            # Try fake-useragent first
            if FAKE_USERAGENT_AVAILABLE:
                ua = UserAgent()
                return ua.random
            
            # Try from file
            ua_file = getattr(config, 'USER_AGENT_FILE', '')
            if ua_file and os.path.exists(ua_file):
                agents = read_file_lines(ua_file)
                if agents:
                    return random.choice(agents)
            
            # Fallback to hardcoded agents
            agents = [
                # Chrome Windows
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                # Firefox Windows
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
                # Chrome Mac
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                # Safari Mac
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
                # Chrome Linux
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            ]
            
            return random.choice(agents)
            
        except Exception as e:
            print(f"[BrowserManager] Error getting user agent: {e}")
            return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    
    def setup_driver(self, proxy: Optional[str] = None) -> bool:
        """Setup browser driver dengan semua features"""
        try:
            print(f"[BrowserManager #{self.worker_id}] Setting up driver...")
            
            # Create options
            options = self.create_chrome_options(proxy)
            if not options:
                print(f"[BrowserManager #{self.worker_id}] Failed to create options")
                return False
            
            # Choose driver type based on availability and config
            driver = None
            
            # Priority 1: Undetected chromedriver (best for stealth)
            if UNDETECTED_CHROMEDRIVER_AVAILABLE and getattr(config, 'ENABLE_STEALTH', True):
                try:
                    print(f"[BrowserManager #{self.worker_id}] Using undetected-chromedriver")
                    
                    uc_options = uc.ChromeOptions()
                    for arg in options.arguments:
                        uc_options.add_argument(arg)
                    
                    driver = uc.Chrome(
                        options=uc_options,
                        version_main=getattr(config, 'CHROME_VERSION', 'auto'),
                        driver_executable_path=getattr(config, 'CHROME_DRIVER_PATH', None),
                        headless=getattr(config, 'BROWSER_HEADLESS', False)
                    )
                    
                except Exception as e:
                    print(f"[BrowserManager #{self.worker_id}] Undetected-chromedriver failed: {e}")
                    driver = None
            
            # Priority 2: Webdriver-manager
            if driver is None and WEBDRIVER_MANAGER_AVAILABLE:
                try:
                    print(f"[BrowserManager #{self.worker_id}] Using webdriver-manager")
                    
                    service = ChromeService(ChromeDriverManager().install())
                    driver = webdriver.Chrome(service=service, options=options)
                    
                except Exception as e:
                    print(f"[BrowserManager #{self.worker_id}] Webdriver-manager failed: {e}")
                    driver = None
            
            # Priority 3: Default Chrome
            if driver is None and SELENIUM_AVAILABLE:
                try:
                    print(f"[BrowserManager #{self.worker_id}] Using default Chrome")
                    driver = webdriver.Chrome(options=options)
                except Exception as e:
                    print(f"[BrowserManager #{self.worker_id}] Default Chrome failed: {e}")
                    return False
            
            if not driver:
                print(f"[BrowserManager #{self.worker_id}] No driver available")
                return False
            
            self.driver = driver
            self.start_time = time.time()
            
            # Apply additional stealth jika available
            self._apply_stealth_techniques()
            
            # Apply fingerprint jika available
            self._apply_fingerprint()
            
            # Set window position dan size
            self._configure_window()
            
            print(f"[BrowserManager #{self.worker_id}] Driver setup complete")
            return True
            
        except Exception as e:
            print(f"[BrowserManager #{self.worker_id}] Setup failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _apply_stealth_techniques(self):
        """Apply berbagai stealth techniques ke browser"""
        if not self.driver:
            return
        
        try:
            # Selenium-stealth
            if STEALTH_AVAILABLE and getattr(config, 'ENABLE_STEALTH', True):
                stealth(self.driver,
                    languages=["en-US", "en"],
                    vendor="Google Inc.",
                    platform="Win32",
                    webgl_vendor="Intel Inc.",
                    renderer="Intel Iris OpenGL Engine",
                    fix_hairline=True,
                )
            
            # Custom stealth scripts
            self._execute_stealth_scripts()
            
            # Modify navigator properties
            self._modify_navigator_properties()
            
            # Modify screen properties
            self._modify_screen_properties()
            
            # Modify timezone
            self._modify_timezone()
            
            # Modify geolocation
            self._modify_geolocation()
            
            # Canvas fingerprint spoofing
            if getattr(config, 'CANVAS_FINGERPRINT_SPOOF', True):
                self._spoof_canvas_fingerprint()
            
            # WebGL fingerprint spoofing
            if getattr(config, 'WEBGL_FINGERPRINT_SPOOF', True):
                self._spoof_webgl_fingerprint()
            
            # AudioContext fingerprint spoofing
            if getattr(config, 'AUDIO_CONTEXT_SPOOF', True):
                self._spoof_audiocontext_fingerprint()
            
        except Exception as e:
            print(f"[BrowserManager] Stealth application error: {e}")
    
    def _execute_stealth_scripts(self):
        """Execute JavaScript untuk stealth"""
        scripts = [
            # Hide webdriver property
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})",
            
            # Modify chrome property
            "window.chrome = {runtime: {}}",
            
            # Modify permissions
            "const originalQuery = window.navigator.permissions.query;"
            "window.navigator.permissions.query = (parameters) => ("
            "    parameters.name === 'notifications' ?"
            "        Promise.resolve({ state: Notification.permission }) :"
            "        originalQuery(parameters)"
            ");",
            
            # Override plugins
            "Object.defineProperty(navigator, 'plugins', {"
            "    get: () => [1, 2, 3, 4, 5],"
            "});",
            
            # Override languages
            "Object.defineProperty(navigator, 'languages', {"
            "    get: () => ['en-US', 'en'],"
            "});",
        ]
        
        for script in scripts:
            try:
                self.driver.execute_script(script)
            except:
                pass
    
    def _modify_navigator_properties(self):
        """Modify navigator properties via CDP"""
        try:
            # Execute via CDP
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": self._get_random_user_agent(),
                "platform": "Windows",
                "userAgentMetadata": {
                    "brands": [
                        {"brand": "Chromium", "version": "120"},
                        {"brand": "Google Chrome", "version": "120"},
                        {"brand": "Not-A.Brand", "version": "99"}
                    ],
                    "fullVersion": "120.0.0.0",
                    "platform": "Windows",
                    "platformVersion": "10.0.0",
                    "architecture": "x86",
                    "model": "",
                    "mobile": False,
                    "bitness": "64"
                }
            })
        except:
            pass
    
    def _modify_screen_properties(self):
        """Modify screen properties"""
        try:
            screen_script = """
            Object.defineProperty(screen, 'width', {get: () => 1920});
            Object.defineProperty(screen, 'height', {get: () => 1080});
            Object.defineProperty(screen, 'availWidth', {get: () => 1920});
            Object.defineProperty(screen, 'availHeight', {get: () => 1040});
            Object.defineProperty(screen, 'colorDepth', {get: () => 24});
            Object.defineProperty(screen, 'pixelDepth', {get: () => 24});
            """
            self.driver.execute_script(screen_script)
        except:
            pass
    
    def _modify_timezone(self):
        """Modify timezone"""
        if getattr(config, 'RANDOM_TIMEZONE', True):
            try:
                timezones = [
                    'America/New_York', 'Europe/London', 'Asia/Tokyo',
                    'Australia/Sydney', 'Europe/Paris', 'Asia/Singapore'
                ]
                timezone = random.choice(timezones)
                
                self.driver.execute_cdp_cmd('Emulation.setTimezoneOverride', {
                    'timezoneId': timezone
                })
            except:
                pass
    
    def _modify_geolocation(self):
        """Modify geolocation"""
        if getattr(config, 'FAKE_GEOLOCATION', True):
            try:
                locations = [
                    {"latitude": 40.7128, "longitude": -74.0060, "accuracy": 100},  # NYC
                    {"latitude": 51.5074, "longitude": -0.1278, "accuracy": 100},  # London
                    {"latitude": 35.6762, "longitude": 139.6503, "accuracy": 100},  # Tokyo
                    {"latitude": -33.8688, "longitude": 151.2093, "accuracy": 100},  # Sydney
                ]
                location = random.choice(locations)
                
                self.driver.execute_cdp_cmd('Emulation.setGeolocationOverride', location)
            except:
                pass
    
    def _spoof_canvas_fingerprint(self):
        """Spoof canvas fingerprint"""
        try:
            canvas_script = """
            const originalGetContext = HTMLCanvasElement.prototype.getContext;
            HTMLCanvasElement.prototype.getContext = function(contextType, contextAttributes) {
                if (contextType === '2d') {
                    const context = originalGetContext.call(this, contextType, contextAttributes);
                    
                    // Override toDataURL
                    const originalToDataURL = context.canvas.toDataURL;
                    context.canvas.toDataURL = function(type, quality) {
                        if (type === 'image/png') {
                            return 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==';
                        }
                        return originalToDataURL.call(this, type, quality);
                    };
                    
                    // Override getImageData
                    const originalGetImageData = context.getImageData;
                    context.getImageData = function(sx, sy, sw, sh) {
                        const imageData = originalGetImageData.call(this, sx, sy, sw, sh);
                        // Add slight random noise
                        for (let i = 0; i < imageData.data.length; i += 4) {
                            imageData.data[i] += Math.floor(Math.random() * 3) - 1;
                        }
                        return imageData;
                    };
                    
                    return context;
                }
                return originalGetContext.call(this, contextType, contextAttributes);
            };
            """
            self.driver.execute_script(canvas_script)
        except:
            pass
    
    def _spoof_webgl_fingerprint(self):
        """Spoof WebGL fingerprint"""
        try:
            webgl_script = """
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) {
                    return 'Intel Inc.';
                }
                if (parameter === 37446) {
                    return 'Intel Iris OpenGL Engine';
                }
                return getParameter.call(this, parameter);
            };
            
            const getExtension = WebGLRenderingContext.prototype.getExtension;
            WebGLRenderingContext.prototype.getExtension = function(name) {
                if (name === 'WEBGL_debug_renderer_info') {
                    return null;
                }
                return getExtension.call(this, name);
            };
            """
            self.driver.execute_script(webgl_script)
        except:
            pass
    
    def _spoof_audiocontext_fingerprint(self):
        """Spoof AudioContext fingerprint"""
        try:
            audio_script = """
            if (window.AudioContext) {
                const originalCreateOscillator = AudioContext.prototype.createOscillator;
                AudioContext.prototype.createOscillator = function() {
                    const oscillator = originalCreateOscillator.call(this);
                    const originalFrequency = oscillator.frequency;
                    Object.defineProperty(oscillator.frequency, 'value', {
                        get: function() {
                            return originalFrequency.value + (Math.random() * 0.1 - 0.05);
                        }
                    });
                    return oscillator;
                };
            }
            """
            self.driver.execute_script(audio_script)
        except:
            pass
    
    def _configure_window(self):
        """Configure window position and size"""
        if not self.driver:
            return
        
        try:
            # Set window size
            size = getattr(config, 'BROWSER_WINDOW_SIZE', '1920,1080')
            width, height = map(int, size.split(','))
            self.driver.set_window_size(width, height)
            
            # Random window position
            if random.random() > 0.5:
                max_x = 100
                max_y = 100
                x = random.randint(0, max_x)
                y = random.randint(0, max_y)
                self.driver.set_window_position(x, y)
            
            # Maximize jika tidak headless
            if not getattr(config, 'BROWSER_HEADLESS', False) and random.random() > 0.7:
                self.driver.maximize_window()
                
        except Exception as e:
            print(f"[BrowserManager] Window configuration error: {e}")
    
    def _apply_fingerprint(self):
        """Apply fingerprint jika fingerprint manager available"""
        if self.fingerprint_manager:
            try:
                self.fingerprint = self.fingerprint_manager.generate_fingerprint()
                self.fingerprint_manager.apply_fingerprint(self.driver, self.fingerprint)
            except Exception as e:
                print(f"[BrowserManager] Fingerprint error: {e}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get browser performance metrics"""
        metrics = {
            'uptime': time.time() - self.start_time if self.start_time else 0,
            'memory_samples': len(self.memory_usage),
            'cpu_samples': len(self.cpu_usage),
            'avg_memory': np.mean(self.memory_usage) if self.memory_usage and NUMPY_AVAILABLE else 0,
            'avg_cpu': np.mean(self.cpu_usage) if self.cpu_usage and NUMPY_AVAILABLE else 0,
        }
        
        # Update current metrics
        if PSUTIL_AVAILABLE:
            try:
                process = psutil.Process(os.getpid())
                self.memory_usage.append(process.memory_info().rss / 1024 / 1024)  # MB
                self.cpu_usage.append(process.cpu_percent())
                
                # Keep only last 100 samples
                if len(self.memory_usage) > 100:
                    self.memory_usage.pop(0)
                if len(self.cpu_usage) > 100:
                    self.cpu_usage.pop(0)
                    
            except:
                pass
        
        return metrics
    
    def cleanup(self):
        """Cleanup browser resources"""
        if self.driver:
            try:
                # Try to close all windows
                for handle in self.driver.window_handles:
                    try:
                        self.driver.switch_to.window(handle)
                        self.driver.close()
                    except:
                        pass
                
                # Quit driver
                self.driver.quit()
                
            except Exception as e:
                print(f"[BrowserManager] Cleanup error: {e}")
            
            finally:
                self.driver = None
        
        # Clear metrics
        self.memory_usage.clear()
        self.cpu_usage.clear()

# ==================== CAPTCHA SOLVER ====================
class CaptchaSolver:
    """Handle CAPTCHA solving dengan berbagai methods"""
    
    def __init__(self, worker_id: int):
        self.worker_id = worker_id
        self.api_key = getattr(config, 'CAPTCHA_API_KEY', '')
        self.service = getattr(config, 'CAPTCHA_SERVICE', '2captcha')
        self.max_attempts = getattr(config, 'CAPTCHA_MAX_ATTEMPTS', 3)
        self.enabled = getattr(config, 'CAPTCHA_SOLVER_ENABLED', False)
        
        # CAPTCHA detection patterns
        self.captcha_patterns = [
            'recaptcha', 'captcha', 'cloudflare', 'hcaptcha',
            'security check', 'robot check', 'human verification',
            'verify you are human', 'i am not a robot'
        ]
        
        # Solver instances
        self.solver = None
        self._init_solver()
    
    def _init_solver(self):
        """Initialize CAPTCHA solver berdasarkan service"""
        if not self.enabled or not self.api_key:
            return
        
        try:
            if self.service.lower() == '2captcha':
                from python_anticaptcha import AnticaptchaClient, NoCaptchaTaskProxylessTask
                self.solver = AnticaptchaClient(self.api_key)
            elif self.service.lower() == 'anticaptcha':
                from anticaptchaofficial.recaptchav2proxyless import recaptchaV2Proxyless
                self.solver = recaptchaV2Proxyless()
                self.solver.set_key(self.api_key)
            elif self.service.lower() == 'capmonster':
                from capmonster_python import RecaptchaV2Task
                self.solver = RecaptchaV2Task(self.api_key)
        except ImportError:
            print(f"[CaptchaSolver #{self.worker_id}] CAPTCHA service not available")
            self.solver = None
    
    def detect_captcha(self, driver) -> Tuple[bool, str]:
        """Detect jika page memiliki CAPTCHA"""
        if not driver:
            return False, ""
        
        try:
            # Check page source
            page_source = driver.page_source.lower()
            
            for pattern in self.captcha_patterns:
                if pattern in page_source:
                    return True, pattern
            
            # Check for reCAPTCHA iframe
            recaptcha_iframes = driver.find_elements(By.XPATH, 
                "//iframe[contains(@src, 'recaptcha') or contains(@src, 'google.com/recaptcha')]")
            if recaptcha_iframes:
                return True, "recaptcha_iframe"
            
            # Check for hCaptcha
            hcaptcha_elements = driver.find_elements(By.XPATH,
                "//div[contains(@class, 'h-captcha')]")
            if hcaptcha_elements:
                return True, "hcaptcha"
            
            # Check Cloudflare
            title = driver.title.lower()
            if 'cloudflare' in title or 'checking your browser' in page_source:
                return True, "cloudflare"
            
            return False, ""
            
        except Exception as e:
            print(f"[CaptchaSolver] Detection error: {e}")
            return False, ""
    
    def solve_recaptcha(self, driver, site_key: str, page_url: str) -> Optional[str]:
        """Solve reCAPTCHA v2"""
        if not self.solver or not self.enabled:
            return None
        
        try:
            print(f"[CaptchaSolver #{self.worker_id}] Solving reCAPTCHA...")
            
            if isinstance(self.solver, AnticaptchaClient):  # 2captcha
                task = NoCaptchaTaskProxylessTask(page_url, site_key)
                job = self.solver.createTask(task)
                job.join()
                return job.get_solution_response()
            
            elif hasattr(self.solver, 'create_task'):  # anticaptcha
                self.solver.set_website_url(page_url)
                self.solver.set_website_key(site_key)
                task_id = self.solver.create_task()
                if task_id != 0:
                    time.sleep(10)  # Wait for solving
                    result = self.solver.get_task_result(task_id)
                    if result.get('status') == 'ready':
                        return result.get('solution', {}).get('gRecaptchaResponse')
            
            return None
            
        except Exception as e:
            print(f"[CaptchaSolver] Solving error: {e}")
            return None
    
    def bypass_cloudflare(self, driver) -> bool:
        """Attempt to bypass Cloudflare protection"""
        try:
            print(f"[CaptchaSolver #{self.worker_id}] Bypassing Cloudflare...")
            
            # Method 1: Wait and retry
            time.sleep(5)
            driver.refresh()
            time.sleep(3)
            
            # Method 2: Change user agent via JavaScript
            user_agent = self._get_random_user_agent()
            driver.execute_script(
                "Object.defineProperty(navigator, 'userAgent', {"
                f"get: function () {{ return '{user_agent}'; }}"
                "});"
            )
            
            # Method 3: Clear cookies and retry
            driver.delete_all_cookies()
            time.sleep(2)
            driver.refresh()
            time.sleep(3)
            
            # Check if bypassed
            page_source = driver.page_source.lower()
            if 'checking your browser' not in page_source:
                print(f"[CaptchaSolver #{self.worker_id}] Cloudflare bypassed")
                return True
            
            return False
            
        except Exception as e:
            print(f"[CaptchaSolver] Cloudflare bypass error: {e}")
            return False
    
    def _get_random_user_agent(self) -> str:
        """Get random user agent"""
        agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
        ]
        return random.choice(agents)
    
    def handle_captcha_page(self, driver) -> bool:
        """Handle CAPTCHA page dengan berbagai methods"""
        if not driver:
            return False
        
        print(f"[CaptchaSolver #{self.worker_id}] Handling CAPTCHA page...")
        
        # Try multiple bypass methods
        methods = [
            self._method_wait_refresh,
            self._method_js_bypass,
            self._method_cookie_clear,
            self._method_user_agent_rotate,
            self._method_proxy_rotate,
        ]
        
        for attempt in range(self.max_attempts):
            print(f"[CaptchaSolver #{self.worker_id}] Attempt {attempt + 1}/{self.max_attempts}")
            
            for method in methods:
                try:
                    if method(driver):
                        print(f"[CaptchaSolver #{self.worker_id}] CAPTCHA bypassed with {method.__name__}")
                        return True
                except Exception as e:
                    print(f"[CaptchaSolver] Method {method.__name__} failed: {e}")
            
            time.sleep(2)
        
        print(f"[CaptchaSolver #{self.worker_id}] All CAPTCHA bypass methods failed")
        return False
    
    def _method_wait_refresh(self, driver) -> bool:
        """Method 1: Wait and refresh"""
        time.sleep(random.uniform(3, 8))
        driver.refresh()
        time.sleep(2)
        return not self.detect_captcha(driver)[0]
    
    def _method_js_bypass(self, driver) -> bool:
        """Method 2: JavaScript bypass"""
        bypass_scripts = [
            # Remove CAPTCHA elements
            "document.querySelectorAll('[class*=\"captcha\"], [id*=\"captcha\"]').forEach(el => el.remove());",
            # Modify page to hide CAPTCHA
            "document.body.style.overflow = 'auto'; document.documentElement.style.overflow = 'auto';",
            # Trigger page load completion
            "window.dispatchEvent(new Event('load'));",
        ]
        
        for script in bypass_scripts:
            try:
                driver.execute_script(script)
                time.sleep(1)
            except:
                pass
        
        time.sleep(2)
        return not self.detect_captcha(driver)[0]
    
    def _method_cookie_clear(self, driver) -> bool:
        """Method 3: Clear cookies"""
        driver.delete_all_cookies()
        time.sleep(1)
        driver.refresh()
        time.sleep(3)
        return not self.detect_captcha(driver)[0]
    
    def _method_user_agent_rotate(self, driver) -> bool:
        """Method 4: Rotate user agent"""
        user_agent = self._get_random_user_agent()
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": user_agent
        })
        time.sleep(1)
        driver.refresh()
        time.sleep(3)
        return not self.detect_captcha(driver)[0]
    
    def _method_proxy_rotate(self, driver) -> bool:
        """Method 5: Proxy rotation (requires proxy setup)"""
        # This would require re-initializing driver with different proxy
        # For now, just refresh
        driver.refresh()
        time.sleep(3)
        return not self.detect_captcha(driver)[0]

# ==================== MAIN BOT WORKER CLASS ====================
class BotWorker:
    """
    Advanced Bot Worker dengan semua features:
    - AI-enhanced behavior
    - Advanced stealth
    - CAPTCHA solving
    - Human simulation
    - Performance monitoring
    """
    
    def __init__(self, worker_id: int):
        """Initialize advanced bot worker"""
        self.worker_id = worker_id
        
        # Core components
        self.logger = AdvancedLogger(worker_id)
        self.browser_manager = AdvancedBrowserManager(worker_id)
        self.behavior_simulator = AdvancedHumanBehavior(worker_id)
        self.captcha_solver = CaptchaSolver(worker_id)
        
        # State
        self.driver = None
        self.is_hidden = False
        self.current_url = None
        self.current_proxy = None
        self.is_running = False
        self.start_time = None
        
        # Statistics
        self.session_stats = {
            'pages_visited': 0,
            'successful_visits': 0,
            'failed_visits': 0,
            'total_time': 0,
            'captcha_encounters': 0,
            'captcha_solved': 0,
            'avg_page_time': 0,
            'errors': []
        }
        
        # AI integration
        self.ai_engine = ai_engine if AI_AVAILABLE else None
        self.prediction_model = None
        
        # Performance monitoring
        self.performance_stats = {
            'memory_peak': 0,
            'cpu_peak': 0,
            'network_requests': 0,
            'dom_elements': 0
        }
        
        # Load AI model jika available
        if self.ai_engine:
            self._load_ai_model()
        
        self.logger.success(f"Worker {worker_id} initialized with all features")
        print(f"\n{'='*60}")
        print(f"🤖 WORKER #{worker_id} - ADVANCED EDITION")
        print(f"{'='*60}")
        print(f"✓ AI Engine: {'ENABLED' if AI_AVAILABLE else 'DISABLED'}")
        print(f"✓ Stealth: {'ENABLED' if STEALTH_AVAILABLE else 'DISABLED'}")
        print(f"✓ CAPTCHA Solver: {'ENABLED' if self.captcha_solver.enabled else 'DISABLED'}")
        print(f"✓ Human Behavior: ENABLED")
        print(f"✓ Performance Monitor: ENABLED")
        print(f"{'='*60}\n")
    
    def _load_ai_model(self):
        """Load AI prediction model"""
        try:
            if hasattr(self.ai_engine, 'load_prediction_model'):
                self.prediction_model = self.ai_engine.load_prediction_model('behavior')
                self.logger.info(f"AI prediction model loaded")
        except Exception as e:
            self.logger.error(f"Failed to load AI model: {e}")
    
    def _get_page_quality_score(self, driver) -> float:
        """Calculate page quality score menggunakan AI"""
        if not driver:
            return 0.0
        
        try:
            # Basic metrics
            title = driver.title
            source = driver.page_source
            url = driver.current_url
            
            score = 0.5  # Base score
            
            # Title quality
            if title and len(title) > 5:
                score += 0.1
            
            # Content length
            content_length = len(source)
            if content_length > 1000:
                score += 0.2
            elif content_length > 500:
                score += 0.1
            
            # Check for errors
            error_indicators = ['404', 'error', 'not found', 'forbidden']
            if any(indicator in title.lower() for indicator in error_indicators):
                score -= 0.3
            
            # Check for CAPTCHA
            captcha_detected, _ = self.captcha_solver.detect_captcha(driver)
            if captcha_detected:
                score -= 0.2
            
            # AI prediction jika available
            if self.prediction_model:
                try:
                    features = {
                        'title_length': len(title),
                        'content_length': content_length,
                        'url_depth': url.count('/'),
                        'has_forms': len(driver.find_elements(By.TAG_NAME, 'form')) > 0
                    }
                    ai_score = self.prediction_model.predict(features)
                    score = (score + ai_score) / 2
                except:
                    pass
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            self.logger.debug(f"Page quality score error: {e}")
            return 0.5
    
    def _perform_advanced_navigation(self, url: str) -> bool:
        """Perform advanced navigation dengan semua features"""
        try:
            self.logger.info(f"Navigating to: {url[:80]}...")
            
            # Navigate to URL
            self.driver.get(url)
            
            # Wait for page load dengan advanced conditions
            wait = WebDriverWait(self.driver, getattr(config, 'BROWSER_TIMEOUT', 30))
            
            # Multiple wait conditions
            conditions = [
                EC.presence_of_element_located((By.TAG_NAME, "body")),
                lambda d: d.execute_script('return document.readyState') == 'complete'
            ]
            
            for condition in conditions:
                try:
                    wait.until(condition)
                    time.sleep(0.5)  # Additional stability delay
                except:
                    pass
            
            # Check for redirects
            current_url = self.driver.current_url
            if current_url != url:
                self.logger.info(f"Redirected to: {current_url[:80]}...")
            
            # Validate page load
            if not self._validate_page_advanced():
                return False
            
            # Check for CAPTCHA
            captcha_detected, captcha_type = self.captcha_solver.detect_captcha(self.driver)
            if captcha_detected:
                self.session_stats['captcha_encounters'] += 1
                self.logger.warning(f"CAPTCHA detected: {captcha_type}")
                
                if not self.captcha_solver.handle_captcha_page(self.driver):
                    self.logger.error("CAPTCHA handling failed")
                    return False
                
                self.session_stats['captcha_solved'] += 1
                self.logger.success("CAPTCHA bypassed successfully")
            
            # Calculate page quality
            quality_score = self._get_page_quality_score(self.driver)
            self.logger.info(f"Page quality score: {quality_score:.2f}")
            
            # Simulate human behavior berdasarkan quality score
            self._simulate_behavior_based_on_quality(quality_score)
            
            return True
            
        except TimeoutException:
            self.logger.error("Page load timeout")
            return False
        except Exception as e:
            self.logger.error(f"Navigation error: {e}")
            return False
    
    def _validate_page_advanced(self) -> bool:
        """Advanced page validation"""
        if not self.driver:
            return False
        
        try:
            # Basic checks
            title = self.driver.title
            current_url = self.driver.current_url
            
            if not title or len(title) < 2:
                self.logger.warning("Page has no title")
                return False
            
            # Error page detection
            error_patterns = [
                '404', 'not found', 'error', 'forbidden', 'access denied',
                'server error', 'maintenance', 'under construction'
            ]
            
            title_lower = title.lower()
            if any(pattern in title_lower for pattern in error_patterns):
                self.logger.warning(f"Error page detected: {title}")
                return False
            
            # Check page source
            page_source = self.driver.page_source
            if len(page_source) < 100:
                self.logger.warning("Page content too small")
                return False
            
            # Check for blank pages
            body_text = self.driver.find_element(By.TAG_NAME, 'body').text
            if len(body_text.strip()) < 10:
                self.logger.warning("Page appears blank")
                return False
            
            # JavaScript errors check
            try:
                errors = self.driver.execute_script("return window.JSErrorCollector_errors || []")
                if errors and len(errors) > 5:
                    self.logger.warning(f"Multiple JavaScript errors: {len(errors)}")
            except:
                pass
            
            return True
            
        except Exception as e:
            self.logger.error(f"Validation error: {e}")
            return False
    
    def _simulate_behavior_based_on_quality(self, quality_score: float):
        """Simulate behavior berdasarkan page quality score"""
        if not self.driver:
            return
        
        # Determine behavior intensity based on quality
        if quality_score > 0.7:  # High quality page
            # Engage more deeply
            self._simulate_engaged_behavior()
        elif quality_score > 0.4:  # Medium quality
            # Normal behavior
            self._simulate_normal_behavior()
        else:  # Low quality
            # Quick glance
            self._simulate_quick_behavior()
    
    def _simulate_engaged_behavior(self):
        """Simulate engaged user behavior"""
        self.logger.info("Simulating engaged behavior")
        
        # Long reading time
        read_time = random.uniform(20, 40)
        
        # Multiple scroll patterns
        for _ in range(random.randint(2, 4)):
            self.behavior_simulator.simulate_scroll_behavior(self.driver)
            time.sleep(read_time / 4)
        
        # Click on elements
        try:
            links = self.driver.find_elements(By.TAG_NAME, "a")[:10]
            if links:
                link = random.choice(links)
                if link.is_displayed() and link.is_enabled():
                    self.behavior_simulator.simulate_click_behavior(link, self.driver)
                    time.sleep(2)
                    self.driver.back()
                    time.sleep(3)
        except:
            pass
        
        # Form interaction jika enabled
        if getattr(config, 'FILL_FORMS', False):
            self._simulate_form_interaction()
    
    def _simulate_normal_behavior(self):
        """Simulate normal user behavior"""
        self.logger.info("Simulating normal behavior")
        
        # Moderate reading time
        read_time = random.uniform(10, 25)
        
        # Some scrolling
        for _ in range(random.randint(1, 3)):
            self.behavior_simulator.simulate_scroll_behavior(self.driver)
            time.sleep(read_time / 3)
        
        # Maybe click something
        if random.random() > 0.7:
            try:
                buttons = self.driver.find_elements(By.TAG_NAME, "button")[:5]
                if buttons:
                    button = random.choice(buttons)
                    if button.is_displayed() and button.is_enabled():
                        self.behavior_simulator.simulate_click_behavior(button, self.driver)
            except:
                pass
    
    def _simulate_quick_behavior(self):
        """Simulate quick glance behavior"""
        self.logger.info("Simulating quick behavior")
        
        # Short reading time
        read_time = random.uniform(5, 15)
        
        # Minimal scrolling
        self.behavior_simulator.simulate_scroll_behavior(self.driver)
        time.sleep(read_time)
    
    def _simulate_form_interaction(self):
        """Simulate form interaction jika forms ditemukan"""
        if not getattr(config, 'FILL_FORMS', False):
            return
        
        try:
            forms = self.driver.find_elements(By.TAG_NAME, "form")[:3]
            
            for form in forms:
                if not form.is_displayed():
                    continue
                
                # Find input fields
                inputs = form.find_elements(By.TAG_NAME, "input")
                textareas = form.find_elements(By.TAG_NAME, "textarea")
                all_fields = inputs + textareas
                
                if not all_fields:
                    continue
                
                self.logger.info(f"Found form with {len(all_fields)} fields")
                
                # Fill some fields
                fields_to_fill = random.sample(all_fields, min(3, len(all_fields)))
                
                for field in fields_to_fill:
                    try:
                        field_type = field.get_attribute("type")
                        field_name = field.get_attribute("name") or field.get_attribute("id") or "field"
                        
                        # Skip certain field types
                        if field_type in ["hidden", "submit", "button", "radio", "checkbox"]:
                            continue
                        
                        # Generate appropriate data
                        if field_type == "email":
                            data = f"test{random.randint(1000, 9999)}@example.com"
                        elif field_type == "tel" or "phone" in field_name.lower():
                            data = f"+1{random.randint(200, 999)}{random.randint(100, 999)}{random.randint(1000, 9999)}"
                        elif "name" in field_name.lower():
                            names = ["John", "Jane", "Bob", "Alice", "Mike", "Sarah"]
                            data = random.choice(names)
                        else:
                            data = f"Test data {random.randint(1, 100)}"
                        
                        # Type the data
                        self.behavior_simulator.simulate_typing_behavior(data, field)
                        time.sleep(random.uniform(0.5, 1.5))
                        
                    except Exception as e:
                        self.logger.debug(f"Form field error: {e}")
                
                # Maybe submit the form
                if getattr(config, 'SUBMIT_FORMS', False) and random.random() > 0.7:
                    try:
                        submit = form.find_element(By.XPATH, ".//*[@type='submit']")
                        if submit:
                            self.behavior_simulator.simulate_click_behavior(submit, self.driver)
                            time.sleep(3)
                            
                            # Handle possible redirect or new page
                            if random.random() > 0.5:
                                self.driver.back()
                                time.sleep(2)
                    except:
                        pass
                
                # Don't fill too many forms
                if random.random() > 0.5:
                    break
                    
        except Exception as e:
            self.logger.debug(f"Form interaction error: {e}")
    
    def execute_task(self, url: str, proxies: List[str] = None) -> bool:
        """
        Execute advanced visit task ke URL
        Returns: True jika berhasil
        """
        self.start_time = time.time()
        self.current_url = url
        self.is_running = True
        
        self.logger.info(f"Starting advanced task execution")
        self.logger.info(f"Target URL: {url[:100]}...")
        
        if proxies:
            self.logger.info(f"Available proxies: {len(proxies)}")
        
        try:
            # Validate URL
            if not validate_url(url):
                self.logger.error("Invalid URL format")
                self.session_stats['errors'].append("Invalid URL")
                return False
            
            # Select proxy
            proxy = None
            if proxies and getattr(config, 'USE_PROXY', False):
                proxy = random.choice(proxies) if proxies else None
                self.current_proxy = proxy
                self.logger.info(f"Using proxy: {proxy[:50] if proxy else 'None'}")
            
            # Setup browser dengan semua features
            self.logger.info("Setting up advanced browser...")
            if not self.browser_manager.setup_driver(proxy):
                self.logger.error("Failed to setup browser")
                self.session_stats['errors'].append("Browser setup failed")
                return False
            
            self.driver = self.browser_manager.driver
            
            # Perform navigation
            self.logger.info("Performing advanced navigation...")
            if not self._perform_advanced_navigation(url):
                self.logger.error("Navigation failed")
                self.session_stats['errors'].append("Navigation failed")
                self._cleanup_task()
                return False
            
            # Update statistics
            self.session_stats['pages_visited'] += 1
            self.session_stats['successful_visits'] += 1
            
            # Calculate task duration
            task_duration = time.time() - self.start_time
            self.session_stats['total_time'] += task_duration
            
            # Update average
            total_visits = self.session_stats['successful_visits'] + self.session_stats['failed_visits']
            if total_visits > 0:
                self.session_stats['avg_page_time'] = self.session_stats['total_time'] / total_visits
            
            # Log success
            self.logger.success(f"Task completed successfully in {task_duration:.1f}s")
            
            # Performance metrics
            perf_metrics = self.browser_manager.get_performance_metrics()
            self.logger.info(f"Performance: {perf_metrics['avg_memory']:.1f}MB memory, {perf_metrics['avg_cpu']:.1f}% CPU")
            
            # Cleanup
            self._cleanup_task()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
            self.session_stats['errors'].append(str(e)[:100])
            self.session_stats['failed_visits'] += 1
            self._cleanup_task()
            return False
    
    def _cleanup_task(self):
        """Cleanup task resources"""
        self.is_running = False
        
        if self.driver:
            try:
                self.browser_manager.cleanup()
                self.driver = None
            except Exception as e:
                self.logger.error(f"Cleanup error: {e}")
    
    def toggle_visibility(self):
        """Toggle browser window visibility"""
        if not self.driver:
            self.logger.warning("No active browser to toggle")
            return
        
        try:
            # Method 1: Minimize/restore window
            if self.is_hidden:
                self.driver.minimize_window()
            else:
                self.driver.maximize_window()
            
            self.is_hidden = not self.is_hidden
            status = "HIDDEN 🙈" if self.is_hidden else "VISIBLE 👁️"
            
            self.logger.info(f"Browser visibility toggled: {status}")
            
            # Method 2: JavaScript untuk hide/show (alternatif)
            if random.random() > 0.5:
                script = "document.body.style.display = 'none';" if not self.is_hidden else "document.body.style.display = 'block';"
                self.driver.execute_script(script)
                
        except Exception as e:
            self.logger.error(f"Visibility toggle error: {e}")
            
            # Fallback: simple flag toggle
            self.is_hidden = not self.is_hidden
    
    def stop(self):
        """Stop worker dengan graceful shutdown"""
        self.logger.info("Initiating graceful shutdown...")
        
        # Update final statistics
        if self.start_time:
            total_time = time.time() - self.start_time
            self.session_stats['total_time'] = total_time
        
        # Print session summary
        print(f"\n{'='*60}")
        print(f"📊 WORKER #{self.worker_id} - SESSION SUMMARY")
        print(f"{'='*60}")
        print(f"Pages visited: {self.session_stats['pages_visited']}")
        print(f"Successful: {self.session_stats['successful_visits']}")
        print(f"Failed: {self.session_stats['failed_visits']}")
        print(f"Success rate: {(self.session_stats['successful_visits']/max(1, self.session_stats['pages_visited'])*100):.1f}%")
        print(f"CAPTCHA encounters: {self.session_stats['captcha_encounters']}")
        print(f"CAPTCHA solved: {self.session_stats['captcha_solved']}")
        print(f"Average page time: {self.session_stats['avg_page_time']:.1f}s")
        print(f"Total session time: {self.session_stats['total_time']:.1f}s")
        
        if self.session_stats['errors']:
            print(f"Recent errors: {self.session_stats['errors'][-3:]}")
        
        print(f"{'='*60}")
        
        # AI learning jika available
        if self.ai_engine and hasattr(self.ai_engine, 'learn_from_session'):
            try:
                self.ai_engine.learn_from_session(self.session_stats)
                self.logger.info("AI learning completed")
            except Exception as e:
                self.logger.error(f"AI learning failed: {e}")
        
        # Cleanup resources
        self._cleanup_task()
        
        self.logger.info("Worker stopped gracefully")
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive worker status"""
        perf_metrics = self.browser_manager.get_performance_metrics() if self.browser_manager else {}
        
        return {
            'worker_id': self.worker_id,
            'is_active': self.is_running,
            'is_hidden': self.is_hidden,
            'current_url': self.current_url,
            'current_proxy': self.current_proxy[:50] if self.current_proxy else None,
            'session_stats': self.session_stats.copy(),
            'performance': perf_metrics,
            'features': {
                'ai_enabled': AI_AVAILABLE,
                'stealth_enabled': STEALTH_AVAILABLE,
                'captcha_solver': self.captcha_solver.enabled,
                'human_behavior': True
            }
        }


# ==================== TEST FUNCTION ====================
def test_worker():
    """Test function untuk worker"""
    print("🧪 Testing Advanced BotWorker...")
    
    worker = BotWorker(999)
    
    # Test status
    status = worker.get_status()
    print(f"Worker status: {json.dumps(status, indent=2, default=str)}")
    
    # Test dengan dummy URL
    test_url = "https://httpbin.org/html"
    print(f"\n🔗 Testing with URL: {test_url}")
    
    success = worker.execute_task(test_url)
    print(f"Task result: {'✅ SUCCESS' if success else '❌ FAILED'}")
    
    # Final status
    final_status = worker.get_status()
    print(f"\n📊 Final stats:")
    print(f"  Pages visited: {final_status['session_stats']['pages_visited']}")
    print(f"  Successful: {final_status['session_stats']['successful_visits']}")
    
    worker.stop()
    
    print("\n✅ Worker test completed!")


if __name__ == "__main__":
    test_worker()