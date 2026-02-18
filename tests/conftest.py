import sys
import types
import pytest

from samus_manus_mvp import hardware_stubs

# Auto-inject hardware stubs so tests run deterministically in CI
@pytest.fixture(autouse=True)
def inject_hardware_stubs(monkeypatch):
    # Only install stubs if the real modules are not present
    modules = {
        'pyautogui': hardware_stubs.pyautogui,
        'sounddevice': hardware_stubs.sounddevice,
        'pyttsx3': hardware_stubs.pyttsx3,
        'vosk': hardware_stubs.vosk,
    }
    for name, mod in modules.items():
        if name not in sys.modules:
            sys.modules[name] = mod
    yield
    # cleanup not necessary; let pytest tear down interpreter state
