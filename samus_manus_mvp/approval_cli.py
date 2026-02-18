#!/usr/bin/env python3
"""Approval audit CLI — view / filter `approval_audit.log` (human-friendly summaries).

Usage examples:
  python samus_manus_mvp/approval_cli.py list --limit 50
  python samus_manus_mvp/approval_cli.py list --auto-only --since-seconds 86400
  python samus_manus_mvp/approval_cli.py list --task "screenshot"
"""
from pathlib import Path
import argparse
import json
import time
from datetime import datetime

BASE = Path(__file__).parent
AUDIT_PATH = BASE / 'approval_audit.log'


def load_audits(path: Path = AUDIT_PATH):
    if not path.exists():
        return []
    out = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                continue
    return out


def summarize_action(act: dict) -> str:
    try:
        if not act:
            return ''
        if isinstance(act, dict):
            atype = act.get('type')
            if atype == 'type':
                txt = (act.get('text') or '')
                s = txt.replace('\n', ' ')[:80]
                return f"type: {s}{'...' if len(txt) > 80 else ''}"
            if atype == 'screenshot':
                return f"screenshot -> {act.get('out') or ''}"
            if atype in ('click', 'double_click'):
                x = act.get('x'); y = act.get('y')
                return f"{atype} at ({x},{y})" if x is not None and y is not None else atype
            if atype in ('find_click', 'find-click'):
                return f"find_click: {act.get('img') or ''}"
            return str(act)
        return str(act)
    except Exception:
        return str(act)


def cmd_list(limit: int = 50, auto_only: bool = False, task: str | None = None, since_seconds: int = 0, raw: bool = False):
    audits = load_audits()
    now = time.time()
    if since_seconds:
        cutoff = now - float(since_seconds)
        audits = [a for a in audits if float(a.get('ts', 0)) >= cutoff]
    if auto_only:
        audits = [a for a in audits if a.get('auto')]
    if task:
        audits = [a for a in audits if task.lower() in (a.get('task') or '').lower()]
    # keep most recent entries
    audits = audits[-limit:]

    if raw:
        for a in audits:
            print(json.dumps(a, default=str))
        return

    for a in audits:
        ts = a.get('ts')
        try:
            ts = datetime.fromtimestamp(float(ts)).isoformat(sep=' ')
        except Exception:
            ts = str(ts)
        auto_flag = 'auto' if a.get('auto') else 'manual'
        approval = a.get('approval') or a.get('answer')
        task_text = a.get('task')
        step = a.get('step')
        # prefer explicit question field, fallback to action summary
        question = a.get('question') or summarize_action(a.get('action'))
        print(f"{ts} | {auto_flag} | {approval} | {task_text} | step:{step} | {question}")


def cmd_aa(action: str = 'last', n_or_when=None, text_only: bool = False, when: str | None = None):
    """Convenience: `aa last N`, `aa list today`, or `aa flamegraph`.

    - aa last N            -> show last N entries (default N=5)
    - aa list today        -> show entries from the last 24 hours
    - aa flamegraph [N]    -> show a flamegraph-like histogram of top N tasks
    - --text / text_only   -> print only the question text per entry

    `n_or_when` can be an integer (for `last` or `flamegraph`) or a keyword like 'today' (for `list`).
    """
    audits = load_audits()
    if not audits:
        return

    # normalize inputs
    if isinstance(n_or_when, str) and n_or_when.isdigit():
        n_val = int(n_or_when)
    elif isinstance(n_or_when, int):
        n_val = n_or_when
    else:
        n_val = None

    when_val = when or (n_or_when if isinstance(n_or_when, str) and not n_or_when.isdigit() else None)

    # default behaviour: `aa` with no args -> last 5 text-only
    if action == 'last' and n_or_when is None and not text_only and when is None:
        text_only = True
        n_val = n_val or 5

    if action == 'last':
        n_final = n_val or 5
        sel = audits[-int(n_final):]
        for a in sel:
            q = a.get('question') or summarize_action(a.get('action'))
            if text_only:
                print(q)
            else:
                ts = a.get('ts')
                try:
                    ts = datetime.fromtimestamp(float(ts)).isoformat(sep=' ')
                except Exception:
                    ts = str(ts)
                approval = a.get('approval') or a.get('answer')
                print(f"{ts} | {approval} | {q}")
        return

    if action == 'list':
        if when_val == 'today':
            cutoff = time.time() - 86400
            sel = [a for a in audits if float(a.get('ts', 0)) >= cutoff]
        else:
            n_final = n_val or 5
            sel = audits[-int(n_final):]
        for a in sel:
            q = a.get('question') or summarize_action(a.get('action'))
            if text_only:
                print(q)
            else:
                ts = a.get('ts')
                try:
                    ts = datetime.fromtimestamp(float(ts)).isoformat(sep=' ')
                except Exception:
                    ts = str(ts)
                approval = a.get('approval') or a.get('answer')
                print(f"{ts} | {approval} | {q}")
        return

    if action == 'flamegraph':
        # produce a simple histogram of top-N approved tasks (auto + manual by default)
        n_final = n_val or 10
        cutoff = None
        if when_val == 'today':
            cutoff = time.time() - 86400
        counts = {}
        for a in audits:
            if cutoff and float(a.get('ts', 0)) < cutoff:
                continue
            t = a.get('task') or (a.get('question') or 'unknown')
            counts[t] = counts.get(t, 0) + 1
        if not counts:
            return
        # sort and take top N
        items = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:int(n_final)]
        max_count = items[0][1]
        BAR_MAX = 48
        for name, cnt in items:
            bar_len = int((cnt / max_count) * BAR_MAX) if max_count > 0 else 0
            bar = '#' * max(1, bar_len)
            print(f"{name[:40]:40} | {bar} {cnt}")
        return

    raise ValueError('unsupported aa action')


def main():
    ap = argparse.ArgumentParser(prog='approval', description='Approval audit CLI')
    sub = ap.add_subparsers(dest='cmd', required=True)

    p = sub.add_parser('list', help='List recent approval audit entries')
    p.add_argument('--limit', type=int, default=50)
    p.add_argument('--auto-only', action='store_true')
    p.add_argument('--task', help='Filter by task substring')
    p.add_argument('--since-seconds', type=int, default=0, help='Show entries newer than now - seconds')
    p.add_argument('--raw', action='store_true', help='Print raw JSON lines')
    p.set_defaults(func=lambda a: cmd_list(a.limit, a.auto_only, a.task, a.since_seconds, a.raw))

    p2 = sub.add_parser('aa', help='Convenience auto-approval helpers (alias for approval audit)')
    p2.add_argument('action', nargs='?', choices=['last','list','flamegraph'], default='last')
    p2.add_argument('n', nargs='?', default=None, help='Number for last N OR keyword like "today" for list')
    p2.add_argument('when', nargs='?', help='Optional period specifier (e.g. today)')
    p2.add_argument('--text', dest='text_only', action='store_true', help='Print only the question text')
    p2.set_defaults(func=lambda a: cmd_aa(a.action, a.n, a.text_only, a.when))

    args = ap.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
