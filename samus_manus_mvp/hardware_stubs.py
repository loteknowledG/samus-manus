"""Lightweight hardware stubs used for testing and CI.

Provides module-like objects for: pyautogui, sounddevice, pyttsx3, vosk.
These are *ONLY* intended for tests / CI where real hardware or native
bindings are unavailable.
"""
from types import ModuleType
import types
import numpy as np
from PIL import Image

# --- pyautogui stub ---
pyautogui = ModuleType('pyautogui')
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.0

class _FakeLoc:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def _pg_moveTo(x, y, duration=0):
    _pg_moveTo.last = (x, y, duration)

def _pg_click(x=0, y=0, clicks=1, interval=0.0, button='left'):
    _pg_click.last = (x, y, clicks, interval, button)

def _pg_doubleClick(x=None, y=None):
    _pg_doubleClick.last = (x, y)

def _pg_write(text, interval=0.02):
    _pg_write.last = (text, interval)

def _pg_screenshot(out=None):
    # return a small white image or save if out provided
    img = Image.new('RGB', (8, 8), 'white')
    if out:
        img.save(out)
        return out
    return img

def _pg_size():
    return (1024, 768)

def _pg_locateCenterOnScreen(img, confidence=None):
    return None

def _pg_press(key):
    _pg_press.last = key

def _pg_hotkey(*keys):
    _pg_hotkey.last = keys

def _pg_scroll(amount):
    _pg_scroll.last = amount

def _pg_dragTo(x, y, duration=0.0, button='left'):
    _pg_dragTo.last = (x, y, duration, button)

pyautogui.moveTo = _pg_moveTo
pyautogui.click = _pg_click
pyautogui.doubleClick = _pg_doubleClick
pyautogui.write = _pg_write
pyautogui.screenshot = _pg_screenshot
pyautogui.size = _pg_size
pyautogui.locateCenterOnScreen = _pg_locateCenterOnScreen
pyautogui.press = _pg_press
pyautogui.hotkey = _pg_hotkey
pyautogui.scroll = _pg_scroll
pyautogui.dragTo = _pg_dragTo

# --- sounddevice stub ---
sounddevice = ModuleType('sounddevice')

def _sd_rec(frames, samplerate=None, channels=1, dtype='float32'):
    # return zeros shaped array similar to sounddevice.rec
    import numpy as _np
    n = int(frames)
    return _np.zeros((n, channels), dtype=_np.float32)

def _sd_wait():
    return None

def _sd_query_devices():
    return []

sounddevice.rec = _sd_rec
sounddevice.wait = _sd_wait
sounddevice.query_devices = _sd_query_devices

# --- pyttsx3 stub ---
pyttsx3 = ModuleType('pyttsx3')
class _FakeEngine:
    def __init__(self):
        self.props = {}
        self.spoken = []
    def say(self, text):
        self.spoken.append(text)
    def runAndWait(self):
        return None
    def setProperty(self, k, v):
        self.props[k] = v

def _pytt_init():
    return _FakeEngine()
pyttsx3.init = _pytt_init

# --- vosk stub ---
vosk = ModuleType('vosk')
class _FakeModel:
    def __init__(self, path):
        self.path = path
class _FakeKaldiRecognizer:
    def __init__(self, model, rate):
        self.model = model
        self.rate = rate
        self._buf = b''
    def AcceptWaveform(self, pcm):
        # pretend short audio always accepted
        return True
    def Result(self):
        return '{"text": ""}'
    def FinalResult(self):
        return '{"text": ""}'

vosk.Model = _FakeModel
vosk.KaldiRecognizer = _FakeKaldiRecognizer

# Expose for tests to import easily
__all__ = ['pyautogui', 'sounddevice', 'pyttsx3', 'vosk']
