#!/usr/bin/env python3
"""Memory CLI for Samus‑Manus MVP.
Provides: add/list/query/export/import/rebuild-embeddings/backup.
"""
from pathlib import Path
import argparse
import json
import shutil

try:
    from samus_manus_mvp.memory import get_memory
except Exception:
    from memory import get_memory


def cmd_add(kind: str, text: str, meta: str):
    m = get_memory()
    metadata = json.loads(meta) if meta else {}
    rid = m.add(kind, text, metadata=metadata)
    print(rid)


def cmd_list(limit: int = 100):
    m = get_memory()
    for r in m.all(limit):
        print(f"{r['id']:4} {r['type'][:12]:12} {r['created_at']:.0f}  {r['text']}")


def cmd_query(q: str, top_k: int = 5):
    m = get_memory()
    res = m.query_similar(q, top_k=top_k)
    print(json.dumps(res, indent=2))


def cmd_export(out: str, limit: int = 1000):
    m = get_memory()
    data = m.all(limit)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print('exported', out)


def cmd_import(path: str):
    m = get_memory()
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    count = 0
    for item in data:
        k = item.get('type', 'import')
        t = item.get('text', '')
        meta = item.get('metadata', {})
        m.add(k, t, metadata=meta)
        count += 1
    print('imported', count)


def cmd_rebuild(limit: int = 100):
    m = get_memory()
    updated = m.rebuild_missing_embeddings(limit=limit)
    print('embeddings updated:', updated)


def cmd_backup(out: str):
    m = get_memory()
    src = Path(m.path)
    out_p = Path(out)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, out_p)
    print('backup created:', out)


def cmd_kg_query(q: str, top_k: int = 5, include_approvals: bool = True):
    try:
        from samus_manus_mvp.knowledge import retrieve, summarize_results
    except Exception:
        try:
            from knowledge import retrieve, summarize_results
        except Exception:
            print('Knowledge module not available')
            return
    res = retrieve(q, top_k=top_k, include_approvals=include_approvals)
    print(summarize_results(res))
    if res.get('memory'):
        print('\nMemory matches:')
        for r in res['memory']:
            print('-', r.get('type'), r.get('text')[:120])
    if res.get('approvals'):
        print('\nApproval matches:')
        for a in res['approvals']:
            print('-', a.get('ts'), a.get('answer') or a.get('approval'), '-', a.get('question') or a.get('task'))


def cmd_list_persona():
    m = get_memory()
    for r in m.all(50):
        if r.get('type') == 'persona':
            print(r.get('text'))
            return
    print('No persona set')


def cmd_list_voice():
    m = get_memory()
    for r in m.all(50):
        if r.get('type') == 'voice':
            print(r.get('text'))
            return
    print('No preferred voice set')

def main():
    ap = argparse.ArgumentParser(prog='memory', description='Memory CLI for Samus‑Manus')
    sub = ap.add_subparsers(dest='cmd', required=True)

    p = sub.add_parser('add')
    p.add_argument('kind')
    p.add_argument('text')
    p.add_argument('--meta', default='')
    p.set_defaults(func=lambda a: cmd_add(a.kind, a.text, a.meta))

    p = sub.add_parser('list')
    p.add_argument('--limit', type=int, default=100)
    p.set_defaults(func=lambda a: cmd_list(a.limit))

    p = sub.add_parser('query')
    p.add_argument('q')
    p.add_argument('--top-k', type=int, default=5)
    p.set_defaults(func=lambda a: cmd_query(a.q, a.top_k))

    p = sub.add_parser('export')
    p.add_argument('--out', required=True)
    p.add_argument('--limit', type=int, default=1000)
    p.set_defaults(func=lambda a: cmd_export(a.out, a.limit))

    p = sub.add_parser('import')
    p.add_argument('--in', dest='infile', required=True)
    p.set_defaults(func=lambda a: cmd_import(a.infile))

    p = sub.add_parser('rebuild-embeddings')
    p.add_argument('--limit', type=int, default=100)
    p.set_defaults(func=lambda a: cmd_rebuild(a.limit))

    p = sub.add_parser('backup')
    p.add_argument('--out', required=True)
    p.set_defaults(func=lambda a: cmd_backup(a.out))

    # persona helpers
    p = sub.add_parser('persona-set', help='Set a persistent persona used by the agent')
    p.add_argument('text', help='Persona description (short)')
    p.set_defaults(func=lambda a: cmd_add('persona', a.text, '{}'))

    p = sub.add_parser('persona-show', help='Show the most recent persona')
    p.set_defaults(func=lambda a: cmd_list_persona())

    p = sub.add_parser('voice-set', help='Set a preferred TTS voice in memory')
    p.add_argument('voice', help='Voice identifier (e.g. Hedda or nb-NO-HeddaNeural)')
    p.set_defaults(func=lambda a: cmd_add('voice', a.voice, '{}'))

    p = sub.add_parser('voice-show', help='Show the most recent preferred TTS voice')
    p.set_defaults(func=lambda a: cmd_list_voice())

    p = sub.add_parser('kg-query', help='Query memory + approvals (knowledge)')
    p.add_argument('q', help='Query text')
    p.add_argument('--top-k', type=int, default=5)
    p.add_argument('--no-approvals', dest='include_approvals', action='store_false', help='Do not search approval audit log')
    p.set_defaults(func=lambda a: cmd_kg_query(a.q, a.top_k, a.include_approvals))

    args = ap.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
