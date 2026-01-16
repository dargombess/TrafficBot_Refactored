"""
Helper Functions
Fungsi-fungsi utility yang sering digunakan
"""

import random
import time
import hashlib
from datetime import datetime

def random_delay(min_seconds, max_seconds):
    """
    Sleep dengan delay random
    
    Args:
        min_seconds: Minimal detik
        max_seconds: Maksimal detik
    """
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)

def generate_hash(text):
    """
    Generate MD5 hash dari text
    
    Args:
        text: Text yang mau di-hash
    
    Returns:
        MD5 hash string
    """
    return hashlib.md5(text.encode()).hexdigest()

def parse_proxy(proxy_string):
    """
    Parse proxy string ke format yang benar
    
    Args:
        proxy_string: Format bisa:
            - IP:PORT
            - IP:PORT:USER:PASS
            - http://IP:PORT
            - socks5://IP:PORT
    
    Returns:
        Dict dengan keys: protocol, host, port, username, password
    """
    result = {
        'protocol': 'http',
        'host': '',
        'port': '',
        'username': None,
        'password': None
    }
    
    proxy_string = proxy_string.strip()
    
    # Check protocol
    if '://' in proxy_string:
        protocol, rest = proxy_string.split('://', 1)
        result['protocol'] = protocol
        proxy_string = rest
    
    # Split by colon
    parts = proxy_string.split(':')
    
    if len(parts) == 2:
        # IP:PORT
        result['host'] = parts[0]
        result['port'] = parts[1]
    elif len(parts) == 4:
        # IP:PORT:USER:PASS
        result['host'] = parts[0]
        result['port'] = parts[1]
        result['username'] = parts[2]
        result['password'] = parts[3]
    
    return result

def format_proxy_for_selenium(proxy_dict):
    """
    Format proxy dict untuk Selenium
    
    Args:
        proxy_dict: Dict dari parse_proxy()
    
    Returns:
        Proxy string untuk Selenium
    """
    protocol = proxy_dict['protocol']
    host = proxy_dict['host']
    port = proxy_dict['port']
    
    return f"{protocol}://{host}:{port}"

def read_file_lines(filepath):
    """
    Baca file dan return list of lines (tanpa empty lines)
    
    Args:
        filepath: Path ke file
    
    Returns:
        List of strings
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
        return lines
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return []

def get_timestamp():
    """
    Get timestamp string untuk logging
    
    Returns:
        Formatted timestamp string
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def clamp(value, min_value, max_value):
    """
    Clamp value antara min dan max
    
    Args:
        value: Nilai yang mau di-clamp
        min_value: Nilai minimum
        max_value: Nilai maksimum
    
    Returns:
        Clamped value
    """
    return max(min_value, min(value, max_value))

def percentage_to_ratio(percentage):
    """
    Convert percentage (0-100) ke ratio (0.0-1.0)
    
    Args:
        percentage: Percentage value
    
    Returns:
        Ratio value
    """
    return clamp(percentage, 0, 100) / 100.0

def calculate_success_rate(success_count, total_count):
    """
    Calculate success rate percentage
    
    Args:
        success_count: Jumlah sukses
        total_count: Total attempts
    
    Returns:
        Success rate percentage (0-100)
    """
    if total_count == 0:
        return 0.0
    return (success_count / total_count) * 100