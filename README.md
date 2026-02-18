# Samus‑Manus — quick start

[![smoke](https://github.com/loteknowledG/samus-manus/actions/workflows/smoke.yml/badge.svg)](https://github.com/loteknowledG/samus-manus/actions/workflows/smoke.yml)

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
- Install (quick): `pip install -r requirements.txt` — see `bootup.md` for the full installer process, demo, and optional voice setup.
- Try `python hands.py screenshot --out screen.png` or `powershell -ExecutionPolicy Bypass -File .\demo_60s.ps1`.

Heartbeat tempo UI
- Small desktop UI to dial the heartbeat tempo: `python samus_manus_mvp/heartbeat_ui.py`
- Use the slider to pick an interval (10s–3600s), then `Apply & Restart` to update the running daemon. The UI preserves `auto_apply` preference and restarts the background heartbeat for you.

Always-on-top flip counter overlay
- Lightweight always-on-top countdown that shows time until the next heartbeat in MM:SS: `python samus_manus_mvp/heartbeat_overlay.py`.
- Displays live metrics: **auto‑approved count**, **pending tasks**, and the **seconds until the next auto‑approval** (next heartbeat). 
- Click-and-drag to reposition; double-click to open the full heartbeat UI. The display uses a subtle flip animation when the seconds change.

Quick links
- `AGENTS.md` — agent guide & first‑run workflow
- `bootup.md` — install & quickstart

### Approval audit log — heartbeat auto‑approvals 🔎
The heartbeat surfaces the exact action/question that was auto‑approved so you can always see *what* was approved, not just the yes/no.

- Location: `samus_manus_mvp/approval_audit.log` (JSON‑lines)
- Each entry records: `ts`, `auto` (true when auto‑approved), `approval` (y/n), `task`, `action` (the low‑level action that required approval), and `step`.
- Typed text is trimmed for privacy; audit entries are append‑only.

Example (from `samus_manus_mvp/approval_audit.log`):

```
{"ts": 1771382115.5210724, "auto": true, "approval": "y", "task": "Take a screenshot", "action": {"type": "wait", "seconds": 0.5}, "step": 1}
{"ts": 1771382116.0324275, "auto": true, "approval": "y", "task": "Take a screenshot", "action": {"type": "screenshot", "out": "samus_screenshot.png"}, "step": 2}
{"ts": 1771382116.363429, "auto": true, "approval": "y", "task": "Take a screenshot", "action": {"type": "done"}, "step": 3}
```

Quick inspect commands:
- `tail -n 50 samus_manus_mvp/approval_audit.log`
- `jq -c '. | {ts,auto,approval,task,action,step}' samus_manus_mvp/approval_audit.log | less`
- `python samus_manus_mvp/approval_cli.py list --limit 50`  # human‑readable audit summary
- `python samus_manus_mvp/approval_cli.py aa last 5 --text`  — quick shorthand (default `aa`)
- `python samus_manus_mvp/approval_cli.py aa list today` — approvals from last 24h
- `python samus_manus_mvp/approval_cli.py aa flamegraph 10` — flamegraph‑style histogram of top 10 approved tasks

> The heartbeat now surfaces this audit action in its spoken/console summary so you can hear/see the exact question that was approved.

Safety
- pyautogui FAILSAFE is enabled: move the mouse to a screen corner to abort.

For more details (usage examples, CLI, demos), see the original docs in the repository.

---

Merged content: files from the workspace `nowon/samus_manus_mvp` have been copied here for consolidation.  
Added files (copy only) include: `samus_agent.py`, `memory.py`, `memory_cli.py`, `voice_assistant.py`, `heartbeat.py`, `tasks.json`, `startup_restore.py`, `eyes.py`, `draw_smiley.py`. Deprecated/archived copies such as `README.samus_manus_mvp.md` and `requirements.samus_manus_mvp.txt` have been moved to the `deprecated/` folder.
Conflicting files were kept as suffixed copies (e.g. `hands.nowon.py`, `voice_loop.nowon.py`) so you can review/merge changes manually.
