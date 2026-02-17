# DEPRECATED: samus_manus_mvp content merged into this repository's README.

This file was a backup copy of the MVP scaffold docs and has been consolidated into `README.md` and other docs. Keep this file only for historical reference.
Install
```
python -m pip install -r samus_manus_mvp/requirements.txt
```

Run (simulation, safe):
```
python samus_manus_mvp/samus_agent.py run "Take a screenshot"
```

Run (execute local actions):
```
python samus_manus_mvp/samus_agent.py run "Open Notepad and type hello" --apply
```

Voice (offline TTS)
```
python samus_manus_mvp/voice_loop.py "Hello world"
```
- Uses `pyttsx3` (offline). Useful for audible notifications and demos.

Hands (GUI automation CLI)
```
python samus_manus_mvp/hands.py move --x 800 --y 450 --dur 0.2
python samus_manus_mvp/hands.py click --x 800 --y 450
python samus_manus_mvp/hands.py type "hello" --interval 0.02
python samus_manus_mvp/hands.py screenshot --out screen.png
python samus_manus_mvp/hands.py find-click --img path/to/img.png --confidence 0.9 --click
```
- Safe by default: simulates actions when `pyautogui` is not installed; install `pyautogui` to enable real GUI automation.

Heartbeat (Moltbook watcher)
- Polls your Moltbook feed using credentials saved at `~/.config/moltbook/credentials.json` and announces new posts.
- Run once:
```
python samus_manus_mvp/heartbeat.py --once --announce
```
- Run continuously (30‑minute default):
```
python samus_manus_mvp/heartbeat.py --interval 1800 --announce
```
- State (last seen post) is stored in `samus_manus_mvp/heartbeat_state.json`.

Notes
- By default the agent simulates actions and asks for approval before each step.
- Set `OPENAI_API_KEY` to use an LLM planner; otherwise a small fallback planner is used.
- This scaffold is deliberately conservative — human‑in‑the‑loop and explicit `--apply` required to change the system.
