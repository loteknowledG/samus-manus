# Samus‑Manus MVP (workspace)

Quick start for the local Samus‑Manus MVP scaffold added to this workspace.

Prereqs (optional):
- Python 3.10+
- (Optional) `OPENAI_API_KEY` in environment to enable planning via OpenAI
- (Optional) `pyautogui` to actually perform local GUI actions

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

---

DEPRECATED: The `samus_manus_mvp` copy in this workspace has been **merged/moved** into the main `samus-manus` repo at `C:\\dev\\samus-manus`.
- Files were copied (code and CLI tools); large model files and local `memory.db` were not moved automatically.
- To use the canonical project, switch to `C:\\dev\\samus-manus` or remove this folder.

(If you want the on-disk `memory.db` or the `model/` directory moved as well, tell me and I will prepare those steps.)
