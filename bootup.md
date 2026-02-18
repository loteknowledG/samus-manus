# bootup.md — Samus‑Manus MVP (first run)

Quick, repeatable steps to get Samus‑Manus (voice + heartbeat + memory + hands/eyes) running locally.

## Prerequisites ✅
- Python 3.10+ installed
- Recommended: a working audio device (speaker + microphone) for voice demos
- (Optional, advanced) `OPENAI_API_KEY` — only required for embeddings / planner features; the core voice, hands, and heartbeat flows work without it.

## Install dependencies 📦
- From repo root:
  - pip install -r samus_manus_mvp/requirements.txt

## First run — smoke checks 🔍
1. TTS (voice):
   - python samus_manus_mvp/voice_loop.py "Hello Samus — voice test"
2. Agent (planner simulation):
   - python samus_manus_mvp/samus_agent.py run "Take a screenshot"
3. Local heartbeat (announces tasks):
   - python samus_manus_mvp/heartbeat.py --once --announce
4. Chrome DevTools quick check — useful for Prompt API / built‑in AI testing:
   - start chrome --auto-open-devtools-for-tabs https://developer.chrome.com/docs/ai/prompt-api
   - in DevTools Console run `await LanguageModel.availability()` to confirm model availability (shows: "unavailable" | "downloadable" | "downloading" | "available")

## Enable live voice (STT + TTS) 🎤
- Optional offline STT: Vosk model (small):
  - mkdir -p samus_manus_mvp/model
  - download `https://alphacephei.com/vosk/models` (e.g. `vosk-model-small-en-us-0.15`) and extract into `samus_manus_mvp/model`
- Run voice assistant (interactive):
  - python samus_manus_mvp/voice_assistant.py --live

Windows: install a Norwegian TTS voice (recommended)
- Why: installing a native Norwegian system voice (e.g. **Hedda**, nb-NO) makes Hanna sound authentic and works offline.
- GUI steps (Windows 10/11):
  1. Open Settings → Time & language → Speech (or Settings → Accessibility → Speech).
  2. Click **Manage voices** (or **Add voices**).
  3. Click **Add a voice**, search for **Norwegian** or **Hedda (Norwegian Bokmål, nb‑NO)** and install the voice.
  4. Restart any running TTS apps (or sign out/in) so the new voice appears to programs.
- Quick verification & test:
  - List installed voices: `python samus_manus_mvp/voice_loop.py --list-voices` (look for `Hedda` or `nb-NO`).
  - Test Hanna (Norwegian):
    - `python samus_manus_mvp/voice_loop.py --voice Hedda "Hei — jeg heter Hanna, 26 år, fra Bergen. Si ifra hvis du trenger noe."`
    - or use the Hanna preset (will prefer Hedda if installed):
      `python samus_manus_mvp/voice_loop.py --hanna "Hei — jeg heter Hanna..."`

- PowerShell check (optional):
  - `Get-ChildItem HKLM:\SOFTWARE\Microsoft\Speech\Voices\Tokens` — installed SAPI voice tokens.
  - `Get-WindowsCapability -Online | Where-Object Name -like '*nb-NO*'` — list nb-NO language / speech capabilities.

PowerShell (admin) — install Hedda (nb-NO)
- NOTE: requires **Administrator** rights, internet, and may download a language pack (100+ MB). Sign out / restart after install.
- Discover the exact capability name first (do **not** install without confirming the name):
  - `Get-WindowsCapability -Online | Where-Object Name -like '*nb-NO*' | Format-Table -AutoSize`
- Example install command (replace the capability name you found):
  - `Add-WindowsCapability -Online -Name "Speech.TTS.nb-NO~~~~0.0.1.0"`
  - or using DISM: `dism /Online /Add-Capability /CapabilityName:Speech.TTS.nb-NO~~~~0.0.1.0`
- Verify the voice appears for SAPI/pyttsx3:
  - `Get-ChildItem HKLM:\SOFTWARE\Microsoft\Speech\Voices\Tokens`
  - `python samus_manus_mvp/voice_loop.py --list-voices` (look for `Hedda` / `nb-NO`)
- Remove if needed:
  - `Remove-WindowsCapability -Online -Name "Speech.TTS.nb-NO~~~~0.0.1.0"`

Notes: if you can't install the system voice, use the cloud `nb-NO-HeddaNeural` via `tools/edge_tts.py` (documented below).

Cloud TTS (Edge / Azure) — higher-quality Norwegian voices
- Quick install (optional):
  - `pip install edge-tts` — lightweight client that uses Microsoft Edge TTS voices (no API key required)
  - For Azure Neural TTS (more features), see Azure docs and set `AZURE_TTS_KEY` / `AZURE_TTS_REGION` as needed.
- List Norwegian cloud voices (example):
  - `python tools/edge_tts.py --list --locale nb-NO`
- Synthesize & play with Edge TTS:
  - `python tools/edge_tts.py --voice nb-NO-HeddaNeural "Hei — jeg heter Hanna"`
  - This saves a temporary MP3 and opens it with your system player.
- When to use:
  - Use cloud voices for higher fidelity or if a native Windows Norwegian voice isn't available.
  - Edge TTS is convenient (no API key) and supports `nb-NO-HeddaNeural` and other Norwegian neural voices.

Notes: if Vosk not available, voice assistant falls back to typed input. If you want, I can add optional edge-tts playback in `tools/tts_say.py` so `--voice` accepts cloud voice names.

## Persistent memory (advanced, optional)
- The persistent memory + embeddings feature is an optional, advanced capability and has been moved to the end of this file. See the **Optional — Persistent memory** section for setup, installation, and `OPENAI_API_KEY` details.

(If you don't need semantic search or OpenAI-based planner features, you can ignore the memory/embeddings section.)

## Eyes & Hands (vision + automation) 👁️🖐️
- Screenshots: `capture_screenshot()` via `eyes.py` or `samus_agent` actions.
- Image‑targeting: `find_click` action in planner uses `eyes.find_on_screen()` (requires pyautogui + optional OpenCV for confidence).
- Safe execution: actions are simulated by default. Use `--apply` to actually run GUI actions.
  - Example: python samus_manus_mvp/samus_agent.py run "Open Notepad and type hello" --apply
- Safety: `pyautogui.FAILSAFE` is enabled — move mouse to a corner to abort.

### Web‑hands (browser automation with Playwright) 🌐🖐️
- New helper: `tools/web_hands.py` — a Playwright-based CLI and Python API for reliable browser interactions (open, click by text or selector, fill inputs, screenshot).
- Install (one‑time):
  - pip install playwright
  - python -m playwright install
- Quick examples:
  - `python tools/web_hands.py open "https://example.com" --headful`
  - `python tools/web_hands.py click-text "Send verification" --headful`
  - `python tools/web_hands.py fill "#email" "you@example.com" --headful`
  - `python tools/web_hands.py screenshot --out page.png --headful`
- When to use:
  - Prefer `web_hands.py` over pixel-matching for web UIs — it uses DOM selectors and is far more robust.
  - Use `tools/puppeteer_send_verification.js` (Node/Puppeteer) if you prefer a Node-based flow.
- Notes:
  - See `tools/PLAYWRIGHT.md` for a short cheatsheet and `tools/web_hands.py` for the API.
  - Keep browser sessions `--headful` while developing so you can visually verify actions.

## Heartbeat & Tasks ⏱️
- Tasks file: `samus_manus_mvp/tasks.json` (add pending tasks there)
- Per‑task whitelist: add `"auto_approve": true` to a task in `tasks.json` to allow the heartbeat to automatically `--apply` that task when running in whitelist mode.
- Start continuous heartbeat:
  - python samus_manus_mvp/heartbeat.py --interval 1800 --announce
  - Start in background/daemon: `python samus_manus_mvp/heartbeat.py --background --announce`
  - Stop background heartbeat: `python samus_manus_mvp/heartbeat.py --stop`
  - Auto‑apply pending tasks (background): `python samus_manus_mvp/heartbeat.py --background --auto-apply --announce`
  - Control auto‑apply mode: `--auto-apply-mode whitelist` (default) or `--auto-apply-mode global`
  - AFK auto‑run: `--afk-threshold <minutes>` — when the user is idle for that many minutes the heartbeat can run pending tasks automatically. Use `--afk-mode whitelist` (default) or `--afk-mode global` to control which tasks are eligible.

> The background heartbeat stores its PID in `heartbeat_state.json` under `heartbeat_pid` — use `--stop` or kill the PID to stop it.

Note: when a `make an approval` task is processed, the heartbeat will automatically re-add a fresh `make an approval` pending task (marked `auto_approve: true`) so approvals do not permanently block automated runs.

## Backup & restore (recommended) 💾
- Quick backup (creates `backups/state-<timestamp>.zip`):
  - `python tools/backup_state.py backup`
- List backups:
  - `python tools/backup_state.py list`
- Restore from a backup:
  - `python tools/backup_state.py restore backups/state-20260101T123456.zip --yes`

Files saved by default: `heartbeat_state.json`, `tasks.json`, `memory.db`, `approval_audit.log`.
- Recommended: run `tools/backup_state.py backup` after you finish a configuration session or before major changes.

## Moltbook & external integrations (optional) 🚫
- Moltbook integration is optional and **not required** for the MVP.
- We kept Moltbook separate — you can ignore or remove `~/.config/moltbook` credentials.

## Troubleshooting & tips ⚠️
- If TTS silent: ensure system audio + `pyttsx3` voices installed. Try restarting Python process.
- If STT fails: confirm `samus_manus_mvp/model` contains a Vosk model and `sounddevice` works.
- If `pyautogui` actions misalign: take a screenshot first to verify coordinates.

## Next steps (suggested) ✨
- Add more task templates to `tasks.json` for demos.
- Add persistent logs and screenshots for audit trails.
- (Optional) Add CI checks that validate `samus_agent` dry‑run behavior.

### Recommended ClawHub skills (useful to install)
- `Summarize` — CLI to summarize URLs, PDFs, images, audio and YouTube. Quick install: `brew install steipete/tap/summarize` or install via ClawHub; requires model API key (e.g. `OPENAI_API_KEY` or `GEMINI_API_KEY`).
- `Tavily` — AI‑optimized web search skill (great for research). Requires `TAVILY_API_KEY` and review of SKILL.md before use.
- `Slack` — Integrate with Slack (send/read/pin messages, react). Requires a Slack bot token; review security notes before installing.

Tip: install skills with `npx clawhub@latest install <skill>` or download the skill ZIP from ClawHub for inspection before running.

## Copilot session snapshot (saved 2026-02-17) 💾
- Core components confirmed present: `eyes.py`, `voice_loop.py`, `voice_assistant.py`, `heartbeat.py`, `samus_agent.py`, `memory.py`, `draw_smiley.py`, `tasks.json`, `heartbeat_state.json`, `requirements.txt`, `hands.py`, `tools/web_hands.py` (`tools/PLAYWRIGHT.md`).
- `samus_manus_mvp/model/` contains ASR/Kaldi-style artifacts (`am/`, `conf/`, `graph/`, `ivector/`) — offline STT model is available.
- Observations from inspection: voice (TTS/STT), eyes (screenshot/find), and hands (GUI automation CLI) are implemented and runnable; memory persists locally; heartbeat and task scheduling are in place.
- Recent changes performed in this session (saved 2026-02-17):
  - `hands.py` CLI stub added (safe-by-default simulation when `pyautogui` is missing).
  - GitHub Actions smoke workflow added to `.github/workflows/smoke.yml`.
  - Heartbeat: added `--background` / `--stop`, `--auto-apply`, and `--auto-apply-mode` (whitelist/global); persisted in `heartbeat_state.json`.
  - Per-task whitelist (`"auto_approve": true` in `tasks.json`) and heartbeat whitelist behavior implemented.
  - Memory‑driven auto‑approve + `auto_approve` preference saved to memory; approvals are audit‑logged.
  - Approval audit log added: `samus_manus_mvp/approval_audit.log` (JSON lines; typed text trimmed for privacy).
  - Backup/restore tool added: `tools/backup_state.py` (documents included in this file).
  - `memory_cli.py` extended with `persona` helpers.

- Recommended immediate actions:
  - Unit tests added for `hands.py`, `eyes.py`, and `samus_agent` — run with `pytest` (CI smoke workflow at `.github/workflows/smoke.yml`).
  - Add a short Windows audio troubleshooting checklist in this file.
  - (Optional) Extend CI smoke tests to run lint/tests.
- Quick references:
  - ASR/STT model: `samus_manus_mvp/model/`
  - Agent entry points: `samus_manus_mvp/samus_agent.py`, `voice_assistant.py`, `voice_loop.py`, `samus_manus_mvp/hands.py`
  - Tasks & state: `samus_manus_mvp/tasks.json`, `heartbeat_state.json`


## Optional — Persistent memory (SQLite + embeddings) 🧠
- Local DB: `samus_manus_mvp/memory.db` (created automatically).
- What is auto-captured: `voice_command`, `typed_input`, `task`, `plan`, `approval`, `action`, `task_result` (voice/agent activity and approvals are saved automatically).
- API key & SDK: `OPENAI_API_KEY` enables embeddings & semantic search; the `openai` Python package is optional. Install only if you want embeddings/planner features:
  - `pip install openai`

### Quick usage (python REPL)
- `from samus_manus_mvp.memory import get_memory`
- `m = get_memory(); m.add('note','Remember to water plants')`
- `m.query_similar('water plants')`

### Memory CLI (inspect / export / restore)
- `python samus_manus_mvp/memory_cli.py list --limit 50`
- `python samus_manus_mvp/memory_cli.py query "voice" --top-k 10`
- `python samus_manus_mvp/memory_cli.py export --out mem-export.json`
- `python samus_manus_mvp/memory_cli.py import --in mem-export.json`
- `python samus_manus_mvp/memory_cli.py backup --out backups/memory.db.bak`

### Rebuild embeddings (after adding OPENAI_API_KEY)
- Set `OPENAI_API_KEY` in your environment and install the `openai` SDK, then:
  - `python samus_manus_mvp/memory_cli.py rebuild-embeddings --limit 500`

### Quick restore checklist — make Copilot "remember" everything
1. Restore/copy `memory.db` into `samus_manus_mvp/` or run `memory_cli.py import --in <file>`.
2. Confirm load: `python -c "from samus_manus_mvp.memory import get_memory; print(len(get_memory().all(10)))"`.
3. If you added `OPENAI_API_KEY` and installed the `openai` SDK, run `rebuild-embeddings` to enable semantic search.
4. (Optional) Run `python samus_manus_mvp/memory_cli.py query "<keyword>" --top-k 10` to verify important entries.

> Important: memory is local (SQLite). Do **not** commit `samus_manus_mvp/memory.db` to public repos — add it to `.gitignore` if needed.

### How Copilot/agent uses memory
- The agent and voice assistant call `get_memory()` automatically to save and query records.
- The agent will **auto-load memory on startup by default** (use `--no-restore` to disable automatic restore).
- The agent now consults recent approval records and will **auto‑approve matching actions** based on past decisions (you can still override interactively).
- **Audit log:** all approval decisions are appended to `samus_manus_mvp/approval_audit.log` as JSON lines. Note: approvals are recorded in the audit log (including the `action` payload), but are **not** duplicated into `memory.db` (audit-only unless you opt to persist).
- After you restore/import `memory.db`, Copilot can query and **speak** past commands and results using `voice_loop.speak()`.

### Tips & housekeeping ✨
- Export regularly (`memory_cli.py export`) and keep periodic backups.
- Rebuild embeddings once after enabling `OPENAI_API_KEY` so semantic search works for historical data.
- Prune or archive old entries if privacy or size is a concern.

---
Keep this file updated with any environment changes — it’s your single‑point boot guide for Samus‑Manus.