# Samus‑Manus — quick start

Samus‑Manus is a local desktop automation toolkit (pyautogui). It uses `pyautogui` to move the mouse and control the keyboard, takes screenshots (Pillow) to inspect the screen, and supports optional local voice (pyttsx3; Vosk STT). For first‑time setup and the agent's recommended workflow, start with `AGENTS.md`.

- Read `AGENTS.md` first — it has the agent defaults, etiquette, and where to start. (`soul.md` is referenced there for agent behavior.)
- Then follow `bootup.md` for the minimal install + first run steps (hands + optional voice).

## About — Samus‑Manus ⚙️🖐️👁️
Samus‑Manus is an agent‑style toolkit that gives scripts local "hands" (mouse/keyboard), "eyes" (screenshots), and optional offline voice. It automates GUI tasks privately and reliably using `pyautogui` + Pillow, with a persona and small CLI for demos and scripting.

Key points
- **Local & privacy‑first** — no cloud LLMs or external APIs. 🔒
- **Hands**: mouse/keyboard automation via `pyautogui` (`hands.py`). 🖱️
- **Eyes**: screen capture (Pillow) for sensing; BEFORE/AFTER screenshot ritual. 👁️
- **Voice**: offline TTS (`pyttsx3`) and optional Vosk STT for voice control. 🔊
- **Safety**: `pyautogui.FAILSAFE` + Ctrl+C to abort. ⚠️
- Agent defaults and behavior are defined in `soul.md` and `AGENTS.md` (read those first). 📜

Quick start
- Read `AGENTS.md` → follow `bootup.md` to install and run the demo.
- Try `python hands.py screenshot --out screen.png` or `powershell -ExecutionPolicy Bypass -File .\demo_60s.ps1`.

Quick links
- `AGENTS.md` — agent guide & first‑run workflow
- `bootup.md` — install & quickstart

Safety
- pyautogui FAILSAFE is enabled: move the mouse to a screen corner to abort.

For more details (usage examples, CLI, demos), see the original docs in the repository.
