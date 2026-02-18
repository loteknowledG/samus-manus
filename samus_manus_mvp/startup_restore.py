#!/usr/bin/env python3
"""Startup restore helper — load memory and `bootup.md` and speak a short summary.

Behavior:
- Loads `samus_manus_mvp/memory.db` via `get_memory()` when available.
- Reads `bootup.md` (repo root) for context notes.
- Speaks a concise summary via `voice_loop.speak()` (falls back to printing).
- Exposes a small CLI for manual runs and optional embedding rebuild.
"""
from pathlib import Path
import json
import os
import textwrap

# TTS (best-effort)
try:
    from voice_loop import speak
except Exception:
    def speak(t):
        print('[TTS]', t)

# Memory (best-effort)
try:
    from memory import get_memory
except Exception:
    try:
        from samus_manus_mvp.memory import get_memory
    except Exception:
        get_memory = None

BOOTUP_PATH = Path(__file__).parent.parent / 'bootup.md'


def _read_bootup_excerpt(lines: int = 6) -> str:
    try:
        txt = BOOTUP_PATH.read_text(encoding='utf-8')
        excerpt = '\n'.join(txt.splitlines()[:lines])
        return excerpt
    except Exception:
        return ''


def _summarize_mem_items(items, limit=5):
    out = []
    for i, it in enumerate(items[:limit]):
        t = it.get('type', 'unk')
        txt = (it.get('text') or '')
        txt = txt.replace('\n', ' ')[:80]
        out.append(f"{t}:{txt}")
    return '; '.join(out) or 'no recent items'


def restore_and_speak(rebuild_embeddings: bool = False, summary_limit: int = 5, speak_summary: bool = True):
    parts = []
    # bootup excerpt
    boot_excerpt = _read_bootup_excerpt()
    if boot_excerpt:
        parts.append('Bootup notes loaded.')
    # memory
    mem = None
    mem_count = 0
    recent = ''
    try:
        if get_memory is not None:
            mem = get_memory()
            rows = mem.all(limit=summary_limit)
            mem_count = len(rows)
            recent = _summarize_mem_items(rows, limit=summary_limit)
            parts.append(f'Memory loaded: {mem_count} records; recent: {recent}')
    except Exception:
        parts.append('Memory not available')

    # optionally rebuild embeddings
    if rebuild_embeddings and mem is not None:
        try:
            updated = mem.rebuild_missing_embeddings(limit=500)
            parts.append(f'embeddings rebuilt for {updated} records')
        except Exception:
            parts.append('embedding rebuild failed')

    # quick environment checks
    try:
        has_stt = (Path(__file__).parent / 'model').exists()
        parts.append('STT model present' if has_stt else 'no STT model')
    except Exception:
        pass

    summary = ' — '.join(parts) if parts else 'No boot or memory information available.'
    short = textwrap.shorten(summary, width=320, placeholder='...')

    # speak + print
    if speak_summary:
        try:
            speak(short)
        except Exception:
            print('[speak failed]', short)
    print('STARTUP RESTORE SUMMARY:')
    print(short)
    if recent:
        print('\nRecent memory entries:')
        for r in (mem.all(limit=summary_limit) if mem is not None else []):
            print('-', r.get('type'), ':', (r.get('text') or '')[:140])

    return {'summary': short, 'count': mem_count}


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser(prog='startup_restore', description='Load memory and bootup notes and speak a short summary')
    ap.add_argument('--rebuild-embeddings', action='store_true')
    ap.add_argument('--limit', type=int, default=5)
    ap.add_argument('--silent', action='store_true', help='Do not speak, only print')
    args = ap.parse_args()
    restore_and_speak(rebuild_embeddings=args.rebuild_embeddings, summary_limit=args.limit, speak_summary=not args.silent)
