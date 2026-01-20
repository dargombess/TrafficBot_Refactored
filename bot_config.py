"""
Bot Configuration Settings - Professional Edition
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# ==================== CONFIGURATION VERSION ====================
CONFIG_VERSION = "2.0.0"
CONFIG_AUTHOR = "TrafficBot Team"

# ==================== PATHS & DIRECTORIES ====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data directories
DATA_DIR = os.path.join(BASE_DIR, 'data')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
AI_MODELS_DIR = os.path.join(BASE_DIR, 'ai', 'models')
CONFIG_DIR = os.path.join(BASE_DIR, 'config')

# Create directories if they don't exist
for directory in [DATA_DIR, LOGS_DIR, AI_MODELS_DIR, CONFIG_DIR]:
    os.makedirs(directory, exist_ok=True)

# ==================== FILE PATHS ====================
# URLs/Articles file (required)
FILE_ARTICLES = os.path.join(BASE_DIR, 'artikel.txt')  # Sesuaikan dengan nama file Anda

# Proxies file (optional)
FILE_PROXIES = os.path.join(DATA_DIR, 'proxies.txt')

# Database files
DATABASE_FILE = os.path.join(DATA_DIR, 'bot_data.db')
HISTORY_DB_FILE = os.path.join(DATA_DIR, 'history.db')
STATS_DB_FILE = os.path.join(DATA_DIR, 'statistics.db')

# Log files
MAIN_LOG_FILE = os.path.join(LOGS_DIR, 'trafficbot.log')
ERROR_LOG_FILE = os.path.join(LOGS_DIR, 'errors.log')
PERFORMANCE_LOG_FILE = os.path.join(LOGS_DIR, 'performance.log')

# Configuration backup
CONFIG_BACKUP_DIR = os.path.join(CONFIG_DIR, 'backups')

# ==================== CORE SETTINGS ====================
# Worker settings
TASK_COUNT = 10                    # Default number of workers
MAX_WORKERS = 50                   # Maximum workers allowed
MIN_WORKERS = 1                    # Minimum workers allowed
WORKER_TIMEOUT = 30                # Worker timeout in seconds

# Queue & Processing
SHUFFLE_MODE = True                # Enable intelligent URL shuffle
MAX_URL_RETRIES = 3                # Maximum retries for failed URLs
RETRY_DELAY = 5                    # Delay between retries (seconds)
CONCURRENT_TASKS = 5               # Max concurrent tasks per worker

# Infinite Loop
INFINITE_MODE = True               # Run in infinite loop mode
MAX_CYCLES = 0                     # 0 = unlimited, >0 = limit cycles

# ==================== BROWSER SETTINGS ====================
BROWSER_HEADLESS = False           # Show browser (False = visible)
BROWSER_TYPE = "chrome"            # "chrome" or "firefox"
BROWSER_TIMEOUT = 30               # Page load timeout (seconds)
BROWSER_WINDOW_SIZE = "1920,1080"  # Browser window size
BROWSER_LANGUAGE = "en-US"         # Browser language

# Chrome specific
CHROME_VERSION = "auto"            # "auto" or specific version
CHROME_DRIVER_PATH = "auto"        # "auto" or custom path

# ==================== BEHAVIOR SETTINGS ====================
# Navigation behavior
MIN_NAVIGATION_DELAY = 1.5         # Minimum delay between actions (seconds)
MAX_NAVIGATION_DELAY = 4.0         # Maximum delay between actions (seconds)
RANDOM_MOUSE_MOVEMENT = True       # Add random mouse movements
RANDOM_SCROLLING = True            # Add random scrolling
PAGE_READ_TIME_MIN = 10            # Minimum time on page (seconds)
PAGE_READ_TIME_MAX = 30            # Maximum time on page (seconds)

# Click behavior
CLICK_VARIATION = True             # Add variation to click positions
DOUBLE_CLICK_CHANCE = 0.1          # 10% chance for double click
RIGHT_CLICK_CHANCE = 0.05          # 5% chance for right click

# Form interaction
FILL_FORMS = False                 # Fill forms if found
RANDOM_FORM_DATA = True            # Use random form data
SUBMIT_FORMS = False               # Submit forms

# ==================== AI & INTELLIGENCE SETTINGS ====================
AI_ENABLED = True                  # Enable AI Engine
AI_TRAINING_INTERVAL = 100         # Train AI every N tasks
AI_PREDICTION_ENABLED = True       # Enable AI predictions

# Machine Learning models
ML_MODEL_PATH = os.path.join(AI_MODELS_DIR, 'behavior_model.pkl')
ML_TRAINING_DATA = os.path.join(AI_MODELS_DIR, 'training_data.json')

# Pattern detection
PATTERN_DETECTION = True           # Enable pattern detection
ANOMALY_DETECTION = True           # Enable anomaly detection
BEHAVIOR_LEARNING = True           # Enable behavior learning

# ==================== STEALTH & ANTI-DETECTION ====================
# Basic stealth
RANDOM_USER_AGENT = True           # Randomize user agents
USER_AGENT_FILE = os.path.join(DATA_DIR, 'user_agents.txt')

# Advanced stealth
ENABLE_STEALTH = True              # Enable selenium-stealth
FINGERPRINT_RANDOMIZATION = True   # Randomize browser fingerprint
CANVAS_FINGERPRINT_SPOOF = True    # Spoof canvas fingerprint
WEBGL_FINGERPRINT_SPOOF = True     # Spoof WebGL fingerprint
AUDIO_CONTEXT_SPOOF = True         # Spoof audio context

# Timezone & location
RANDOM_TIMEZONE = True             # Randomize timezone
RANDOM_LOCALE = True               # Randomize locale
FAKE_GEOLOCATION = True            # Use fake geolocation

# ==================== PROXY SETTINGS ====================
USE_PROXY = True                   # Use proxies if available
PROXY_TYPE = "http"                # "http", "socks4", "socks5", "auto"
PROXY_TIMEOUT = 10                 # Proxy timeout (seconds)
PROXY_MAX_RETRIES = 3              # Max proxy retries
PROXY_ROTATION_INTERVAL = 10       # Rotate proxy every N requests

# Proxy authentication
PROXY_AUTH_REQUIRED = False        # Proxy requires authentication
PROXY_USERNAME = ""                # Proxy username
PROXY_PASSWORD = ""                # Proxy password

# Proxy quality filtering
MIN_PROXY_SUCCESS_RATE = 0.7       # Minimum success rate to use proxy
MAX_PROXY_RESPONSE_TIME = 5.0      # Maximum response time in seconds

# ==================== CAPTCHA SETTINGS ====================
CAPTCHA_SOLVER_ENABLED = False     # Enable CAPTCHA solver
CAPTCHA_SERVICE = "2captcha"       # "2captcha", "anticaptcha", "capmonster"
CAPTCHA_API_KEY = ""               # Your CAPTCHA service API key
CAPTCHA_MAX_ATTEMPTS = 3           # Max CAPTCHA solving attempts
CAPTCHA_RETRY_DELAY = 5            # Delay between CAPTCHA attempts

# ==================== PERFORMANCE SETTINGS ====================
# Resource management
MAX_MEMORY_USAGE = 512             # Max memory usage in MB
MAX_CPU_USAGE = 80                 # Max CPU usage percentage
AUTO_SCALING = True                # Auto-scale workers based on resources

# Network optimization
CONNECTION_POOL_SIZE = 10          # HTTP connection pool size
REQUEST_TIMEOUT = 30               # HTTP request timeout
MAX_REDIRECTS = 5                  # Maximum HTTP redirects

# Cache settings
ENABLE_CACHE = True                # Enable caching
CACHE_SIZE = 100                   # Cache size in MB
CACHE_TTL = 3600                   # Cache time-to-live in seconds

# ==================== LOGGING SETTINGS ====================
LOG_LEVEL = "INFO"                 # DEBUG, INFO, WARNING, ERROR
LOG_TO_FILE = True                 # Save logs to file
LOG_TO_CONSOLE = True              # Show logs in console
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Log rotation
LOG_ROTATION = True                # Enable log rotation
LOG_MAX_SIZE = 10                  # Max log file size in MB
LOG_BACKUP_COUNT = 5               # Number of backup logs to keep

# ==================== MONITORING & METRICS ====================
METRICS_ENABLED = True             # Enable metrics collection
METRICS_INTERVAL = 60              # Metrics collection interval (seconds)
METRICS_DB = os.path.join(DATA_DIR, 'metrics.db')

# Performance metrics
TRACK_PERFORMANCE = True           # Track performance metrics
PERFORMANCE_SAMPLES = 1000         # Number of samples to keep

# ==================== SAFETY & LIMITS ====================
# Rate limiting
REQUESTS_PER_MINUTE = 60           # Max requests per minute
REQUESTS_PER_HOUR = 3600           # Max requests per hour
CONCURRENT_REQUESTS = 10           # Max concurrent requests

# Safety limits
MAX_PAGES_PER_SESSION = 100        # Max pages per browser session
MAX_SESSION_DURATION = 1800        # Max session duration in seconds (30 min)
COOL_DOWN_PERIOD = 300             # Cool down period between sessions (5 min)

# Blacklisting
ENABLE_BLACKLIST = True            # Enable IP/domain blacklisting
BLACKLIST_FILE = os.path.join(DATA_DIR, 'blacklist.txt')
AUTO_BLACKLIST_FAILURES = True     # Auto-blacklist after N failures
BLACKLIST_THRESHOLD = 5            # Failures before blacklisting

# ==================== ADVANCED SETTINGS ====================
# Debug settings
DEBUG_MODE = False                 # Enable debug mode
VERBOSE_LOGGING = False            # Enable verbose logging
SCREENSHOT_ON_ERROR = True         # Take screenshot on error
HTML_DUMP_ON_ERROR = False         # Dump HTML on error

# Network settings
DNS_CACHE_ENABLED = True           # Enable DNS cache
TCP_FAST_OPEN = True               # Enable TCP Fast Open
HTTP2_ENABLED = True               # Enable HTTP/2

# SSL settings
VERIFY_SSL = True                  # Verify SSL certificates
SSL_CIPHERS = "HIGH:!aNULL:!MD5"   # SSL cipher suite

# ==================== EXPORT CONFIG ====================
class Config:
    """Configuration object with validation and utilities"""
    
    def __init__(self):
        # Copy all uppercase variables to config object
        for key, value in globals().items():
            if not key.startswith('_') and key.upper() == key and key != 'Config':
                setattr(self, key, value)
        
        # Initialize logger
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        """Setup application logger"""
        logger = logging.getLogger("TrafficBot")
        logger.setLevel(getattr(logging, self.LOG_LEVEL))
        
        # Remove existing handlers
        logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            self.LOG_FORMAT,
            datefmt=self.LOG_DATE_FORMAT
        )
        
        # Console handler
        if self.LOG_TO_CONSOLE:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(getattr(logging, self.LOG_LEVEL))
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # File handler
        if self.LOG_TO_FILE:
            try:
                file_handler = logging.FileHandler(
                    self.MAIN_LOG_FILE,
                    encoding='utf-8'
                )
                file_handler.setLevel(getattr(logging, self.LOG_LEVEL))
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
            except Exception as e:
                print(f"Failed to setup file logging: {e}")
        
        # Error file handler
        try:
            error_handler = logging.FileHandler(
                self.ERROR_LOG_FILE,
                encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(formatter)
            logger.addHandler(error_handler)
        except:
            pass
        
        return logger
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration as dictionary"""
        config_dict = {}
        for key in dir(self):
            if not key.startswith('_') and key.upper() == key:
                value = getattr(self, key)
                # Skip callables and the logger
                if not callable(value) and key != 'logger':
                    config_dict[key] = value
        return config_dict
    
    def save_to_file(self, filepath: str = None) -> bool:
        """Save configuration to JSON file"""
        try:
            if filepath is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filepath = os.path.join(
                    self.CONFIG_BACKUP_DIR,
                    f'config_backup_{timestamp}.json'
                )
            
            config_data = self.get_all()
            config_data['__version__'] = self.CONFIG_VERSION
            config_data['__timestamp__'] = datetime.now().isoformat()
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, default=str)
            
            self.logger.info(f"Configuration saved to: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            return False
    
    def load_from_file(self, filepath: str) -> bool:
        """Load configuration from JSON file"""
        try:
            if not os.path.exists(filepath):
                self.logger.error(f"Config file not found: {filepath}")
                return False
            
            with open(filepath, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Validate version
            if config_data.get('__version__') != self.CONFIG_VERSION:
                self.logger.warning(
                    f"Config version mismatch: "
                    f"expected {self.CONFIG_VERSION}, "
                    f"got {config_data.get('__version__')}"
                )
            
            # Update configuration
            for key, value in config_data.items():
                if not key.startswith('__') and hasattr(self, key):
                    setattr(self, key, value)
            
            self.logger.info(f"Configuration loaded from: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            return False
    
    def validate(self) -> tuple[bool, list[str]]:
        """Validate configuration"""
        errors = []
        
        # Check required files
        if not os.path.exists(self.FILE_ARTICLES):
            errors.append(f"Articles file not found: {self.FILE_ARTICLES}")
        
        # Check numeric ranges
        if self.TASK_COUNT < self.MIN_WORKERS or self.TASK_COUNT > self.MAX_WORKERS:
            errors.append(f"TASK_COUNT must be between {self.MIN_WORKERS} and {self.MAX_WORKERS}")
        
        if self.MIN_NAVIGATION_DELAY >= self.MAX_NAVIGATION_DELAY:
            errors.append("MIN_NAVIGATION_DELAY must be less than MAX_NAVIGATION_DELAY")
        
        if self.PAGE_READ_TIME_MIN >= self.PAGE_READ_TIME_MAX:
            errors.append("PAGE_READ_TIME_MIN must be less than PAGE_READ_TIME_MAX")
        
        # Check proxy settings
        if self.USE_PROXY and self.FILE_PROXIES and not os.path.exists(self.FILE_PROXIES):
            errors.append(f"Proxy file specified but not found: {self.FILE_PROXIES}")
        
        # Check CAPTCHA settings
        if self.CAPTCHA_SOLVER_ENABLED and not self.CAPTCHA_API_KEY:
            errors.append("CAPTCHA solver enabled but no API key provided")
        
        # Check directories
        for dir_path in [self.DATA_DIR, self.LOGS_DIR, self.AI_MODELS_DIR]:
            if not os.path.exists(dir_path):
                try:
                    os.makedirs(dir_path, exist_ok=True)
                except Exception as e:
                    errors.append(f"Cannot create directory {dir_path}: {e}")
        
        return len(errors) == 0, errors
    
    def get_summary(self) -> str:
        """Get configuration summary"""
        summary = [
            f"TrafficBot Configuration v{self.CONFIG_VERSION}",
            "=" * 50,
            f"Workers: {self.TASK_COUNT} (max: {self.MAX_WORKERS})",
            f"Mode: {'Infinite Loop' if self.INFINITE_MODE else 'Single Cycle'}",
            f"Shuffle: {'Enabled' if self.SHUFFLE_MODE else 'Disabled'}",
            f"Browser: {'Headless' if self.BROWSER_HEADLESS else 'Visible'}",
            f"AI Engine: {'Enabled' if self.AI_ENABLED else 'Disabled'}",
            f"Stealth Mode: {'Enabled' if self.ENABLE_STEALTH else 'Disabled'}",
            f"Proxy: {'Enabled' if self.USE_PROXY else 'Disabled'}",
            f"CAPTCHA Solver: {'Enabled' if self.CAPTCHA_SOLVER_ENABLED else 'Disabled'}",
            f"Logging: {self.LOG_LEVEL}",
            "=" * 50
        ]
        return "\n".join(summary)


# Create global config instance
config = Config()

# Validate configuration on import
is_valid, validation_errors = config.validate()
if not is_valid:
    config.logger.warning("Configuration validation failed:")
    for error in validation_errors:
        config.logger.warning(f"  - {error}")

# Log configuration summary
config.logger.info(config.get_summary())

# Auto-save backup on import
try:
    config.save_to_file()
except:
    pass