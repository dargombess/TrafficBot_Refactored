# Import config yang SAMA dengan yang dipakai GUI
import sys
import importlib

# Reload config untuk ambil nilai terbaru dari memory
if 'bot_config' in sys.modules:
    importlib.reload(sys.modules['bot_config'])

from bot_config import config

print("="*50)
print("CAPTCHA CONFIGURATION TEST (LIVE)")
print("="*50)

try:
    print(f"CAPTCHA Enabled: {config.CAPTCHA_SOLVER_ENABLED}")
except AttributeError:
    print("CAPTCHA Enabled: NOT SET ❌")

try:
    print(f"Service: {config.CAPTCHA_SOLVER_SERVICE}")
except AttributeError:
    print("Service: NOT SET ❌")

try:
    print(f"API Key: {config.CAPTCHA_API_KEY}")
except AttributeError:
    print("API Key: NOT SET ❌")

try:
    print(f"Max Retry: {config.CAPTCHA_MAX_RETRY}")
except AttributeError:
    print("Max Retry: NOT SET ❌")

try:
    print(f"Auto Learn: {config.AUTO_CAPTCHA_LEARN}")
except AttributeError:
    print("Auto Learn: NOT SET ❌")

print("="*50)
print("\n✅ Test selesai!")
