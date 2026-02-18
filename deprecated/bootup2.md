# bootup.md

Quick boot sequence for local hands/voice.

## 1) Install base (hands/eyes)
```powershell
pip install -r requirements.txt
```
Verify:
```powershell
python .\hands.py screenshot --out .\boot_check.png
```

Paint drawing test (man + machine are friends)
- Purpose: verify `hands.py` can control an app (MS Paint) and capture before/after screenshots.

Steps:
1. Take a pre-check screenshot to confirm the desktop state:

```powershell
python .\hands.py screenshot --out .\before_paint.png
```

2. Run the automated Paint drawing (opens MS Paint, draws, saves a result):

```powershell
python .\draw_friends.py
```

- Output: `friends_paint.png` (saved in repo root).
- Optional: take an explicit after screenshot with `hands.py` if you want a second capture:

```powershell
python .\hands.py screenshot --out .\after_paint.png
```

Notes:
- The `draw_friends.py` script automates Paint to draw a human + robot handshake and saves `friends_paint.png` for verification.
- Use `pyautogui` failsafe (move cursor to a screen corner) to abort if needed.

## 2) 60‑second demo (optional)
```powershell
powershell -ExecutionPolicy Bypass -File .\demo_60s.ps1
```

## 3) Voice

Quick summary
- Offline STT (Vosk) + local TTS (pyttsx3) for hands‑free control. Use `tools/mic_test.py` to validate microphone and `tools/tts_say.py` / `tools/tts_server.py` for persistent TTS.

Recommended install (two easy options)
- Using the voice requirements file:

```powershell
python -m pip install -r requirements-voice.txt
```

- Or install the voice extras when you install the package locally:

```powershell
pip install .[voice]
```

(Prefer running inside a virtualenv or pipx — example below.)

Virtualenv / pipx (recommended)
- Create & activate a venv (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-voice.txt
```

- Or use pipx for an isolated CLI install:

```powershell
pipx install .
```

Run
- Start the voice loop (press Enter to speak):

```powershell
python .\voice_loop.py            # use --no-prompt to silence the "Speak now." prompt
```

- One‑shot mic test (records, transcribes, optional TTS):

```powershell
python tools\mic_test.py            # record 4s and print transcript
python tools\mic_test.py --speak    # speak the transcript via local TTS
python tools\mic_test.py --no-prompt -s 4  # disable the audible "Speak now." prompt
```

TTS server and `tts_say.py`
- Persistent TTS server: `tools/tts_server.py` (used by `tools/tts_say.py`).
- Start-on-demand + foreground logging (recommended):

```powershell
python tools\tts_say.py --ensure --wait "Samus is here."  # starts server if needed, waits until audio finishes
```

- Flags you should know:
  - `--no-prompt` — supported by `tools/mic_test.py` and `voice_loop.py` (disables the audible "Speak now.")
  - `--wait` — supported by `tools/tts_say.py` (blocks until playback completes)
  - `--ensure` — start the persistent TTS server if it's not running

Smoke tests (what to run and what to expect)
- Mic + TTS: `python tools\mic_test.py --speak -s 4` → prints transcript and (if `--speak`) plays it back via TTS.
- Mic no prompt: `python tools\mic_test.py --no-prompt -s 4` → records without audible prompt.
- TTS server + wait: `python tools\tts_say.py --ensure --wait "Test"` → command returns after playback; check `tools/tts_server.log` for `[TTS] play:` / `[TTS] done:` lines.
- Voice loop: `python .\voice_loop.py` → press Enter, speak commands like "click" or "type hello".

Notes
- First run of STT will auto-download the Vosk English model (~50MB) into `models/` (gitignored). Local copy: `models/vosk-model-small-en-us-0.15/`.
- `tools/tts_say.py --ensure` now starts the TTS server in a foreground‑capable mode and logs playback to `tools/tts_server.log` for easier debugging.

Troubleshooting & tips
- Python version: use Python 3.8+.
- Sounddevice check: `python -c "import sounddevice as sd; print(sd.query_devices())"` — verifies audio devices.
- One‑shot TTS test: `python -c "import pyttsx3; e=pyttsx3.init(); e.say('test'); e.runAndWait()"`.
- If you see no audio: verify system volume, default playback device, and microphone permissions (Windows: Settings → Privacy → Microphone). RDP/VM sessions may not forward audio.
- Check TTS server log for playback entries: `tail -n 40 tools/tts_server.log` (or open the file in your editor).
- Model download fails: ensure internet access and that `models/` is writable.
- Use `--no-prompt` when you want silent recording (useful for automated tests).

Safety
- pyautogui FAILSAFE: move cursor to any screen corner to abort.
- Ctrl+C interrupts any script.

Run the sanity-check from VS Code:
- A VS Code task `Hands: screenshot` is available (`.vscode/tasks.json`). Run it with Ctrl+Shift+P → "Tasks: Run Task" → select `Hands: screenshot`.
- Or run manually in PowerShell: `python .\hands.py screenshot --out .\boot_check.png`.

Optional verification:
- The Vosk model folder `models/vosk-model-small-en-us-0.15/` is present in the repo (checked).

## 4) Heartbeat
Local heartbeat watcher + task runner — keeps `heartbeat_state.json` up to date and can announce/status-check and run pending `tasks.json` entries.

- Run one check and exit:

```powershell
python heartbeat.py --once
```

- Run continuously (default interval 1800s):

```powershell
python heartbeat.py
```

- Use TTS announcements:

```powershell
python heartbeat.py --announce
```

- Change polling interval (seconds):

```powershell
python heartbeat.py --interval 60
```

Notes:
- State file: `heartbeat_state.json` (stores last heartbeat timestamp).
- Tasks file: `tasks.json` — add tasks with `status: "pending"` to have them executed (simulated by `samus_agent.py run ... --no-approve`).
- Requires local TTS (`pyttsx3`) for voice; fallback prints to console if unavailable.
- Stop with Ctrl+C; `pyautogui` failsafe still applies.

## 5) Session memory
`MEMORY.md` contains the persistent session context for Samus‑Manus — identity, defaults, last‑session notes, and next‑session TODOs. Edit `MEMORY.md` to persist any state or reminders you want available on next boot.

- Open/edit: `code MEMORY.md` or open the file in your editor.
- Quick checks:
  - Review `Last session notes` for recent actions.
  - Check `Next session TODO` for outstanding items to run after boot.
- Use it to store defaults such as working dir, artifact folder, and safety cues.

Examples:
- Add a TODO under `Next session TODO` to persist a task across boots.
- Use the `Boot sequence (quick)` entries in `MEMORY.md` for common commands.

Notes:
- Treat `MEMORY.md` as the single source of session context for local runs.
- Keep entries concise and append‑only when possible.

## 6) Memory CLI
A thin CLI for inspecting and managing the repository memory store. See `MEMORY_CLI.md` for full details; common commands below use `samus_manus_mvp/memory_cli.py`.

Common commands:
- List recent entries:
  - `python samus_manus_mvp/memory_cli.py list --limit 20`
- Query (semantic / fallback):
  - `python samus_manus_mvp/memory_cli.py query "voice" --top-k 5`
- Export to JSON:
  - `python samus_manus_mvp/memory_cli.py export --out mem-export.json`
- Import from JSON:
  - `python samus_manus_mvp/memory_cli.py import --in mem-export.json`
- Rebuild embeddings (requires `OPENAI_API_KEY`):
  - `python samus_manus_mvp/memory_cli.py rebuild-embeddings --limit 100`
- Backup the DB file:
  - `python samus_manus_mvp/memory_cli.py backup --out backups/memory.db.bak`

Notes:
- The CLI wraps `samus_manus_mvp.memory.get_memory()` and mirrors the JSON format returned by `Memory.all()`.
- Rebuilding embeddings requires `OPENAI_API_KEY` (set before running).
- See `MEMORY_CLI.md` for examples and advanced options.

## 7) Manifest
High‑level capabilities and primitives for Samus‑Manus. See `manifest.md` for full details.

- Primitives: `Mouse` (move/click/drag), `Keyboard` (type/press/hotkey), `Screenshots` (capture/inspect).
- Tools: `hands.py` (CLI for direct control), `voice_loop.py` (offline voice control — Vosk + pyttsx3).
- Dependencies: `pyautogui`, `pillow`, plus optional voice deps (`vosk`, `sounddevice`, `pyttsx3`, `numpy`).

Quick checks:
- Hands CLI: `python hands.py screenshot --out screen.png` — verifies the core input/output loop.
- Voice: `python voice_loop.py` — starts offline STT/TTS (first run may auto-download model).

Notes:
- `manifest.md` is the best place to understand what the project can do and which files implement core primitives.
- Use the primitives in `hands.py` for reproducible automations and `voice_loop.py` for local voice control.
