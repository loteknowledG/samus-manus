# manifest.md

Computer use via pyautogui.

## How it works
- **Mouse**: move, click, double-click, drag
- **Keyboard**: type text, press keys, hotkey combos
- **Screenshots**: capture the screen to see what's on the monitor

With these primitives, the agent has hands and eyes — full computer use without external LLM APIs.

## Tools
- `hands.py` — CLI for direct mouse/keyboard/screenshot control
- `voice_loop.py` — offline voice control (Vosk STT + pyttsx3 TTS)

## Dependencies
- pyautogui (mouse, keyboard, screenshots)
- pillow (image handling)
- vosk, sounddevice, pyttsx3, numpy (voice control, optional)
