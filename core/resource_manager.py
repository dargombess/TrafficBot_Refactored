"""
Resource Manager
Mengelola IP blacklist, proxy selection, dan resource cleanup
"""

import time
import threading
from collections import defaultdict
from typing import List, Dict, Set, Optional

class ResourceManager:
    """Manager untuk resource bot (IP, proxy, fingerprint)"""
    
    def __init__(self):
        """Initialize resource manager"""
        # Blacklists
        self.blacklisted_ips: Set[str] = set()
        self.blacklisted_fingerprints: Set[str] = set()
        
        # Cooldowns (IP/fingerprint -> waktu bisa dipakai lagi)
        self.ip_cooldown: Dict[str, float] = {}
        self.fingerprint_cooldown: Dict[str, float] = {}
        
        # Statistics
        self.stats = {
            'success_count': 0,
            'failed_count': 0,
            'blocked_count': 0,
            'total_requests': 0
        }
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Start cleanup thread
        self._start_cleanup_thread()
    
    def blacklist_ip(self, ip: str, duration_minutes: int = 30):
        """
        Blacklist IP untuk duration tertentu
        
        Args:
            ip: IP address
            duration_minutes: Berapa lama di-blacklist (menit)
        """
        with self._lock:
            self.blacklisted_ips.add(ip)
            cooldown_end = time.time() + (duration_minutes * 60)
            self.ip_cooldown[ip] = cooldown_end
            print(f"🚫 IP Blacklisted: {ip} (for {duration_minutes} minutes)")
    
    def blacklist_fingerprint(self, fp_hash: str, duration_minutes: int = 60):
        """
        Blacklist fingerprint untuk duration tertentu
        
        Args:
            fp_hash: Fingerprint hash
            duration_minutes: Berapa lama di-blacklist (menit)
        """
        with self._lock:
            self.blacklisted_fingerprints.add(fp_hash)
            cooldown_end = time.time() + (duration_minutes * 60)
            self.fingerprint_cooldown[fp_hash] = cooldown_end
            print(f"🚫 Fingerprint Blacklisted: {fp_hash[:8]}... (for {duration_minutes} minutes)")
    
    def is_ip_available(self, ip: str) -> bool:
        """
        Check apakah IP tersedia (tidak di-blacklist)
        
        Args:
            ip: IP address
        
        Returns:
            True jika available
        """
        with self._lock:
            if ip not in self.blacklisted_ips:
                return True
            
            # Check apakah cooldown sudah habis
            if ip in self.ip_cooldown:
                if time.time() > self.ip_cooldown[ip]:
                    # Cooldown habis, remove dari blacklist
                    self.blacklisted_ips.remove(ip)
                    del self.ip_cooldown[ip]
                    return True
            
            return False
    
    def is_fingerprint_available(self, fp_hash: str) -> bool:
        """
        Check apakah fingerprint tersedia
        
        Args:
            fp_hash: Fingerprint hash
        
        Returns:
            True jika available
        """
        with self._lock:
            if fp_hash not in self.blacklisted_fingerprints:
                return True
            
            if fp_hash in self.fingerprint_cooldown:
                if time.time() > self.fingerprint_cooldown[fp_hash]:
                    self.blacklisted_fingerprints.remove(fp_hash)
                    del self.fingerprint_cooldown[fp_hash]
                    return True
            
            return False
    
    def get_available_proxy(self, proxies: List[str]) -> Optional[str]:
        """
        Pilih proxy yang available dari list
        
        Args:
            proxies: List of proxy strings
        
        Returns:
            Proxy string atau None jika tidak ada
        """
        with self._lock:
            available = []
            for proxy in proxies:
                # Extract IP dari proxy string
                try:
                    ip = proxy.split(':')[0] if ':' in proxy else proxy
                    if self.is_ip_available(ip):
                        available.append(proxy)
                except:
                    continue
            
            if not available:
                return None
            
            # Random selection dari available proxies
            import random
            return random.choice(available)
    
    def record_success(self):
        """Record successful request"""
        with self._lock:
            self.stats['success_count'] += 1
            self.stats['total_requests'] += 1
    
    def record_failure(self):
        """Record failed request"""
        with self._lock:
            self.stats['failed_count'] += 1
            self.stats['total_requests'] += 1
    
    def record_blocked(self):
        """Record blocked request"""
        with self._lock:
            self.stats['blocked_count'] += 1
            self.stats['total_requests'] += 1
    
    def get_stats(self) -> Dict:
        """
        Get current statistics
        
        Returns:
            Dict dengan statistics
        """
        with self._lock:
            stats = self.stats.copy()
            stats['blacklisted_ips'] = len(self.blacklisted_ips)
            stats['blacklisted_fingerprints'] = len(self.blacklisted_fingerprints)
            
            # Calculate success rate
            if stats['total_requests'] > 0:
                stats['success_rate'] = (stats['success_count'] / stats['total_requests']) * 100
            else:
                stats['success_rate'] = 0.0
            
            return stats
    
    def reset_stats(self):
        """Reset all statistics"""
        with self._lock:
            self.stats = {
                'success_count': 0,
                'failed_count': 0,
                'blocked_count': 0,
                'total_requests': 0
            }
    
    def _start_cleanup_thread(self):
        """Start background thread untuk cleanup expired entries"""
        def cleanup_loop():
            while True:
                try:
                    time.sleep(60)  # Check setiap 1 menit
                    self._cleanup_expired()
                except Exception as e:
                    print(f"Cleanup error: {e}")
        
        thread = threading.Thread(target=cleanup_loop, daemon=True)
        thread.start()
    
    def _cleanup_expired(self):
        """Cleanup expired blacklist entries"""
        with self._lock:
            current_time = time.time()
            
            # Cleanup expired IPs
            expired_ips = [
                ip for ip, end_time in self.ip_cooldown.items()
                if current_time > end_time
            ]
            
            for ip in expired_ips:
                if ip in self.blacklisted_ips:
                    self.blacklisted_ips.remove(ip)
                del self.ip_cooldown[ip]
            
            # Cleanup expired fingerprints
            expired_fps = [
                fp for fp, end_time in self.fingerprint_cooldown.items()
                if current_time > end_time
            ]
            
            for fp in expired_fps:
                if fp in self.blacklisted_fingerprints:
                    self.blacklisted_fingerprints.remove(fp)
                del self.fingerprint_cooldown[fp]
            
            if expired_ips or expired_fps:
                print(f"🧹 Cleaned up: {len(expired_ips)} IPs, {len(expired_fps)} fingerprints")
    
    def force_cleanup(self):
        """Force cleanup semua resource"""
        with self._lock:
            self.blacklisted_ips.clear()
            self.blacklisted_fingerprints.clear()
            self.ip_cooldown.clear()
            self.fingerprint_cooldown.clear()
            print("🧹 Force cleanup completed")

# Global instance
resource_manager = ResourceManager()