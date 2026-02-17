# AGENTS.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

Project summary
Samus‑Manus is a small, script‑first desktop automation toolkit centered on pyautogui. It runs entirely locally: move/click/drag, type/keys/hotkeys, and take screenshots. Voice control (Vosk + pyttsx3).

Role of this file: concise summary and map of docs/capabilities.
- First-time setup: bootup.md
- Session context: MEMORY.md
- Journal of milestones/artifacts: RECORDS.md

For new agents: start here
1) Install base (hands/eyes)
   powershell> pip install -r requirements.txt
2) Sanity check (save a screenshot)
   powershell> python .\hands.py screenshot --out .\screen.png
3) Optional voice (offline)
   powershell> pip install vosk sounddevice pyttsx3 numpy
   powershell> python .\voice_loop.py

Common commands (PowerShell)
- Install & package
  - `pip install .`                — standard install (exposes `hands` CLI)
  - `pip install .[voice]`        — optional voice extras (Vosk/pyttsx3)
  - `pip install -e .`             — editable / developer install
  - `pipx install .`               — recommended isolated CLI install
  - `pip install -r requirements.txt`  — quick dependency install
- Hands CLI quickstart
  - python hands.py move --x 800 --y 450 --dur 0.2
  - python hands.py click --x 800 --y 450
  - python hands.py screenshot --out .\\screen.png
- Voice control (optional, offline)
  - pip install vosk sounddevice pyttsx3 numpy
  - python voice_loop.py
  - First run auto-downloads the Vosk English model (~50MB) into models/ (gitignored). Prompt: "Voice control ready. Press Enter to talk."
- Fast voice (persistent TTS)
  - Start server once: `python tools/tts_say.py --ensure "Fast voice online"`
  - Speak: `./say.ps1 "Hello"` (or `python tools/tts_say.py -- "Hello"`)
- 60-second demo
  - powershell -ExecutionPolicy Bypass -File .\\demo_60s.ps1
- Warp jump (voice + before/after + minimize + log)
  - .\\warp_jump.ps1 -What both -Label demo -App mspaint
- Single test / utility
  - python test_screenshot.py
- Build / Lint / Test framework
  - No build step; scripts run directly with Python.
  - No linter or test framework is configured in-repo.

Capabilities at a glance
- Entry points
  - hands.py — stateless CLI for direct mouse/keyboard/screenshot control
  - voice_loop.py — offline voice control using Vosk STT + pyttsx3 TTS (no API; auto-downloads ~50MB model on first run)
- Core primitives (pyautogui)
  - moveTo/click/doubleClick/dragTo · write/press/hotkey · scroll/screenshot
- Optional image targeting
  - hands.py find-click can use opencv-python for confidence matching if installed

Extension points (where to change things)
- Adding a new action: implement a new case in execute_action(...) and reflect it in CLI/voice prompts
- Shared logic: execute_action(...) and parse_actions(...) are duplicated; consider extracting to a shared module (e.g., actions.py)
- Robust text entry: for non‑ASCII text, prefer clipboard paste (pyperclip + ctrl+v) instead of pyautogui.write

Operational notes
- Read MEMORY.md at repo root on start for persistent context/next‑steps.
- Safety: pyautogui.FAILSAFE=True (move cursor to a corner to abort). Ctrl+C interrupts any script
- Coordinates: commands use absolute screen coordinates; use hands.py screenshot to verify alignment


Documentation map
- bootup.md — first-time install and quick run steps (hands + optional voice)
- README.md — usage overview (Hands CLI, demo, how it works)
- manifest.md — capabilities summary (pyautogui: hands/eyes)
- [soul.md](soul.md) — nuanced preferences (voice, screenshots, co‑driving etiquette)
- MEMORY.md — session scratchpad to carry state between runs
- RECORDS.md — running journal of milestones/artifacts
- .gitignore — includes models/ to keep Vosk downloads untracked
- tools/ — small helper scripts (e.g., draw_cat.py)
- test_screenshot.py — ad‑hoc utility; not a formal test suite
