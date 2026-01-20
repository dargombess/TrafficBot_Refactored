"""
ADVANCED SETTINGS - TABBED VERSION
Reorganized interface with 6 tabs - Professional dashboard labels
Fully compatible with existing code (has AdvancedSettings alias)
"""

import sys
import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QGroupBox, QFormLayout, QLabel, QLineEdit, QSpinBox,
    QDoubleSpinBox, QComboBox, QCheckBox, QPushButton,
    QFileDialog, QTextEdit, QScrollArea, QMessageBox, QGridLayout
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIntValidator

from bot_config import config
from config_saver import save_config_to_file


class OrganizedSettingsDialog(QDialog):
    """Reorganized settings dialog with 6 tabs and professional labels"""
    
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Advanced Configuration Panel")
        self.setMinimumSize(1000, 750)
        
        self.settings_widgets = {}
        self.setup_ui()
        self.load_current_settings()
        
    def setup_ui(self):
        """Setup the tabbed interface"""
        main_layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("TrafficBot Configuration Center")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px; color: #2c3e50;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Add all tabs
        self.tab_widget.addTab(self.create_basic_tab(), "Basic & Resource")
        self.tab_widget.addTab(self.create_browser_tab(), "Browser & Fingerprint")
        self.tab_widget.addTab(self.create_captcha_tab(), "CAPTCHA & Proxy")
        self.tab_widget.addTab(self.create_ai_tab(), "AI & Behavior")
        self.tab_widget.addTab(self.create_navigation_tab(), "Deep Navigation")
        self.tab_widget.addTab(self.create_advanced_tab(), "Advanced")
        
        main_layout.addWidget(self.tab_widget)
        
        # Status bar
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #7f8c8d; font-size: 10px; padding: 5px;")
        main_layout.addWidget(self.status_label)
        
        # Add control buttons
        self.setup_control_buttons(main_layout)
        
        # Apply styling
        self.setup_professional_styling()
    
    def create_basic_tab(self):
        """Tab 1: Basic & Resource settings"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # --- Runtime Configuration ---
        runtime_group = QGroupBox("Runtime Configuration")
        runtime_layout = QGridLayout()
        
        runtime_layout.addWidget(QLabel("Concurrent Workers:"), 0, 0)
        self.settings_widgets['WORKER_COUNT'] = QSpinBox()
        self.settings_widgets['WORKER_COUNT'].setRange(1, 100)
        runtime_layout.addWidget(self.settings_widgets['WORKER_COUNT'], 0, 1)
        
        runtime_layout.addWidget(QLabel("Maximum Retry Attempts:"), 1, 0)
        self.settings_widgets['MAX_RETRIES'] = QSpinBox()
        self.settings_widgets['MAX_RETRIES'].setRange(0, 20)
        runtime_layout.addWidget(self.settings_widgets['MAX_RETRIES'], 1, 1)
        
        runtime_layout.addWidget(QLabel("Request Timeout Duration:"), 2, 0)
        self.settings_widgets['REQUEST_TIMEOUT'] = QSpinBox()
        self.settings_widgets['REQUEST_TIMEOUT'].setRange(10, 600)
        self.settings_widgets['REQUEST_TIMEOUT'].setSuffix(" seconds")
        runtime_layout.addWidget(self.settings_widgets['REQUEST_TIMEOUT'], 2, 1)
        
        runtime_group.setLayout(runtime_layout)
        scroll_layout.addWidget(runtime_group)
        
        # --- System Resources ---
        resource_group = QGroupBox("System Resources Allocation")
        resource_layout = QGridLayout()
        
        resource_layout.addWidget(QLabel("CPU Usage Limit:"), 0, 0)
        self.settings_widgets['MAX_CPU_PERCENT'] = QSpinBox()
        self.settings_widgets['MAX_CPU_PERCENT'].setRange(10, 100)
        self.settings_widgets['MAX_CPU_PERCENT'].setSuffix(" %")
        resource_layout.addWidget(self.settings_widgets['MAX_CPU_PERCENT'], 0, 1)
        
        resource_layout.addWidget(QLabel("Memory Allocation Limit:"), 1, 0)
        self.settings_widgets['MAX_MEMORY_MB'] = QSpinBox()
        self.settings_widgets['MAX_MEMORY_MB'].setRange(100, 16384)
        self.settings_widgets['MAX_MEMORY_MB'].setSuffix(" MB")
        resource_layout.addWidget(self.settings_widgets['MAX_MEMORY_MB'], 1, 1)
        
        resource_layout.addWidget(QLabel("Max Workers per Proxy:"), 2, 0)
        self.settings_widgets['MAX_WORKERS_PER_PROXY'] = QSpinBox()
        self.settings_widgets['MAX_WORKERS_PER_PROXY'].setRange(1, 20)
        resource_layout.addWidget(self.settings_widgets['MAX_WORKERS_PER_PROXY'], 2, 1)
        
        resource_group.setLayout(resource_layout)
        scroll_layout.addWidget(resource_group)
        
        # --- Monitoring & Logging ---
        logging_group = QGroupBox("Monitoring & Logging")
        logging_layout = QGridLayout()
        
        logging_layout.addWidget(QLabel("Logging Verbosity Level:"), 0, 0)
        self.settings_widgets['LOG_LEVEL'] = QComboBox()
        self.settings_widgets['LOG_LEVEL'].addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        logging_layout.addWidget(self.settings_widgets['LOG_LEVEL'], 0, 1)
        
        self.settings_widgets['LOG_TO_FILE'] = QCheckBox("Enable persistent log storage")
        logging_layout.addWidget(self.settings_widgets['LOG_TO_FILE'], 1, 0, 1, 2)
        
        logging_layout.addWidget(QLabel("Log File Storage Path:"), 2, 0)
        self.settings_widgets['LOG_FILE_PATH'] = self.create_file_selector("Select log storage location...", is_save=True)
        logging_layout.addWidget(self.settings_widgets['LOG_FILE_PATH'], 2, 1)
        
        logging_layout.addWidget(QLabel("Session History Capacity:"), 3, 0)
        self.settings_widgets['HISTORY_SIZE'] = QSpinBox()
        self.settings_widgets['HISTORY_SIZE'].setRange(100, 50000)
        logging_layout.addWidget(self.settings_widgets['HISTORY_SIZE'], 3, 1)
        
        logging_group.setLayout(logging_layout)
        scroll_layout.addWidget(logging_group)
        
        # --- Data Management ---
        data_group = QGroupBox("Data Management")
        data_layout = QGridLayout()
        
        data_layout.addWidget(QLabel("Database Storage Location:"), 0, 0)
        self.settings_widgets['DB_PATH'] = self.create_file_selector("Select database storage...", is_save=True)
        data_layout.addWidget(self.settings_widgets['DB_PATH'], 0, 1)
        
        self.settings_widgets['AUTO_BACKUP'] = QCheckBox("Enable automatic backup system")
        data_layout.addWidget(self.settings_widgets['AUTO_BACKUP'], 1, 0, 1, 2)
        
        data_layout.addWidget(QLabel("Backup Interval Frequency:"), 2, 0)
        self.settings_widgets['BACKUP_INTERVAL'] = QSpinBox()
        self.settings_widgets['BACKUP_INTERVAL'].setRange(1, 720)
        self.settings_widgets['BACKUP_INTERVAL'].setSuffix(" hours")
        data_layout.addWidget(self.settings_widgets['BACKUP_INTERVAL'], 2, 1)
        
        data_group.setLayout(data_layout)
        scroll_layout.addWidget(data_group)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        return widget
    
    def create_browser_tab(self):
        """Tab 2: Browser & Fingerprint settings"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # --- Browser Engine ---
        browser_group = QGroupBox("Browser Engine Configuration")
        browser_layout = QGridLayout()
        
        self.settings_widgets['USE_UNDETECTED_CHROME'] = QCheckBox("Enable anti-detection browser engine")
        browser_layout.addWidget(self.settings_widgets['USE_UNDETECTED_CHROME'], 0, 0, 1, 2)
        
        self.settings_widgets['HEADLESS'] = QCheckBox("Enable background execution mode")
        browser_layout.addWidget(self.settings_widgets['HEADLESS'], 1, 0, 1, 2)
        
        browser_layout.addWidget(QLabel("Browser Window Width:"), 2, 0)
        self.settings_widgets['BROWSER_WIDTH'] = QSpinBox()
        self.settings_widgets['BROWSER_WIDTH'].setRange(800, 3840)
        self.settings_widgets['BROWSER_WIDTH'].setValue(1366)
        browser_layout.addWidget(self.settings_widgets['BROWSER_WIDTH'], 2, 1)
        
        browser_layout.addWidget(QLabel("Browser Window Height:"), 3, 0)
        self.settings_widgets['BROWSER_HEIGHT'] = QSpinBox()
        self.settings_widgets['BROWSER_HEIGHT'].setRange(600, 2160)
        self.settings_widgets['BROWSER_HEIGHT'].setValue(768)
        browser_layout.addWidget(self.settings_widgets['BROWSER_HEIGHT'], 3, 1)
        
        browser_group.setLayout(browser_layout)
        scroll_layout.addWidget(browser_group)
        
        # --- Privacy & Security ---
        privacy_group = QGroupBox("Privacy & Security Features")
        privacy_layout = QGridLayout()
        
        self.settings_widgets['WEBRTC_PROTECTION'] = QCheckBox("Enable WebRTC leak protection")
        privacy_layout.addWidget(self.settings_widgets['WEBRTC_PROTECTION'], 0, 0, 1, 2)
        
        self.settings_widgets['WEBGL_SPOOFING'] = QCheckBox("Enable canvas fingerprint protection")
        privacy_layout.addWidget(self.settings_widgets['WEBGL_SPOOFING'], 1, 0, 1, 2)
        
        self.settings_widgets['TIMEZONE_SYNC'] = QCheckBox("Synchronize browser timezone")
        privacy_layout.addWidget(self.settings_widgets['TIMEZONE_SYNC'], 2, 0, 1, 2)
        
        privacy_group.setLayout(privacy_layout)
        scroll_layout.addWidget(privacy_group)
        
        # --- Browser Identity ---
        identity_group = QGroupBox("Browser Identity Management")
        identity_layout = QGridLayout()
        
        identity_layout.addWidget(QLabel("Browser Profile Generation:"), 0, 0)
        self.settings_widgets['FINGERPRINT_MODE'] = QComboBox()
        self.settings_widgets['FINGERPRINT_MODE'].addItems(["Cortex", "JSON", "Random", "Mixed"])
        identity_layout.addWidget(self.settings_widgets['FINGERPRINT_MODE'], 0, 1)
        
        identity_layout.addWidget(QLabel("Profile Storage Directory:"), 1, 0)
        self.settings_widgets['FINGERPRINT_FOLDER'] = self.create_file_selector("Select profile directory...", is_folder=True)
        identity_layout.addWidget(self.settings_widgets['FINGERPRINT_FOLDER'], 1, 1)
        
        identity_layout.addWidget(QLabel("User Agent Strategy:"), 2, 0)
        self.settings_widgets['USER_AGENT_MODE'] = QComboBox()
        self.settings_widgets['USER_AGENT_MODE'].addItems(["Mixed", "Desktop Only", "Mobile Only", "Random"])
        identity_layout.addWidget(self.settings_widgets['USER_AGENT_MODE'], 2, 1)
        
        identity_group.setLayout(identity_layout)
        scroll_layout.addWidget(identity_group)
        
        # --- Interaction Behavior ---
        interaction_group = QGroupBox("Interaction Behavior")
        interaction_layout = QGridLayout()
        
        interaction_layout.addWidget(QLabel("Mouse Movement Style:"), 0, 0)
        self.settings_widgets['MOUSE_STYLE'] = QComboBox()
        self.settings_widgets['MOUSE_STYLE'].addItems(["Human Curves", "Linear", "Random", "Natural"])
        interaction_layout.addWidget(self.settings_widgets['MOUSE_STYLE'], 0, 1)
        
        interaction_layout.addWidget(QLabel("Default Wait Time:"), 1, 0)
        self.settings_widgets['DEFAULT_WAIT_TIME'] = QDoubleSpinBox()
        self.settings_widgets['DEFAULT_WAIT_TIME'].setRange(1.0, 30.0)
        self.settings_widgets['DEFAULT_WAIT_TIME'].setSuffix(" seconds")
        self.settings_widgets['DEFAULT_WAIT_TIME'].setValue(3.0)
        interaction_layout.addWidget(self.settings_widgets['DEFAULT_WAIT_TIME'], 1, 1)
        
        interaction_group.setLayout(interaction_layout)
        scroll_layout.addWidget(interaction_group)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        return widget
    
    def create_captcha_tab(self):
        """Tab 3: CAPTCHA & Proxy settings"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # --- CAPTCHA Resolution ---
        captcha_group = QGroupBox("CAPTCHA Resolution Service")
        captcha_layout = QGridLayout()
        
        self.settings_widgets['CAPTCHA_SOLVER_ENABLED'] = QCheckBox("Enable automated CAPTCHA solving")
        captcha_layout.addWidget(self.settings_widgets['CAPTCHA_SOLVER_ENABLED'], 0, 0, 1, 2)
        
        captcha_layout.addWidget(QLabel("Service Provider:"), 1, 0)
        self.settings_widgets['CAPTCHA_SOLVER_SERVICE'] = QComboBox()
        self.settings_widgets['CAPTCHA_SOLVER_SERVICE'].addItems(["2Captcha", "Anti-Captcha", "CapMonster", "Custom API"])
        captcha_layout.addWidget(self.settings_widgets['CAPTCHA_SOLVER_SERVICE'], 1, 1)
        
        captcha_layout.addWidget(QLabel("Service API Credentials:"), 2, 0)
        self.settings_widgets['CAPTCHA_API_KEY'] = QLineEdit()
        self.settings_widgets['CAPTCHA_API_KEY'].setEchoMode(QLineEdit.Password)
        captcha_layout.addWidget(self.settings_widgets['CAPTCHA_API_KEY'], 2, 1)
        
        captcha_layout.addWidget(QLabel("Maximum Resolution Attempts:"), 3, 0)
        self.settings_widgets['CAPTCHA_MAX_RETRY'] = QSpinBox()
        self.settings_widgets['CAPTCHA_MAX_RETRY'].setRange(1, 10)
        captcha_layout.addWidget(self.settings_widgets['CAPTCHA_MAX_RETRY'], 3, 1)
        
        self.settings_widgets['AUTO_CAPTCHA_LEARN'] = QCheckBox("Enable pattern learning system")
        captcha_layout.addWidget(self.settings_widgets['AUTO_CAPTCHA_LEARN'], 4, 0, 1, 2)
        
        captcha_group.setLayout(captcha_layout)
        scroll_layout.addWidget(captcha_group)
        
        # --- Proxy Network ---
        proxy_group = QGroupBox("Proxy Network Configuration")
        proxy_layout = QGridLayout()
        
        proxy_layout.addWidget(QLabel("Proxy Protocol:"), 0, 0)
        self.settings_widgets['PROXY_TYPE'] = QComboBox()
        self.settings_widgets['PROXY_TYPE'].addItems(["http", "https", "socks5", "socks4", "auto"])
        proxy_layout.addWidget(self.settings_widgets['PROXY_TYPE'], 0, 1)
        
        proxy_layout.addWidget(QLabel("Proxy Server List:"), 1, 0)
        self.settings_widgets['PROXY_FILE_PATH'] = self.create_file_selector("Select proxy list file...")
        proxy_layout.addWidget(self.settings_widgets['PROXY_FILE_PATH'], 1, 1)
        
        proxy_layout.addWidget(QLabel("Rotation Strategy:"), 2, 0)
        self.settings_widgets['PROXY_ROTATION'] = QComboBox()
        self.settings_widgets['PROXY_ROTATION'].addItems(["Per Session", "Per Request", "Random", "Sequential", "Load Balanced"])
        proxy_layout.addWidget(self.settings_widgets['PROXY_ROTATION'], 2, 1)
        
        proxy_layout.addWidget(QLabel("Proxy Test URL:"), 3, 0)
        self.settings_widgets['PROXY_TEST_URL'] = QLineEdit()
        self.settings_widgets['PROXY_TEST_URL'].setText("https://api.ipify.org")
        proxy_layout.addWidget(self.settings_widgets['PROXY_TEST_URL'], 3, 1)
        
        proxy_group.setLayout(proxy_layout)
        scroll_layout.addWidget(proxy_group)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        return widget
    
    def create_ai_tab(self):
        """Tab 4: AI & Behavior settings"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # --- Intelligence Engine ---
        ai_group = QGroupBox("Intelligence Engine")
        ai_layout = QGridLayout()
        
        self.settings_widgets['AI_ENABLED'] = QCheckBox("Enable intelligent behavior engine")
        ai_layout.addWidget(self.settings_widgets['AI_ENABLED'], 0, 0, 1, 2)
        
        ai_layout.addWidget(QLabel("AI Model Configuration:"), 1, 0)
        self.settings_widgets['AI_MODEL_PATH'] = self.create_file_selector("Select AI model file...")
        ai_layout.addWidget(self.settings_widgets['AI_MODEL_PATH'], 1, 1)
        
        self.settings_widgets['AI_PREDICT_CTR'] = QCheckBox("Enable CTR prediction system")
        ai_layout.addWidget(self.settings_widgets['AI_PREDICT_CTR'], 2, 0, 1, 2)
        
        self.settings_widgets['AI_OPTIMIZE_PROXY'] = QCheckBox("Enable proxy optimization")
        ai_layout.addWidget(self.settings_widgets['AI_OPTIMIZE_PROXY'], 3, 0, 1, 2)
        
        ai_group.setLayout(ai_layout)
        scroll_layout.addWidget(ai_group)
        
        # --- Human Behavior Simulation ---
        behavior_group = QGroupBox("Human Behavior Simulation")
        behavior_layout = QGridLayout()
        
        behavior_layout.addWidget(QLabel("Minimum Scroll Events:"), 0, 0)
        self.settings_widgets['SCROLL_MIN'] = QSpinBox()
        self.settings_widgets['SCROLL_MIN'].setRange(5, 100)
        behavior_layout.addWidget(self.settings_widgets['SCROLL_MIN'], 0, 1)
        
        behavior_layout.addWidget(QLabel("Maximum Scroll Events:"), 1, 0)
        self.settings_widgets['SCROLL_MAX'] = QSpinBox()
        self.settings_widgets['SCROLL_MAX'].setRange(10, 200)
        behavior_layout.addWidget(self.settings_widgets['SCROLL_MAX'], 1, 1)
        
        behavior_layout.addWidget(QLabel("Minimum Reading Delay:"), 2, 0)
        self.settings_widgets['DELAY_MIN'] = QDoubleSpinBox()
        self.settings_widgets['DELAY_MIN'].setRange(1.0, 60.0)
        self.settings_widgets['DELAY_MIN'].setSuffix(" seconds")
        behavior_layout.addWidget(self.settings_widgets['DELAY_MIN'], 2, 1)
        
        behavior_layout.addWidget(QLabel("Maximum Reading Delay:"), 3, 0)
        self.settings_widgets['DELAY_MAX'] = QDoubleSpinBox()
        self.settings_widgets['DELAY_MAX'].setRange(5.0, 180.0)
        self.settings_widgets['DELAY_MAX'].setSuffix(" seconds")
        behavior_layout.addWidget(self.settings_widgets['DELAY_MAX'], 3, 1)
        
        behavior_layout.addWidget(QLabel("Target Click-Through Rate:"), 4, 0)
        self.settings_widgets['TARGET_CTR'] = QDoubleSpinBox()
        self.settings_widgets['TARGET_CTR'].setRange(0.1, 50.0)
        self.settings_widgets['TARGET_CTR'].setSuffix(" %")
        behavior_layout.addWidget(self.settings_widgets['TARGET_CTR'], 4, 1)
        
        behavior_layout.addWidget(QLabel("Random Click Probability:"), 5, 0)
        self.settings_widgets['RANDOM_CLICK_PROB'] = QDoubleSpinBox()
        self.settings_widgets['RANDOM_CLICK_PROB'].setRange(0.0, 1.0)
        self.settings_widgets['RANDOM_CLICK_PROB'].setSingleStep(0.05)
        behavior_layout.addWidget(self.settings_widgets['RANDOM_CLICK_PROB'], 5, 1)
        
        behavior_group.setLayout(behavior_layout)
        scroll_layout.addWidget(behavior_group)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        return widget
    
    def create_navigation_tab(self):
        """Tab 5: Deep Navigation settings"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # --- Navigation Engine ---
        nav_group = QGroupBox("Navigation Engine")
        nav_layout = QGridLayout()
        
        self.settings_widgets['DEEP_NAVIGATION_ENABLED'] = QCheckBox("Enable multi-page navigation system")
        nav_layout.addWidget(self.settings_widgets['DEEP_NAVIGATION_ENABLED'], 0, 0, 1, 2)
        
        nav_layout.addWidget(QLabel("Maximum Page Depth:"), 1, 0)
        self.settings_widgets['NAVIGATION_MAX_DEPTH'] = QSpinBox()
        self.settings_widgets['NAVIGATION_MAX_DEPTH'].setRange(1, 20)
        nav_layout.addWidget(self.settings_widgets['NAVIGATION_MAX_DEPTH'], 1, 1)
        
        nav_layout.addWidget(QLabel("Maximum Pages per Session:"), 2, 0)
        self.settings_widgets['NAVIGATION_MAX_PAGES'] = QSpinBox()
        self.settings_widgets['NAVIGATION_MAX_PAGES'].setRange(1, 100)
        nav_layout.addWidget(self.settings_widgets['NAVIGATION_MAX_PAGES'], 2, 1)
        
        nav_layout.addWidget(QLabel("Minimum Time per Page:"), 3, 0)
        self.settings_widgets['MIN_TIME_PER_PAGE'] = QDoubleSpinBox()
        self.settings_widgets['MIN_TIME_PER_PAGE'].setRange(5.0, 300.0)
        self.settings_widgets['MIN_TIME_PER_PAGE'].setSuffix(" seconds")
        nav_layout.addWidget(self.settings_widgets['MIN_TIME_PER_PAGE'], 3, 1)
        
        nav_group.setLayout(nav_layout)
        scroll_layout.addWidget(nav_group)
        
        # --- Link Selection Rules ---
        rules_group = QGroupBox("Link Selection Rules")
        rules_layout = QGridLayout()
        
        self.settings_widgets['NAV_INTERNAL_ONLY'] = QCheckBox("Follow internal links only")
        rules_layout.addWidget(self.settings_widgets['NAV_INTERNAL_ONLY'], 0, 0, 1, 2)
        
        self.settings_widgets['NAV_AVOID_EXTERNAL'] = QCheckBox("Avoid external domain links")
        rules_layout.addWidget(self.settings_widgets['NAV_AVOID_EXTERNAL'], 1, 0, 1, 2)
        
        rules_layout.addWidget(QLabel("URL Patterns to Avoid:"), 2, 0)
        self.settings_widgets['NAV_AVOID_PATTERNS'] = QTextEdit()
        self.settings_widgets['NAV_AVOID_PATTERNS'].setMaximumHeight(80)
        self.settings_widgets['NAV_AVOID_PATTERNS'].setPlaceholderText("Enter URL patterns to avoid (one per line)\nExample: logout, admin, login")
        rules_layout.addWidget(self.settings_widgets['NAV_AVOID_PATTERNS'], 2, 1)
        
        rules_layout.addWidget(QLabel("Preferred Link Keywords:"), 3, 0)
        self.settings_widgets['NAV_PREFERRED_KEYWORDS'] = QTextEdit()
        self.settings_widgets['NAV_PREFERRED_KEYWORDS'].setMaximumHeight(80)
        self.settings_widgets['NAV_PREFERRED_KEYWORDS'].setPlaceholderText("Enter preferred keywords (one per line)\nExample: blog, article, news, post")
        rules_layout.addWidget(self.settings_widgets['NAV_PREFERRED_KEYWORDS'], 3, 1)
        
        rules_group.setLayout(rules_layout)
        scroll_layout.addWidget(rules_group)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        return widget
    
    def create_advanced_tab(self):
        """Tab 6: Advanced settings"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # --- Expert Configuration ---
        expert_group = QGroupBox("Expert Configuration")
        expert_layout = QGridLayout()
        
        self.settings_widgets['DEBUG_MODE'] = QCheckBox("Enable debug mode")
        expert_layout.addWidget(self.settings_widgets['DEBUG_MODE'], 0, 0, 1, 2)
        
        self.settings_widgets['DEV_TOOLS'] = QCheckBox("Enable developer tools")
        expert_layout.addWidget(self.settings_widgets['DEV_TOOLS'], 1, 0, 1, 2)
        
        self.settings_widgets['VERBOSE_LOGGING'] = QCheckBox("Enable verbose logging")
        expert_layout.addWidget(self.settings_widgets['VERBOSE_LOGGING'], 2, 0, 1, 2)
        
        self.settings_widgets['ENABLE_METRICS'] = QCheckBox("Enable performance metrics collection")
        expert_layout.addWidget(self.settings_widgets['ENABLE_METRICS'], 3, 0, 1, 2)
        
        expert_group.setLayout(expert_layout)
        scroll_layout.addWidget(expert_group)
        
        # --- Experimental Features ---
        experimental_group = QGroupBox("Experimental Features")
        experimental_layout = QGridLayout()
        
        self.settings_widgets['BETA_FEATURES'] = QCheckBox("Enable beta features")
        experimental_layout.addWidget(self.settings_widgets['BETA_FEATURES'], 0, 0, 1, 2)
        
        self.settings_widgets['EXPERIMENTAL_AI'] = QCheckBox("Enable experimental AI features")
        experimental_layout.addWidget(self.settings_widgets['EXPERIMENTAL_AI'], 1, 0, 1, 2)
        
        experimental_layout.addWidget(QLabel("Custom JavaScript Injection:"), 2, 0)
        self.settings_widgets['CUSTOM_JS_INJECTION'] = QTextEdit()
        self.settings_widgets['CUSTOM_JS_INJECTION'].setMaximumHeight(100)
        self.settings_widgets['CUSTOM_JS_INJECTION'].setPlaceholderText("Enter custom JavaScript code for browser injection")
        experimental_layout.addWidget(self.settings_widgets['CUSTOM_JS_INJECTION'], 2, 1)
        
        experimental_group.setLayout(experimental_layout)
        scroll_layout.addWidget(experimental_group)
        
        # --- System Tweaks ---
        tweaks_group = QGroupBox("System Tweaks")
        tweaks_layout = QGridLayout()
        
        tweaks_layout.addWidget(QLabel("Browser Cleanup Interval:"), 0, 0)
        self.settings_widgets['BROWSER_CLEANUP_INTERVAL'] = QSpinBox()
        self.settings_widgets['BROWSER_CLEANUP_INTERVAL'].setRange(1, 24)
        self.settings_widgets['BROWSER_CLEANUP_INTERVAL'].setSuffix(" hours")
        tweaks_layout.addWidget(self.settings_widgets['BROWSER_CLEANUP_INTERVAL'], 0, 1)
        
        tweaks_layout.addWidget(QLabel("Cache Size Limit:"), 1, 0)
        self.settings_widgets['CACHE_SIZE_LIMIT'] = QSpinBox()
        self.settings_widgets['CACHE_SIZE_LIMIT'].setRange(50, 2048)
        self.settings_widgets['CACHE_SIZE_LIMIT'].setSuffix(" MB")
        tweaks_layout.addWidget(self.settings_widgets['CACHE_SIZE_LIMIT'], 1, 1)
        
        tweaks_group.setLayout(tweaks_layout)
        scroll_layout.addWidget(tweaks_group)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        return widget
    
    def setup_control_buttons(self, main_layout):
        """Setup control buttons with professional labels"""
        button_layout = QHBoxLayout()
        
        self.apply_btn = QPushButton("Apply Changes")
        self.apply_btn.clicked.connect(self.apply_settings)
        self.apply_btn.setToolTip("Apply changes without closing window")
        
        self.save_btn = QPushButton("Save & Close")
        self.save_btn.clicked.connect(self.save_and_close)
        self.save_btn.setToolTip("Save changes and close window")
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setToolTip("Discard changes and close window")
        
        self.reset_btn = QPushButton("Restore Defaults")
        self.reset_btn.clicked.connect(self.reset_to_defaults)
        self.reset_btn.setToolTip("Restore all settings to default values")
        
        self.test_btn = QPushButton("Test Settings")
        self.test_btn.clicked.connect(self.test_settings)
        self.test_btn.setToolTip("Test current settings configuration")
        
        button_layout.addWidget(self.reset_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.test_btn)
        button_layout.addWidget(self.apply_btn)
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        main_layout.addLayout(button_layout)
    
    def create_file_selector(self, dialog_title, is_save=False, is_folder=False):
        """Create file selector widget"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        line_edit = QLineEdit()
        browse_btn = QPushButton("Browse...")
        
        def browse_action():
            if is_folder:
                folder = QFileDialog.getExistingDirectory(self, dialog_title, "", QFileDialog.ShowDirsOnly)
                if folder:
                    line_edit.setText(folder)
            elif is_save:
                filename, _ = QFileDialog.getSaveFileName(self, dialog_title, "", "All Files (*)")
                if filename:
                    line_edit.setText(filename)
            else:
                filename, _ = QFileDialog.getOpenFileName(self, dialog_title, "", "All Files (*)")
                if filename:
                    line_edit.setText(filename)
        
        browse_btn.clicked.connect(browse_action)
        
        layout.addWidget(line_edit, 1)
        layout.addWidget(browse_btn)
        
        return widget
    
    def load_current_settings(self):
        """Load current settings from config"""
        try:
            # Define default values for all settings
            defaults = {
                # Basic & Resource
                'WORKER_COUNT': 5,
                'MAX_RETRIES': 3,
                'REQUEST_TIMEOUT': 30,
                'MAX_CPU_PERCENT': 80,
                'MAX_MEMORY_MB': 2048,
                'MAX_WORKERS_PER_PROXY': 3,
                'LOG_LEVEL': 'INFO',
                'LOG_TO_FILE': False,
                'LOG_FILE_PATH': '',
                'HISTORY_SIZE': 1000,
                'DB_PATH': 'trafficbot.db',
                'AUTO_BACKUP': True,
                'BACKUP_INTERVAL': 24,
                
                # Browser & Fingerprint
                'USE_UNDETECTED_CHROME': True,
                'HEADLESS': False,
                'BROWSER_WIDTH': 1366,
                'BROWSER_HEIGHT': 768,
                'WEBRTC_PROTECTION': True,
                'WEBGL_SPOOFING': True,
                'TIMEZONE_SYNC': True,
                'FINGERPRINT_MODE': 'Cortex',
                'FINGERPRINT_FOLDER': '',
                'USER_AGENT_MODE': 'Mixed',
                'MOUSE_STYLE': 'Human Curves',
                'DEFAULT_WAIT_TIME': 3.0,
                
                # CAPTCHA & Proxy
                'CAPTCHA_SOLVER_ENABLED': False,
                'CAPTCHA_SOLVER_SERVICE': '2Captcha',
                'CAPTCHA_API_KEY': '',
                'CAPTCHA_MAX_RETRY': 3,
                'AUTO_CAPTCHA_LEARN': True,
                'PROXY_TYPE': 'http',
                'PROXY_FILE_PATH': '',
                'PROXY_ROTATION': 'Per Session',
                'PROXY_TEST_URL': 'https://api.ipify.org',
                
                # AI & Behavior
                'AI_ENABLED': False,
                'AI_MODEL_PATH': '',
                'AI_PREDICT_CTR': True,
                'AI_OPTIMIZE_PROXY': True,
                'SCROLL_MIN': 10,
                'SCROLL_MAX': 30,
                'DELAY_MIN': 5.0,
                'DELAY_MAX': 15.0,
                'TARGET_CTR': 8.0,
                'RANDOM_CLICK_PROB': 0.1,
                
                # Deep Navigation
                'DEEP_NAVIGATION_ENABLED': True,
                'NAVIGATION_MAX_DEPTH': 3,
                'NAVIGATION_MAX_PAGES': 10,
                'MIN_TIME_PER_PAGE': 30.0,
                'NAV_INTERNAL_ONLY': True,
                'NAV_AVOID_EXTERNAL': True,
                'NAV_AVOID_PATTERNS': '',
                'NAV_PREFERRED_KEYWORDS': '',
                
                # Advanced
                'DEBUG_MODE': False,
                'DEV_TOOLS': False,
                'VERBOSE_LOGGING': False,
                'ENABLE_METRICS': True,
                'BETA_FEATURES': False,
                'EXPERIMENTAL_AI': False,
                'CUSTOM_JS_INJECTION': '',
                'BROWSER_CLEANUP_INTERVAL': 6,
                'CACHE_SIZE_LIMIT': 512,
            }
            
            # Load each setting
            for key, default_value in defaults.items():
                try:
                    # Get value from config or use default
                    config_value = getattr(config, key, default_value)
                    
                    # Set widget value based on type
                    widget = self.settings_widgets.get(key)
                    if widget:
                        if isinstance(widget, QSpinBox):
                            widget.setValue(int(config_value))
                        elif isinstance(widget, QDoubleSpinBox):
                            widget.setValue(float(config_value))
                        elif isinstance(widget, QLineEdit):
                            widget.setText(str(config_value))
                        elif isinstance(widget, QComboBox):
                            index = widget.findText(str(config_value))
                            if index >= 0:
                                widget.setCurrentIndex(index)
                        elif isinstance(widget, QCheckBox):
                            widget.setChecked(bool(config_value))
                        elif isinstance(widget, QTextEdit):
                            widget.setText(str(config_value))
                except Exception as e:
                    print(f"Warning: Failed to load setting {key}: {e}")
                    continue
            
            self.status_label.setText("Settings loaded successfully")
            
        except Exception as e:
            QMessageBox.warning(self, "Load Error", f"Failed to load settings: {str(e)}")
            self.status_label.setText("Error loading settings")
    
    def apply_settings(self):
        """Apply settings to config"""
        try:
            # Collect all settings
            new_settings = {}
            
            # Basic & Resource
            new_settings['WORKER_COUNT'] = self.settings_widgets['WORKER_COUNT'].value()
            new_settings['MAX_RETRIES'] = self.settings_widgets['MAX_RETRIES'].value()
            new_settings['REQUEST_TIMEOUT'] = self.settings_widgets['REQUEST_TIMEOUT'].value()
            new_settings['MAX_CPU_PERCENT'] = self.settings_widgets['MAX_CPU_PERCENT'].value()
            new_settings['MAX_MEMORY_MB'] = self.settings_widgets['MAX_MEMORY_MB'].value()
            new_settings['MAX_WORKERS_PER_PROXY'] = self.settings_widgets['MAX_WORKERS_PER_PROXY'].value()
            new_settings['LOG_LEVEL'] = self.settings_widgets['LOG_LEVEL'].currentText()
            new_settings['LOG_TO_FILE'] = self.settings_widgets['LOG_TO_FILE'].isChecked()
            new_settings['LOG_FILE_PATH'] = self.settings_widgets['LOG_FILE_PATH'].layout().itemAt(0).widget().text()
            new_settings['HISTORY_SIZE'] = self.settings_widgets['HISTORY_SIZE'].value()
            new_settings['DB_PATH'] = self.settings_widgets['DB_PATH'].layout().itemAt(0).widget().text()
            new_settings['AUTO_BACKUP'] = self.settings_widgets['AUTO_BACKUP'].isChecked()
            new_settings['BACKUP_INTERVAL'] = self.settings_widgets['BACKUP_INTERVAL'].value()
            
            # Browser & Fingerprint
            new_settings['USE_UNDETECTED_CHROME'] = self.settings_widgets['USE_UNDETECTED_CHROME'].isChecked()
            new_settings['HEADLESS'] = self.settings_widgets['HEADLESS'].isChecked()
            new_settings['BROWSER_WIDTH'] = self.settings_widgets['BROWSER_WIDTH'].value()
            new_settings['BROWSER_HEIGHT'] = self.settings_widgets['BROWSER_HEIGHT'].value()
            new_settings['WEBRTC_PROTECTION'] = self.settings_widgets['WEBRTC_PROTECTION'].isChecked()
            new_settings['WEBGL_SPOOFING'] = self.settings_widgets['WEBGL_SPOOFING'].isChecked()
            new_settings['TIMEZONE_SYNC'] = self.settings_widgets['TIMEZONE_SYNC'].isChecked()
            new_settings['FINGERPRINT_MODE'] = self.settings_widgets['FINGERPRINT_MODE'].currentText()
            new_settings['FINGERPRINT_FOLDER'] = self.settings_widgets['FINGERPRINT_FOLDER'].layout().itemAt(0).widget().text()
            new_settings['USER_AGENT_MODE'] = self.settings_widgets['USER_AGENT_MODE'].currentText()
            new_settings['MOUSE_STYLE'] = self.settings_widgets['MOUSE_STYLE'].currentText()
            new_settings['DEFAULT_WAIT_TIME'] = self.settings_widgets['DEFAULT_WAIT_TIME'].value()
            
            # CAPTCHA & Proxy
            new_settings['CAPTCHA_SOLVER_ENABLED'] = self.settings_widgets['CAPTCHA_SOLVER_ENABLED'].isChecked()
            new_settings['CAPTCHA_SOLVER_SERVICE'] = self.settings_widgets['CAPTCHA_SOLVER_SERVICE'].currentText()
            new_settings['CAPTCHA_API_KEY'] = self.settings_widgets['CAPTCHA_API_KEY'].text()
            new_settings['CAPTCHA_MAX_RETRY'] = self.settings_widgets['CAPTCHA_MAX_RETRY'].value()
            new_settings['AUTO_CAPTCHA_LEARN'] = self.settings_widgets['AUTO_CAPTCHA_LEARN'].isChecked()
            new_settings['PROXY_TYPE'] = self.settings_widgets['PROXY_TYPE'].currentText()
            new_settings['PROXY_FILE_PATH'] = self.settings_widgets['PROXY_FILE_PATH'].layout().itemAt(0).widget().text()
            new_settings['PROXY_ROTATION'] = self.settings_widgets['PROXY_ROTATION'].currentText()
            new_settings['PROXY_TEST_URL'] = self.settings_widgets['PROXY_TEST_URL'].text()
            
            # AI & Behavior
            new_settings['AI_ENABLED'] = self.settings_widgets['AI_ENABLED'].isChecked()
            new_settings['AI_MODEL_PATH'] = self.settings_widgets['AI_MODEL_PATH'].layout().itemAt(0).widget().text()
            new_settings['AI_PREDICT_CTR'] = self.settings_widgets['AI_PREDICT_CTR'].isChecked()
            new_settings['AI_OPTIMIZE_PROXY'] = self.settings_widgets['AI_OPTIMIZE_PROXY'].isChecked()
            new_settings['SCROLL_MIN'] = self.settings_widgets['SCROLL_MIN'].value()
            new_settings['SCROLL_MAX'] = self.settings_widgets['SCROLL_MAX'].value()
            new_settings['DELAY_MIN'] = self.settings_widgets['DELAY_MIN'].value()
            new_settings['DELAY_MAX'] = self.settings_widgets['DELAY_MAX'].value()
            new_settings['TARGET_CTR'] = self.settings_widgets['TARGET_CTR'].value()
            new_settings['RANDOM_CLICK_PROB'] = self.settings_widgets['RANDOM_CLICK_PROB'].value()
            
            # Deep Navigation
            new_settings['DEEP_NAVIGATION_ENABLED'] = self.settings_widgets['DEEP_NAVIGATION_ENABLED'].isChecked()
            new_settings['NAVIGATION_MAX_DEPTH'] = self.settings_widgets['NAVIGATION_MAX_DEPTH'].value()
            new_settings['NAVIGATION_MAX_PAGES'] = self.settings_widgets['NAVIGATION_MAX_PAGES'].value()
            new_settings['MIN_TIME_PER_PAGE'] = self.settings_widgets['MIN_TIME_PER_PAGE'].value()
            new_settings['NAV_INTERNAL_ONLY'] = self.settings_widgets['NAV_INTERNAL_ONLY'].isChecked()
            new_settings['NAV_AVOID_EXTERNAL'] = self.settings_widgets['NAV_AVOID_EXTERNAL'].isChecked()
            new_settings['NAV_AVOID_PATTERNS'] = self.settings_widgets['NAV_AVOID_PATTERNS'].toPlainText()
            new_settings['NAV_PREFERRED_KEYWORDS'] = self.settings_widgets['NAV_PREFERRED_KEYWORDS'].toPlainText()
            
            # Advanced
            new_settings['DEBUG_MODE'] = self.settings_widgets['DEBUG_MODE'].isChecked()
            new_settings['DEV_TOOLS'] = self.settings_widgets['DEV_TOOLS'].isChecked()
            new_settings['VERBOSE_LOGGING'] = self.settings_widgets['VERBOSE_LOGGING'].isChecked()
            new_settings['ENABLE_METRICS'] = self.settings_widgets['ENABLE_METRICS'].isChecked()
            new_settings['BETA_FEATURES'] = self.settings_widgets['BETA_FEATURES'].isChecked()
            new_settings['EXPERIMENTAL_AI'] = self.settings_widgets['EXPERIMENTAL_AI'].isChecked()
            new_settings['CUSTOM_JS_INJECTION'] = self.settings_widgets['CUSTOM_JS_INJECTION'].toPlainText()
            new_settings['BROWSER_CLEANUP_INTERVAL'] = self.settings_widgets['BROWSER_CLEANUP_INTERVAL'].value()
            new_settings['CACHE_SIZE_LIMIT'] = self.settings_widgets['CACHE_SIZE_LIMIT'].value()
            
            # Update config object
            for key, value in new_settings.items():
                setattr(config, key, value)
            
            # Save to file
            save_config_to_file(config)
            
            # Emit signal
            self.settings_changed.emit(new_settings)
            
            # Update status
            self.status_label.setText("Settings applied successfully")
            QMessageBox.information(self, "Success", "Settings have been applied successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply settings: {str(e)}")
            self.status_label.setText("Error applying settings")
    
    def save_and_close(self):
        """Save settings and close dialog"""
        self.apply_settings()
        self.accept()
    
    def test_settings(self):
        """Test current settings configuration"""
        QMessageBox.information(self, "Test Settings", 
                              "Settings test functionality will be implemented here.\n\n"
                              "This would typically test:\n"
                              "1. Proxy connectivity\n"
                              "2. CAPTCHA service API\n"
                              "3. Browser initialization\n"
                              "4. Database connection")
    
    def reset_to_defaults(self):
        """Reset all settings to default values"""
        reply = QMessageBox.question(
            self, "Confirm Reset",
            "Are you sure you want to reset ALL settings to default values?\n\n"
            "This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Reset to hardcoded defaults
            defaults = {
                'WORKER_COUNT': 5,
                'MAX_RETRIES': 3,
                'REQUEST_TIMEOUT': 30,
                'MAX_CPU_PERCENT': 80,
                'MAX_MEMORY_MB': 2048,
                'MAX_WORKERS_PER_PROXY': 3,
                'LOG_LEVEL': 'INFO',
                'LOG_TO_FILE': False,
                'HISTORY_SIZE': 1000,
                'AUTO_BACKUP': True,
                'BACKUP_INTERVAL': 24,
                'USE_UNDETECTED_CHROME': True,
                'HEADLESS': False,
                'BROWSER_WIDTH': 1366,
                'BROWSER_HEIGHT': 768,
                'WEBRTC_PROTECTION': True,
                'WEBGL_SPOOFING': True,
                'TIMEZONE_SYNC': True,
                'FINGERPRINT_MODE': 'Cortex',
                'USER_AGENT_MODE': 'Mixed',
                'MOUSE_STYLE': 'Human Curves',
                'DEFAULT_WAIT_TIME': 3.0,
                'CAPTCHA_SOLVER_ENABLED': False,
                'CAPTCHA_SOLVER_SERVICE': '2Captcha',
                'CAPTCHA_MAX_RETRY': 3,
                'AUTO_CAPTCHA_LEARN': True,
                'PROXY_TYPE': 'http',
                'PROXY_ROTATION': 'Per Session',
                'PROXY_TEST_URL': 'https://api.ipify.org',
                'AI_ENABLED': False,
                'AI_PREDICT_CTR': True,
                'AI_OPTIMIZE_PROXY': True,
                'SCROLL_MIN': 10,
                'SCROLL_MAX': 30,
                'DELAY_MIN': 5.0,
                'DELAY_MAX': 15.0,
                'TARGET_CTR': 8.0,
                'RANDOM_CLICK_PROB': 0.1,
                'DEEP_NAVIGATION_ENABLED': True,
                'NAVIGATION_MAX_DEPTH': 3,
                'NAVIGATION_MAX_PAGES': 10,
                'MIN_TIME_PER_PAGE': 30.0,
                'NAV_INTERNAL_ONLY': True,
                'NAV_AVOID_EXTERNAL': True,
                'DEBUG_MODE': False,
                'DEV_TOOLS': False,
                'VERBOSE_LOGGING': False,
                'ENABLE_METRICS': True,
                'BETA_FEATURES': False,
                'EXPERIMENTAL_AI': False,
                'BROWSER_CLEANUP_INTERVAL': 6,
                'CACHE_SIZE_LIMIT': 512,
            }
            
            # Apply defaults to widgets
            for key, value in defaults.items():
                widget = self.settings_widgets.get(key)
                if widget:
                    if isinstance(widget, QSpinBox):
                        widget.setValue(value)
                    elif isinstance(widget, QDoubleSpinBox):
                        widget.setValue(value)
                    elif isinstance(widget, QLineEdit):
                        widget.setText(str(value))
                    elif isinstance(widget, QComboBox):
                        index = widget.findText(str(value))
                        if index >= 0:
                            widget.setCurrentIndex(index)
                    elif isinstance(widget, QCheckBox):
                        widget.setChecked(value)
                    elif isinstance(widget, QTextEdit):
                        widget.setText(str(value))
            
            # Clear file paths
            for key in ['LOG_FILE_PATH', 'DB_PATH', 'FINGERPRINT_FOLDER', 
                       'PROXY_FILE_PATH', 'AI_MODEL_PATH']:
                widget = self.settings_widgets.get(key)
                if widget:
                    line_edit = widget.layout().itemAt(0).widget()
                    if line_edit:
                        line_edit.clear()
            
            # Clear text fields
            for key in ['CAPTCHA_API_KEY', 'NAV_AVOID_PATTERNS', 
                       'NAV_PREFERRED_KEYWORDS', 'CUSTOM_JS_INJECTION']:
                widget = self.settings_widgets.get(key)
                if isinstance(widget, (QLineEdit, QTextEdit)):
                    widget.clear()
            
            self.status_label.setText("Settings reset to defaults")
            QMessageBox.information(self, "Reset Complete", 
                                  "All settings have been reset to default values.")
    
    def setup_professional_styling(self):
        """Apply professional styling"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f7fa;
            }
            QLabel {
                color: #2c3e50;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: 11px;
            }
            QGroupBox {
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: 12px;
                font-weight: 600;
                color: #34495e;
                border: 1px solid #dce1e6;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
                color: #3498db;
            }
            QTabWidget::pane {
                border: 1px solid #dce1e6;
                border-radius: 6px;
                background-color: white;
                margin: 5px;
            }
            QTabBar::tab {
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: 11px;
                font-weight: 500;
                padding: 8px 16px;
                margin-right: 3px;
                background-color: #ecf0f1;
                border: 1px solid #dce1e6;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                color: #7f8c8d;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: #2980b9;
                border-bottom: 2px solid #2980b9;
                font-weight: 600;
            }
            QTabBar::tab:hover {
                background-color: #e0e6e8;
                color: #5d6d7e;
            }
            QPushButton {
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: 11px;
                font-weight: 500;
                padding: 7px 16px;
                border-radius: 4px;
                border: 1px solid #dce1e6;
                background-color: white;
                color: #2c3e50;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #f8f9fa;
                border-color: #bdc3c7;
            }
            QPushButton:pressed {
                background-color: #ecf0f1;
            }
            QPushButton:focus {
                border: 1px solid #3498db;
            }
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: 11px;
                padding: 6px 8px;
                border: 1px solid #dce1e6;
                border-radius: 4px;
                background-color: white;
                min-height: 24px;
            }
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
                border: 1px solid #3498db;
                background-color: #f8fafc;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #7f8c8d;
                margin-right: 5px;
            }
            QCheckBox {
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: 11px;
                color: #2c3e50;
                spacing: 6px;
            }
            QCheckBox::indicator {
                width: 14px;
                height: 14px;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                background-color: #3498db;
                border: 1px solid #2980b9;
            }
            QTextEdit {
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 10px;
                border: 1px solid #dce1e6;
                border-radius: 4px;
                background-color: white;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #f8f9fa;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #dce1e6;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #bdc3c7;
            }
        """)


# ============================================================================
# COMPATIBILITY ALIAS - Untuk mempertahankan kode yang sudah ada
# ============================================================================

class AdvancedSettings(OrganizedSettingsDialog):
    """
    Alias class untuk kompatibilitas dengan kode yang sudah ada.
    Kode lama yang mengimpor 'AdvancedSettings' akan otomatis 
    menggunakan interface tabbed yang baru.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Advanced Settings")  # Judul asli untuk kompatibilitas


# ============================================================================
# TEST FUNCTION - Untuk debugging
# ============================================================================

def test_settings_dialog():
    """Test function untuk mengetes dialog settings"""
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Test new dialog
    dialog = OrganizedSettingsDialog()
    dialog.settings_changed.connect(lambda s: print(f"Settings changed: {s}"))
    
    print("Testing OrganizedSettingsDialog...")
    if dialog.exec_() == QDialog.Accepted:
        print("Settings saved successfully")
    else:
        print("Settings cancelled")
    
    # Test compatibility alias
    print("\nTesting AdvancedSettings (compatibility alias)...")
    dialog2 = AdvancedSettings()
    if dialog2.exec_() == QDialog.Accepted:
        print("Compatibility test passed")
    
    sys.exit(0)


if __name__ == "__main__":
    test_settings_dialog()