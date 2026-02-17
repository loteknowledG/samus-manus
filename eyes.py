"""
Eyes: simple vision helpers for Samus‑Manus MVP.
- capture_screenshot(out) -> path
- find_on_screen(img_path, confidence=0.8, timeout=3.0) -> center (x,y) or None

Uses `pyautogui` when available; falls back to Pillow ImageGrab for screenshots.
"""
from pathlib import Path
import time

try:
    import pyautogui
except Exception:
    pyautogui = None

try:
    from PIL import ImageGrab
except Exception:
    ImageGrab = None


def capture_screenshot(out: str) -> str:
    out_p = Path(out)
    if pyautogui:
        img = pyautogui.screenshot()
        img.save(out_p)
        return str(out_p)
    if ImageGrab:
        img = ImageGrab.grab()
        img.save(out_p)
        return str(out_p)
    raise RuntimeError('No screenshot backend available (install pyautogui or Pillow)')


def find_on_screen(img_path: str, confidence: float = 0.8, timeout: float = 3.0):
    """Locate image on screen and return center (x, y) or None.
    - Uses pyautogui.locateCenterOnScreen when available (supports `confidence` if OpenCV present).
    - `timeout` is seconds to keep searching.
    """
    if not pyautogui:
        return None
    end = time.time() + float(timeout or 0)
    while True:
        try:
            if confidence and hasattr(pyautogui, 'locateCenterOnScreen'):
                loc = pyautogui.locateCenterOnScreen(img_path, confidence=confidence)
            else:
                loc = pyautogui.locateCenterOnScreen(img_path)
            if loc:
                return (int(loc.x), int(loc.y))
        except Exception:
            # locateCenterOnScreen may raise if dependencies missing; swallow and return None
            return None
        if time.time() > end:
            return None
        time.sleep(0.2)