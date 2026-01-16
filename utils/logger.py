"""
Unified Logger System
Logging untuk semua aktivitas bot
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

class BotLogger:
    """Central logging system untuk bot"""
    
    def __init__(self, name="TrafficBot", log_file="bot.log"):
        """
        Initialize logger
        
        Args:
            name: Logger name
            log_file: Path ke file log
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Buat folder logs jika belum ada
        os.makedirs("logs", exist_ok=True)
        
        # File handler dengan rotation (TAMBAH ENCODING UTF-8!)
        file_handler = RotatingFileHandler(
            f"logs/{log_file}",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'  # ← FIX UNICODE ERROR!
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler (TAMBAH ENCODING UTF-8!)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Set encoding untuk console (Windows fix)
        import sys
        if sys.platform == 'win32':
            # Fix untuk Windows console
            try:
                sys.stdout.reconfigure(encoding='utf-8')
            except:
                pass
        
        # Format
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def info(self, message):
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message):
        """Log error message"""
        self.logger.error(message)
    
    def debug(self, message):
        """Log debug message"""
        self.logger.debug(message)
    
    def success(self, message):
        """Log success message (custom)"""
        # Gunakan text saja untuk avoid encoding error di Windows
        self.logger.info(f"[SUCCESS] {message}")
    
    def failed(self, message):
        """Log failed message (custom)"""
        # Gunakan text saja untuk avoid encoding error di Windows
        self.logger.error(f"[FAILED] {message}")

# Global logger instance
logger = BotLogger()
