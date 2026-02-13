# AGENTS.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

Project summary
Species: Amanu — agents with hands and eyes.
Samus‑Manus is a small, script‑first desktop automation agent. It captures a screenshot, asks a vision model what to do, parses a JSON action list, executes those actions with pyautogui, and loops until "done" or user abort.

Common commands (PowerShell)
- Install deps
  - pip install -r requirements.txt
- Run (OpenAI version)
  - Create .env with OPENAI_API_KEY=...
  - python samus_manus.py
  - When prompted, enter a task, e.g. "Open Notepad and type hello".
- Run (Gemini version)
  - Create .env with GOOGLE_API_KEY=...
  - python samus_manus_gemini.py
  - Uses model id gemini-2.0-flash.
- Single test / utility
  - python test_screenshot.py  # saves screenshot_YYYYMMDD_HHMMSS.png and prints screen size & mouse position
- Build / Lint / Test framework
  - No build step; scripts run directly with Python.
  - No linter or test framework is configured in-repo.

High‑level architecture
- Entry points
  - samus_manus.py (OpenAI) and samus_manus_gemini.py (Gemini). They implement the same control loop with different SDKs.
- Control loop (both versions)
  1) capture_screenshot(): grab full-screen PNG (PIL via pyautogui)
  2) Prompting: a system prompt defines the action grammar the model must return
  3) Message: current screenshot + task text sent to the model
  4) Parsing: parse_actions(...) extracts a JSON array from the model message (prefers fenced code blocks, falls back to regex scanning)
  5) Execution: execute_action(...) maps each item to pyautogui primitives (click, double_click, type, press, hotkey, scroll, move, wait, done)
  6) Loop: stop when an action returns "DONE" or max_steps is reached; Ctrl+C interrupts; moving the mouse to a corner triggers pyautogui.FAILSAFE
- SDK differences
  - OpenAI version: OpenAI.chat.completions (model "gpt-4o"); keeps conversation_history including screenshots between steps
  - Gemini version: genai.GenerativeModel('gemini-2.0-flash') with a stateful chat; screenshots passed as bytes

Extension points (where to change things)
- Adding a new action: implement a new case in execute_action(...) and add its JSON shape to the system prompt so the model can call it
- Cost control (OpenAI path): cap conversation_history to the most recent 1–2 steps or summarize prior state before sending
- Shared logic: execute_action(...) and parse_actions(...) are duplicated; consider extracting to a shared module (e.g., actions.py)
- Robust text entry: for non‑ASCII text, prefer clipboard paste (pyperclip + ctrl+v) instead of pyautogui.write

Operational notes
- Read MEMORY.md at repo root on start for persistent context/next‑steps.
- Environment: python‑dotenv loads .env automatically; if a key is missing, the script prints a clear error and exits
- Safety: pyautogui.FAILSAFE=True (slam cursor to a corner to abort). The main loop also catches KeyboardInterrupt
- Coordinates: the model must return absolute screen coordinates; consider providing screen size to the prompt if accuracy is an issue (pyautogui.size())

Known quirks
- samus_manus.py parse_actions catches json.JSONDecodeException (typo); should be json.JSONDecodeError
- Regex fallback in parse_actions may pick up stray JSON‑looking text; prefer returning a fenced JSON array from the model

Minimal repo map
- README.md — user‑facing setup/usage; action list; safety notes
- samus_manus.py — OpenAI loop
- samus_manus_gemini.py — Gemini loop (model id: gemini-2.0-flash)
- requirements.txt — pyautogui, pillow, google‑generativeai, python‑dotenv
- test_screenshot.py — ad‑hoc utility; not a formal test suite
