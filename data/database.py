"""
Database Manager
SQLite database untuk analytics dan tracking
"""

import sqlite3
import threading
from datetime import datetime

class BotDatabase:
    """Database manager untuk bot"""
    
    def __init__(self, db_file="bot_data.db"):
        """
        Initialize database
        
        Args:
            db_file: Path ke database file
        """
        self.db_file = db_file
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._lock = threading.RLock()
        self._setup_tables()
    
    def _setup_tables(self):
        """Setup database tables"""
        with self._lock:
            # IP History table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS ip_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    ip TEXT NOT NULL,
                    success BOOLEAN,
                    duration REAL,
                    error_reason TEXT
                )
            ''')
            
            # Session Analytics table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    worker_id INTEGER,
                    url TEXT,
                    success BOOLEAN,
                    duration REAL,
                    actions_count INTEGER
                )
            ''')
            
            self.conn.commit()
    
    def save_ip_record(self, ip: str, success: bool, duration: float = 0, error: str = None):
        """
        Save IP usage record
        
        Args:
            ip: IP address
            success: Apakah sukses
            duration: Duration in seconds
            error: Error reason jika gagal
        """
        with self._lock:
            try:
                self.cursor.execute('''
                    INSERT INTO ip_history (ip, success, duration, error_reason)
                    VALUES (?, ?, ?, ?)
                ''', (ip, success, duration, error))
                self.conn.commit()
            except Exception as e:
                print(f"Error saving IP record: {e}")
    
    def save_session(self, worker_id: int, url: str, success: bool, 
                     duration: float, actions: int):
        """
        Save session record
        
        Args:
            worker_id: Worker ID
            url: Target URL
            success: Apakah sukses
            duration: Duration in seconds
            actions: Jumlah actions yang dilakukan
        """
        with self._lock:
            try:
                self.cursor.execute('''
                    INSERT INTO sessions (worker_id, url, success, duration, actions_count)
                    VALUES (?, ?, ?, ?, ?)
                ''', (worker_id, url, success, duration, actions))
                self.conn.commit()
            except Exception as e:
                print(f"Error saving session: {e}")
    
    def get_ip_stats(self, hours: int = 24):
        """
        Get IP statistics
        
        Args:
            hours: Last N hours
        
        Returns:
            Dict dengan statistics
        """
        with self._lock:
            try:
                self.cursor.execute('''
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success,
                        AVG(duration) as avg_duration
                    FROM ip_history
                    WHERE timestamp >= datetime('now', ?)
                ''', (f'-{hours} hours',))
                
                result = self.cursor.fetchone()
                return {
                    'total': result[0] or 0,
                    'success': result[1] or 0,
                    'avg_duration': result[2] or 0
                }
            except Exception as e:
                print(f"Error getting IP stats: {e}")
                return {'total': 0, 'success': 0, 'avg_duration': 0}
    
    def cleanup_old_data(self, days: int = 7):
        """
        Cleanup data older than N days
        
        Args:
            days: Berapa hari yang mau di-keep
        """
        with self._lock:
            try:
                self.cursor.execute('''
                    DELETE FROM ip_history
                    WHERE timestamp < datetime('now', ?)
                ''', (f'-{days} days',))
                
                self.cursor.execute('''
                    DELETE FROM sessions
                    WHERE timestamp < datetime('now', ?)
                ''', (f'-{days} days',))
                
                self.conn.commit()
                print(f"🧹 Cleaned up data older than {days} days")
            except Exception as e:
                print(f"Error cleaning up data: {e}")
    
    def close(self):
        """Close database connection"""
        self.conn.close()

# Global instance
database = BotDatabase()