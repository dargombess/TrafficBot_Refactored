"""
Configuration Manager - Single Source of Truth
Semua pengaturan bot disimpan di sini
"""

class BotConfig:
    """Konfigurasi utama bot - Bisa diubah dari GUI"""
    
    # ============================================
    # FILE PATHS
    # ============================================
    FILE_ARTICLES = ""      # Path ke file artikel.txt
    FILE_PROXIES = ""       # Path ke file proxy.txt
    FILE_REFERRERS = ""     # Path ke file referrer.txt (optional)
    
    # ============================================
    # WORKER SETTINGS
    # ============================================
    MAX_WORKERS = 100       # Maksimal concurrent workers
    TASK_COUNT = 50         # Target jumlah task
    
    # ============================================
    # STEALTH SETTINGS
    # ============================================
    FINGERPRINT_MODE = "Cortex"  # Cortex, Pro, atau JSON
    FINGERPRINT_KEY = ""         # License key untuk mode Pro
    FINGERPRINT_FOLDER = ""      # Folder JSON untuk mode JSON
    WEBRTC_ENABLED = True        # Enable WebRTC leak protection
    TIMEZONE_SYNC = True         # Sync timezone dengan proxy
    USER_AGENT_MODE = "Mixed"    # Mobile Only, Desktop Only, Mixed
    
    # ============================================
    # PROXY SETTINGS
    # ============================================
    PROXY_TYPE = "auto"          # auto, http, socks4, socks5
    MAX_PROXY_LATENCY = 5000     # Maksimal latency (ms)
    CHECK_DUPLICATE_IP = True    # Check IP sudah pernah dipakai
    
    # ============================================
    # TRAFFIC SETTINGS
    # ============================================
    TRAFFIC_MODE = "Hybrid"      # Hybrid atau External
    SEARCH_RATIO = 40            # % search vs social (Hybrid mode)
    
    # ============================================
    # BEHAVIOR SETTINGS
    # ============================================
    TARGET_CTR = 8.0             # Target Click-Through Rate (%)
    SCROLL_MIN = 30              # Minimal scroll count
    SCROLL_MAX = 60              # Maksimal scroll count
    DELAY_MIN = 20               # Minimal delay antar action (detik)
    DELAY_MAX = 30               # Maksimal delay antar action (detik)
    MOUSE_STYLE = "Human Curves" # Human Curves atau Direct Jump
    MANUAL_CLICK = False         # Mode manual click
    
    # ============================================
    # BROWSER SETTINGS
    # ============================================
    HEADLESS = False             # Mode headless
    BROWSER_VISIBILITY = "stealth"  # stealth, ghost, normal
    AUTO_HEADLESS = False        # Auto convert ke headless
    
    # ============================================
    # RETRY SETTINGS
    # ============================================
    MAX_RETRIES = 3              # Maksimal retry per task
    RETRY_DELAY = 5              # Delay antar retry (detik)
    
    # ============================================
    # AI SETTINGS
    # ============================================
    AI_ENABLED = True            # Enable AI engine
    AI_PREDICT_CTR = True        # AI prediksi CTR optimal
    AI_ANOMALY_DETECTION = True  # AI deteksi anomali
    
    # ============================================
    # PERFORMANCE SETTINGS
    # ============================================
    PARALLEL_PROCESSING = True   # Enable parallel processing
    IN_MEMORY_CACHE = True       # Enable in-memory caching
    
    @classmethod
    def to_dict(cls):
        """Convert config ke dictionary"""
        return {
            key: value for key, value in cls.__dict__.items()
            if not key.startswith('_') and not callable(value)
        }
    
    @classmethod
    def update_from_dict(cls, config_dict):
        """Update config dari dictionary"""
        for key, value in config_dict.items():
            if hasattr(cls, key):
                setattr(cls, key, value)
    
    @classmethod
    def reset_to_default(cls):
        """Reset semua ke default values"""
        cls.TASK_COUNT = 50
        cls.TARGET_CTR = 8.0
        cls.SCROLL_MIN = 30
        cls.SCROLL_MAX = 60
        cls.DELAY_MIN = 20
        cls.DELAY_MAX = 30
        cls.MAX_RETRIES = 3
        cls.RETRY_DELAY = 5

# Instance global yang bisa diakses dari mana saja
config = BotConfig()
