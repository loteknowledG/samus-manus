This folder (`samus_manus_mvp`) has been superseded and **merged** into the canonical project at `C:\dev\samus-manus`.

What was moved (copy of source files):
- `samus_agent.py`, `memory.py`, `memory_cli.py`, `voice_assistant.py`, `heartbeat.py`, `tasks.json`, `startup_restore.py`, `eyes.py`, `draw_smiley.py`, `memory_cli.py`, plus docs and helpers.

What was NOT moved automatically:
- `memory.db` (local SQLite file) — use `memory_cli.py export`/`import` to transfer persistent data.
- `model/` (ASR/STT model artifacts) — large files; move manually if needed.

Next steps you can run locally:
- Inspect and merge `hands.nowon.py` / `voice_loop.nowon.py` into existing files in `C:\dev\samus-manus`.
- If you want the runtime DB moved: `python samus_manus_mvp/memory_cli.py export --out mem-export.json` then import into the other repo.

If you want me to move the `model/` directory or copy `memory.db`, tell me and I will prepare the file transfer or export commands.