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


def _match_template_opencv(screen_bgr, tpl_bgr, min_confidence: float):
    import cv2
    import numpy as np

    # convert to gray for matching
    screen_gray = cv2.cvtColor(screen_bgr, cv2.COLOR_BGR2GRAY)
    tpl_gray = cv2.cvtColor(tpl_bgr, cv2.COLOR_BGR2GRAY)

    th, tw = tpl_gray.shape[::-1]
    sh, sw = screen_gray.shape[::-1]

    best_val = 0.0
    best_loc = None

    # try a few template scales to tolerate DPI/zoom differences
    for scale in [1.0, 0.95, 1.05, 0.9, 1.1, 0.85, 1.15]:
        try:
            new_w = int(tw * scale)
            new_h = int(th * scale)
            if new_w < 8 or new_h < 8 or new_w > sw or new_h > sh:
                continue
            tpl_resized = cv2.resize(tpl_gray, (new_w, new_h), interpolation=cv2.INTER_AREA)
            res = cv2.matchTemplate(screen_gray, tpl_resized, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            if max_val > best_val:
                best_val = float(max_val)
                best_loc = (int(max_loc[0]), int(max_loc[1]), new_w, new_h)
                if best_val >= min_confidence:
                    break
        except Exception:
            continue

    if best_loc and best_val >= min_confidence:
        x, y, w, h = best_loc
        cx = x + w // 2
        cy = y + h // 2
        return (cx, cy)
    return None


def find_on_screen(img_path: str, confidence: float = 0.8, timeout: float = 3.0):
    """Locate image on screen and return center (x, y) or None.
    - Prefer OpenCV multi-scale template matching when `cv2` is available.
    - Fallback to `pyautogui.locateCenterOnScreen` when OpenCV is not available.
    - `timeout` is seconds to keep searching.
    """
    if not pyautogui:
        return None

    end = time.time() + float(timeout or 0)
    # allow progressively lower confidence as time runs out
    start_conf = float(confidence or 0.8)

    while True:
        try:
            # If OpenCV is installed, use a multi-scale, grayscale template matcher (more robust to scaling/zoom)
            try:
                import cv2
                import numpy as np
                # capture current screen as BGR numpy array
                img = pyautogui.screenshot()
                screen = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                tpl = cv2.imread(str(img_path))
                if tpl is not None:
                    # try a few confidence thresholds (allow relaxing if not found)
                    conf_threshold = start_conf
                    pos = _match_template_opencv(screen, tpl, conf_threshold)
                    if pos:
                        return pos
                    # relax threshold once if not found and time remains
                    if time.time() + 0.1 < end and conf_threshold > 0.6:
                        pos = _match_template_opencv(screen, tpl, max(0.6, conf_threshold - 0.15))
                        if pos:
                            return pos
                # fall back to pyautogui.locateCenterOnScreen if needed
            except Exception:
                pass

            # prefer pyautogui.locateCenterOnScreen when available (uses OpenCV internally if installed)
            if hasattr(pyautogui, 'locateCenterOnScreen'):
                try:
                    loc = pyautogui.locateCenterOnScreen(img_path, confidence=start_conf)
                except TypeError:
                    loc = pyautogui.locateCenterOnScreen(img_path)
                if loc:
                    return (int(loc.x), int(loc.y))
        except Exception:
            # swallow low-level errors and continue retrying until timeout
            pass

        if time.time() > end:
            return None
        time.sleep(0.2)