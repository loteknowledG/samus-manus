"""
Test script - just take a screenshot and save it
"""

import pyautogui
from datetime import datetime

print("📸 Taking screenshot...")
screenshot = pyautogui.screenshot()

filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
screenshot.save(filename)

print(f"✅ Screenshot saved as: {filename}")
print(f"📂 Location: C:\\dev\\samus-manus\\{filename}")

# Also show screen size
width, height = pyautogui.size()
print(f"🖥️  Screen size: {width}x{height}")

# Show mouse position
x, y = pyautogui.position()
print(f"🖱️  Current mouse position: ({x}, {y})")
