"""
Traffic Bot - Professional Edition
Entry Point

Cara Pakai:
1. Install requirements: pip install -r requirements.txt
2. Jalankan: python main.py
"""

import sys
import os

# Tambahkan root directory ke path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    """Check apakah semua dependencies sudah terinstall"""
    required_packages = [
        'selenium',
        'selenium_stealth',
        'webdriver_manager',
        'numpy',
        'scipy',
        'sklearn',
        'pandas',
        'psutil'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print("❌ Missing dependencies!")
        print(f"   Please run: pip install -r requirements.txt")
        print(f"\n   Missing packages: {', '.join(missing)}")
        return False
    
    return True

def main():
    """Main entry point"""
    print("=" * 60)
    print("🤖 TRAFFIC BOT - PROFESSIONAL EDITION")
    print("=" * 60)
    print()
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    if not check_dependencies():
        input("\nPress Enter to exit...")
        return
    
    print("✅ All dependencies installed!")
    print()
    
    # Import GUI (after dependency check)
    try:
        from ui.app import TrafficBotGUI
        from utils.logger import logger
        
        logger.info("Starting Traffic Bot GUI...")
        
        # Create and run GUI
        app = TrafficBotGUI()
        app.mainloop()
        
        logger.info("Traffic Bot closed")
    
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
