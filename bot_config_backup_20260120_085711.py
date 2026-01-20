"""
Traffic Bot Configuration File
All bot settings are stored here
"""

import os

# ==================== BASIC SETTINGS ====================

# Bot identification
BOT_NAME = "Traffic Bot Professional"
BOT_VERSION = "2.0.0"

# Base directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
STEALTH_DIR = os.path.join(BASE_DIR, "stealth")

# Create directories if they don't exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(STEALTH_DIR, exist_ok=True)


# ==================== TRAFFIC SETTINGS ====================

# Traffic mode: "organic", "aggressive", "hybrid"
TRAFFIC_MODE = "hybrid"

# Organic traffic settings (0-100)
ORGANIC_PERCENTAGE = 70

# Session settings
SESSION_MIN_DURATION = 30  # seconds
SESSION_MAX_DURATION = 120  # seconds
SESSION_SCROLL_ENABLED = True
SESSION_RANDOM_CLICKS = True

# Page interaction settings
MIN_PAGE_VIEWS = 2
MAX_PAGE_VIEWS = 5
ENABLE_DEEP_NAVIGATION = True


# ==================== BROWSER SETTINGS ====================

# Browser type: "chrome", "firefox", "edge"
BROWSER_TYPE = "chrome"

# Headless mode
HEADLESS_MODE = False

# Browser fingerprint randomization
RANDOMIZE_FINGERPRINT = True
RANDOMIZE_USER_AGENT = True
RANDOMIZE_CANVAS = True
RANDOMIZE_WEBGL = True
RANDOMIZE_AUDIO = True

# Browser window size
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080


# ==================== PROXY SETTINGS ====================

# Proxy configuration
USE_PROXY = True
PROXY_FILE = "proxies.txt"
PROXY_TYPE = "http"  # "http", "socks4", "socks5"
PROXY_ROTATION = "per_session"  # "per_session", "per_request", "disabled"

# Proxy validation
VALIDATE_PROXIES = True
PROXY_TIMEOUT = 10  # seconds
MAX_PROXY_RETRIES = 3


# ==================== FINGERPRINT SETTINGS ====================

# Device types for fingerprinting
DEVICE_TYPES = ["desktop", "mobile", "tablet"]
DESKTOP_PERCENTAGE = 70
MOBILE_PERCENTAGE = 20
TABLET_PERCENTAGE = 10

# Operating systems
OS_TYPES = ["Windows", "MacOS", "Linux", "Android", "iOS"]

# Screen resolutions (desktop)
SCREEN_RESOLUTIONS = [
    (1920, 1080),
    (1366, 768),
    (1440, 900),
    (1536, 864),
    (1280, 720)
]


# ==================== CAPTCHA SETTINGS ====================

CAPTCHA_SOLVER_ENABLED = False
CAPTCHA_SOLVER_SERVICE = "2captcha"
CAPTCHA_API_KEY = ""
CAPTCHA_MAX_RETRY = 3
AUTO_CAPTCHA_LEARN = True


# ==================== AI/ML SETTINGS ====================

# Behavioral learning
ENABLE_BEHAVIORAL_AI = True
BEHAVIOR_LEARNING_RATE = 0.1
BEHAVIOR_MEMORY_SIZE = 1000

# Pattern detection
ENABLE_PATTERN_DETECTION = True
PATTERN_CONFIDENCE_THRESHOLD = 0.75

# CTR prediction
ENABLE_CTR_PREDICTION = True
CTR_MODEL_UPDATE_FREQUENCY = 100  # sessions

# Anomaly detection
ENABLE_ANOMALY_DETECTION = True
ANOMALY_THRESHOLD = 0.85


# ==================== PERFORMANCE SETTINGS ====================

# Worker settings
MAX_WORKERS = 50
WORKER_STARTUP_DELAY = 2  # seconds between worker starts
WORKER_RESTART_ON_ERROR = True

# Resource limits
MAX_MEMORY_PER_WORKER = 512  # MB
MAX_CPU_USAGE = 80  # percentage

# Timeouts
PAGE_LOAD_TIMEOUT = 30  # seconds
ELEMENT_WAIT_TIMEOUT = 10  # seconds
SCRIPT_TIMEOUT = 30  # seconds


# ==================== LOGGING SETTINGS ====================

# Log level: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
LOG_LEVEL = "INFO"

# Log file settings
LOG_TO_FILE = True
LOG_FILE = os.path.join(LOGS_DIR, "bot.log")
LOG_MAX_SIZE = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT = 5

# Console logging
LOG_TO_CONSOLE = True
COLORED_LOGS = True


# ==================== OPERATION SETTINGS ====================

# Bot operation hours (24-hour format)
OPERATION_START_HOUR = 0  # 00:00
OPERATION_END_HOUR = 23  # 23:00
RESPECT_OPERATION_HOURS = False

# Pause/Resume
ENABLE_AUTO_PAUSE = True
AUTO_PAUSE_ON_ERROR = True
PAUSE_DURATION = 60  # seconds

# Safety features
EMERGENCY_STOP_ENABLED = True
MAX_CONSECUTIVE_ERRORS = 10


# ==================== DEEP NAVIGATION SETTINGS ====================

# Deep navigation behavior
DEEP_NAV_PROBABILITY = 0.7  # 70% chance
DEEP_NAV_MAX_DEPTH = 3
DEEP_NAV_SAME_DOMAIN_ONLY = True

# Link selection
PREFER_INTERNAL_LINKS = True
AVOID_EXTERNAL_LINKS = True
LINK_SELECTION_RANDOM = True


# ==================== REPORTING SETTINGS ====================

# Statistics collection
ENABLE_STATISTICS = True
STATS_UPDATE_INTERVAL = 60  # seconds

# Report generation
AUTO_GENERATE_REPORTS = True
REPORT_INTERVAL = 3600  # 1 hour in seconds
REPORT_FORMAT = "json"  # "json", "csv", "html"


# ==================== ADVANCED SETTINGS ====================

# Stealth mode features
ENABLE_WEBRTC_LEAK_PROTECTION = True
ENABLE_TIMEZONE_SPOOFING = True
ENABLE_LANGUAGE_SPOOFING = True
ENABLE_HARDWARE_CONCURRENCY_SPOOFING = True

# Anti-detection measures
ENABLE_NAVIGATOR_PERMISSIONS = True
ENABLE_PLUGINS_SPOOFING = True
ENABLE_MEDIA_DEVICES_SPOOFING = True

# Network settings
ENABLE_DNS_LEAK_PROTECTION = False
USE_CUSTOM_DNS = False
CUSTOM_DNS_SERVERS = ["8.8.8.8", "8.8.4.4"]


# ==================== DATABASE SETTINGS ====================

# Database configuration
DB_TYPE = "sqlite"  # "sqlite", "mysql", "postgresql"
DB_FILE = os.path.join(DATA_DIR, "bot_data.db")

# MySQL/PostgreSQL settings (if used)
DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "trafficbot"
DB_USER = "root"
DB_PASSWORD = ""


# ==================== API SETTINGS ====================

# External API integrations
ENABLE_WEBHOOK = False
WEBHOOK_URL = ""
WEBHOOK_EVENTS = ["session_start", "session_end", "error", "captcha_solved"]

# API rate limiting
API_RATE_LIMIT = 100  # requests per minute
API_RATE_LIMIT_ENABLED = True


# ==================== CONFIGURATION CLASS ====================

class Config:
    """Configuration manager class"""
    
    def __init__(self):
        """Initialize configuration"""
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        # Load all global variables into config object
        for key in dir():
            if key.isupper():
                setattr(self, key, globals()[key])
    
    def save_config(self):
        """Save configuration to file"""
        # This will be implemented to save changes back to file
        pass
    
    def get(self, key, default=None):
        """Get configuration value"""
        return getattr(self, key, default)
    
    def set(self, key, value):
        """Set configuration value"""
        setattr(self, key, value)


# Create global config instance
config = Config()
