"""
Bot Configuration
Semua settings bot dalam satu class
"""

class BotConfig:
    """Configuration untuk Traffic Bot"""
    
    # ==================== BASIC SETTINGS ====================
    
    # Browser settings
    HEADLESS = False
    USE_UNDETECTED_CHROME = True
    BROWSER_VISIBILITY = "normal"  # "normal", "minimized", "stealth"
    
    # User Agent
    USER_AGENT_MODE = "Mixed"  # "Desktop Only", "Mobile Only", "Mixed"
    
    # ==================== PROXY SETTINGS ====================
    
    PROXY_ENABLED = False
    PROXY_TYPE = "http"  # "http", "socks4", "socks5", "auto"
    PROXY_FILE = "proxies.txt"
    PROXY_ROTATION = True
    
    # ==================== INTERACTION BEHAVIOR ====================
    
    # Scroll behavior
    SCROLL_MIN = 30
    SCROLL_MAX = 60
    
    # Delay (reading time) in seconds
    DELAY_MIN = 20
    DELAY_MAX = 30
    
    # CTR Simulation (Click-Through Rate)
    TARGET_CTR = 8.0  # Percentage (0-100)
    
    # Mouse behavior
    MOUSE_STYLE = "Human Curves"  # "Human Curves", "Direct", "Random"
    
    # ==================== DEEP NAVIGATION SETTINGS ====================
    
    # Enable/Disable Deep Navigation
    DEEP_NAVIGATION_ENABLED = True
    
    # Navigation Depth
    MIN_DEPTH = 2  # Minimal berapa halaman yang dikunjungi
    MAX_DEPTH = 5  # Maksimal berapa halaman yang dikunjungi
    
    # Behavior per Depth Level
    # Format: {depth: {scroll_min, scroll_max, read_min, read_max, click_prob}}
    DEPTH_BEHAVIORS = {
        0: {  # Landing Page
            'scroll_min': 30,
            'scroll_max': 60,
            'read_min': 20,
            'read_max': 30,
            'click_prob': 80  # 80% chance to click to next page
        },
        1: {  # Depth Level 1
            'scroll_min': 20,
            'scroll_max': 40,
            'read_min': 15,
            'read_max': 25,
            'click_prob': 70  # 70% chance to click deeper
        },
        2: {  # Depth Level 2
            'scroll_min': 15,
            'scroll_max': 30,
            'read_min': 10,
            'read_max': 20,
            'click_prob': 50  # 50% chance to click deeper
        },
        3: {  # Depth Level 3
            'scroll_min': 10,
            'scroll_max': 20,
            'read_min': 8,
            'read_max': 15,
            'click_prob': 30  # 30% chance to click deeper
        },
        4: {  # Depth Level 4
            'scroll_min': 5,
            'scroll_max': 15,
            'read_min': 5,
            'read_max': 10,
            'click_prob': 10  # 10% chance to click deeper
        },
    }
    
    # Link Selection Priority (True = enabled, False = disabled)
    LINK_PRIORITY_NAV_MENU = True    # Prioritize navigation menu links
    LINK_PRIORITY_RELATED = True     # Prioritize related posts/articles
    LINK_PRIORITY_CONTENT = True     # Prioritize content links
    LINK_PRIORITY_FOOTER = False     # Prioritize footer links
    
    # Link Filtering
    LINK_INTERNAL_ONLY = True        # Only click internal links (same domain)
    LINK_AVOID_VISITED = True        # Avoid clicking already visited URLs
    LINK_EXCLUDE_SOCIAL = True       # Exclude social media links
    LINK_EXCLUDE_EXTERNAL = True     # Exclude external domain links
    
    # ==================== CAPTCHA SETTINGS ====================
    
    CAPTCHA_SOLVER_ENABLED = False
    CAPTCHA_SOLVER_SERVICE = "2captcha"  # "2captcha", "anticaptcha"
    CAPTCHA_API_KEY = ""
    CAPTCHA_MAX_RETRY = 3
    AUTO_CAPTCHA_LEARN = True  # AI learning dari CAPTCHA patterns
    
    # ==================== FINGERPRINT SETTINGS ====================
    
    FINGERPRINT_MODE = "Cortex"  # "Cortex", "JSON"
    FINGERPRINT_FOLDER = ""  # Path ke folder JSON fingerprints
    
    # Canvas fingerprinting
    CANVAS_FINGERPRINT = True
    WEBGL_FINGERPRINT = True
    AUDIO_FINGERPRINT = True
    
    # Browser features
    WEBRTC_ENABLED = True
    TIMEZONE_SYNC = True
    LANGUAGE_SYNC = True
    SCREEN_RESOLUTION_RANDOM = True
    
    # ==================== AI SETTINGS ====================
    
    AI_ENABLED = True
    AI_PREDICT_CTR = True
    AI_OPTIMIZE_BEHAVIOR = True
    AI_ANOMALY_DETECTION = True
    
    # ==================== PERFORMANCE SETTINGS ====================
    
    MAX_WORKERS = 50
    TASK_TIMEOUT = 300  # seconds
    RETRY_FAILED_TASKS = True
    MAX_RETRY_ATTEMPTS = 3
    
    # ==================== LOGGING ====================
    
    LOG_LEVEL = "INFO"  # "DEBUG", "INFO", "WARNING", "ERROR"
    LOG_FILE = "bot.log"
    LOG_MAX_SIZE = 10 * 1024 * 1024  # 10 MB
    
    # ==================== ADVANCED ====================
    
    # Resource blocking (untuk speed)
    BLOCK_IMAGES = False
    BLOCK_CSS = False
    BLOCK_FONTS = False
    
    # Page load strategy
    PAGE_LOAD_STRATEGY = "normal"  # "normal", "eager", "none"
    
    # Stealth mode
    STEALTH_MODE = True
    HIDE_AUTOMATION = True
    
    def __repr__(self):
        return f"<BotConfig: Workers={self.MAX_WORKERS}, AI={self.AI_ENABLED}, DeepNav={self.DEEP_NAVIGATION_ENABLED}>"


# Global config instance
config = BotConfig()
