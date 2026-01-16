"""
IP History Tracker
Track IP yang sudah pernah dipakai (simple text file)
"""

import os
import threading
from datetime import datetime

class IPHistory:
    """Track IP history di text file"""
    
    def __init__(self, filename="ip_history.txt"):
        """
        Initialize IP history
        
        Args:
            filename: Path ke history file
        """
        self.filename = filename
        self._lock = threading.RLock()
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Ensure history file exists"""
        if not os.path.exists(self.filename):
            with open(self.filename, 'w', encoding='utf-8') as f:
                f.write("# IP History Log\n")
    
    def is_duplicate(self, ip: str) -> bool:
        """
        Check apakah IP sudah pernah dipakai
        
        Args:
            ip: IP address
        
        Returns:
            True jika duplicate
        """
        with self._lock:
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                    return ip in content
            except Exception as e:
                print(f"Error checking duplicate IP: {e}")
                return False
    
    def save_ip(self, ip: str) -> bool:
        """
        Save IP ke history
        
        Args:
            ip: IP address
        
        Returns:
            True jika sukses
        """
        with self._lock:
            try:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open(self.filename, 'a', encoding='utf-8') as f:
                    f.write(f"{timestamp} | {ip}\n")
                return True
            except Exception as e:
                print(f"Error saving IP to history: {e}")
                return False
    
    def cleanup_old_entries(self, days: int = 7):
        """
        Cleanup entries older than N days
        
        Args:
            days: Berapa hari yang mau di-keep
        """
        with self._lock:
            try:
                from datetime import timedelta
                cutoff_time = datetime.now() - timedelta(days=days)
                
                with open(self.filename, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                new_lines = []
                for line in lines:
                    if line.startswith('#'):
                        new_lines.append(line)
                        continue
                    
                    try:
                        parts = line.split('|')
                        if len(parts) >= 2:
                            timestamp_str = parts[0].strip()
                            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                            
                            if timestamp >= cutoff_time:
                                new_lines.append(line)
                    except:
                        # Keep line jika tidak bisa parse
                        new_lines.append(line)
                
                with open(self.filename, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                
                print(f"🧹 Cleaned up IP history older than {days} days")
            except Exception as e:
                print(f"Error cleaning up IP history: {e}")

# Global instance
ip_history = IPHistory()