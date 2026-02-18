"""Memory Intelligence / Knowledge helpers

Provides simple retrieval over persistent `Memory` plus the approval audit log.
- retrieve(query): returns persona, similar memory records, and matching approvals.
- Lightweight and local-first: uses embeddings when available via `Memory.query_similar`.

This is intentionally small and testable; later we can add a proper vector index or RAG server.
"""
from pathlib import Path
import json
import time
from typing import List, Dict, Any

try:
    from samus_manus_mvp.memory import get_memory
except Exception:
    try:
        from memory import get_memory
    except Exception:
        get_memory = None

BASE = Path(__file__).parent
AUDIT_PATH = BASE / 'approval_audit.log'


def _load_approvals() -> List[Dict[str, Any]]:
    if not AUDIT_PATH.exists():
        return []
    out = []
    try:
        with open(AUDIT_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    out.append(json.loads(line))
                except Exception:
                    continue
    except Exception:
        return []
    return out


def retrieve(query: str, top_k: int = 5, include_approvals: bool = True) -> Dict[str, Any]:
    """Return a dictionary with `persona`, `memory` (similar), and `approvals` (matching).

    - `memory` uses Memory.query_similar when available (falls back to substring matches).
    - `approvals` searches `approval_audit.log` for the query in `question`/`task`/`action`.
    """
    res: Dict[str, Any] = {'persona': None, 'memory': [], 'approvals': []}

    # persona: most recent persona in memory (best-effort)
    try:
        if get_memory is not None:
            m = get_memory()
            for r in m.all(50):
                if r.get('type') == 'persona':
                    res['persona'] = r.get('text')
                    break
    except Exception:
        res['persona'] = None

    # memory: use semantic query when possible
    try:
        if get_memory is not None:
            res['memory'] = get_memory().query_similar(query, top_k=top_k)
        else:
            res['memory'] = []
    except Exception:
        res['memory'] = []

    # approvals: simple substring match against question/task/action
    if include_approvals:
        try:
            arows = _load_approvals()
            qlow = (query or '').lower()
            matched = []
            for a in reversed(arows):
                # consider question, task, and serialized action
                question = str(a.get('question') or '').lower()
                task = str(a.get('task') or '').lower()
                action = json.dumps(a.get('action') or {}) if a.get('action') else ''
                if qlow in question or qlow in task or qlow in action.lower():
                    matched.append(a)
                if len(matched) >= top_k:
                    break
            res['approvals'] = matched
        except Exception:
            res['approvals'] = []

    return res


def summarize_results(r: Dict[str, Any]) -> str:
    """Return a short human summary of retrieve() results."""
    parts = []
    if r.get('persona'):
        parts.append(f"Persona: {r['persona']}")
    mem = r.get('memory') or []
    if mem:
        parts.append(f"Memory matches: {len(mem)} (top: {mem[0].get('text')[:80]})")
    appr = r.get('approvals') or []
    if appr:
        parts.append(f"Approvals matching: {len(appr)} (latest: {appr[0].get('question') or appr[0].get('task')})")
    return ' | '.join(parts) if parts else 'No results.'
