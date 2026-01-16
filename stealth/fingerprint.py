"""
Browser Fingerprint Manager
Mengelola browser fingerprinting untuk stealth
"""

import random
import json
import os
from typing import Dict, Optional

class FingerprintManager:
    """Manager untuk browser fingerprinting"""
    
    # User agents pool
    MOBILE_USER_AGENTS = [
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
    ]
    
    DESKTOP_USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]
    
    def __init__(self, mode: str = "Cortex"):
        """
        Initialize fingerprint manager
        
        Args:
            mode: Fingerprint mode (Cortex, Pro, JSON)
        """
        self.mode = mode
        self.json_folder = ""
        self.current_fingerprint = None
    
    def set_json_folder(self, folder_path: str):
        """Set folder path untuk JSON fingerprints"""
        self.json_folder = folder_path
    
    def get_random_user_agent(self, ua_mode: str = "Mixed") -> str:
        """
        Get random user agent
        
        Args:
            ua_mode: User agent mode (Mobile Only, Desktop Only, Mixed)
        
        Returns:
            User agent string
        """
        if ua_mode == "Mobile Only":
            return random.choice(self.MOBILE_USER_AGENTS)
        elif ua_mode == "Desktop Only":
            return random.choice(self.DESKTOP_USER_AGENTS)
        else:  # Mixed
            all_agents = self.MOBILE_USER_AGENTS + self.DESKTOP_USER_AGENTS
            return random.choice(all_agents)
    
    def get_fingerprint(self, ua_mode: str = "Mixed") -> Dict:
        """
        Get fingerprint configuration
        
        Args:
            ua_mode: User agent mode
        
        Returns:
            Dict dengan fingerprint config
        """
        if self.mode == "JSON" and self.json_folder:
            return self._load_json_fingerprint()
        elif self.mode == "Cortex":
            return self._generate_cortex_fingerprint(ua_mode)
        else:  # Pro mode (simplified)
            return self._generate_cortex_fingerprint(ua_mode)
    
    def _load_json_fingerprint(self) -> Dict:
        """Load fingerprint dari JSON file"""
        try:
            if not os.path.exists(self.json_folder):
                return self._generate_cortex_fingerprint("Mixed")
            
            json_files = [f for f in os.listdir(self.json_folder) if f.endswith('.json')]
            if not json_files:
                return self._generate_cortex_fingerprint("Mixed")
            
            chosen_file = random.choice(json_files)
            file_path = os.path.join(self.json_folder, chosen_file)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract user agent dari JSON
            ua = data.get('fingerprint', {}).get('navigator', {}).get('userAgent', '')
            if not ua:
                ua = data.get('navigator', {}).get('userAgent', '')
            if not ua:
                ua = self.get_random_user_agent("Mixed")
            
            return {
                'user_agent': ua,
                'fingerprint_hash': chosen_file.replace('.json', ''),
                'source': 'json'
            }
        except Exception as e:
            print(f"Error loading JSON fingerprint: {e}")
            return self._generate_cortex_fingerprint("Mixed")
    
    def _generate_cortex_fingerprint(self, ua_mode: str) -> Dict:
        """Generate Cortex-style fingerprint"""
        user_agent = self.get_random_user_agent(ua_mode)
        
        # Generate fingerprint hash
        import hashlib
        fp_hash = hashlib.md5(user_agent.encode()).hexdigest()
        
        return {
            'user_agent': user_agent,
            'fingerprint_hash': fp_hash,
            'source': 'cortex'
        }
    
    def apply_fingerprint_to_driver(self, driver, fingerprint: Dict):
        """
        Apply fingerprint ke Selenium driver
        
        Args:
            driver: Selenium WebDriver instance
            fingerprint: Fingerprint dict dari get_fingerprint()
        """
        try:
            # Set navigator properties via CDP
            user_agent = fingerprint.get('user_agent', '')
            
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": user_agent
            })
            
            # Additional stealth scripts
            driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            
            self.current_fingerprint = fingerprint
            
        except Exception as e:
            print(f"Error applying fingerprint: {e}")

# Global instance
fingerprint_manager = FingerprintManager()