# Memory CLI — Samus‑Manus

Quick usage for the new `memory` CLI implemented in `samus_manus_mvp/memory_cli.py`.

Commands

- List recent entries:
  - `python samus_manus_mvp/memory_cli.py list --limit 20`
- Query (semantic / fallback):
  - `python samus_manus_mvp/memory_cli.py query "voice" --top-k 5`
- Export to JSON:
  - `python samus_manus_mvp/memory_cli.py export --out mem-export.json`
- Import from JSON:
  - `python samus_manus_mvp/memory_cli.py import --in mem-export.json`
- Rebuild missing embeddings (requires `OPENAI_API_KEY`):
  - `python samus_manus_mvp/memory_cli.py rebuild-embeddings --limit 100`
- Backup DB file:
  - `python samus_manus_mvp/memory_cli.py backup --out backups/memory.db.bak`

Notes
- The CLI is a thin wrapper around `samus_manus_mvp.memory.get_memory()`.
- Export/import produce/consume the same JSON format returned by `Memory.all()`.
- Rebuilding embeddings only works when `OPENAI_API_KEY` is set; use it after adding an API key to compute embeddings for historical records.
