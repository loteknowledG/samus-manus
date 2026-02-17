"""
Simple persistent memory for Samus‑Manus (SQLite + OpenAI embeddings).
- Stores conversations and task records persistently.
- If OPENAI_API_KEY present, stores embeddings using OpenAI embeddings API and supports similarity search.
- Safe fallback to text-only storage when embeddings are unavailable.

Usage:
  from memory import Memory
  m = Memory()
  m.add('conversation', 'user said hello', meta={})
  m.query_similar('hello', top_k=3)
"""
import os
import json
import sqlite3
import time
from typing import Optional, List, Dict

try:
    import openai
except Exception:
    openai = None

try:
    import numpy as np
except Exception:
    np = None

DB_PATH = os.path.join(os.path.dirname(__file__), 'memory.db')
EMBED_MODEL = os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')


class Memory:
    def __init__(self, path: str = DB_PATH):
        self.path = path
        self._conn = sqlite3.connect(self.path, check_same_thread=False)
        self._conn.execute(
            'CREATE TABLE IF NOT EXISTS memories (id INTEGER PRIMARY KEY, type TEXT, text TEXT, metadata TEXT, embedding TEXT, created_at REAL)'
        )
        self._conn.commit()

    def _get_embedding(self, text: str) -> Optional[List[float]]:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or not openai:
            return None
        try:
            openai.api_key = api_key
            resp = openai.Embedding.create(model=EMBED_MODEL, input=text)
            emb = resp['data'][0]['embedding']
            return emb
        except Exception:
            return None

    def add(self, kind: str, text: str, metadata: Optional[Dict] = None):
        """Add a memory record. Stores embedding if available."""
        meta = json.dumps(metadata or {})
        emb = self._get_embedding(text)
        emb_json = json.dumps(emb) if emb else None
        ts = time.time()
        cur = self._conn.cursor()
        cur.execute(
            'INSERT INTO memories (type, text, metadata, embedding, created_at) VALUES (?, ?, ?, ?, ?)',
            (kind, text, meta, emb_json, ts),
        )
        self._conn.commit()
        return cur.lastrowid

    def all(self, limit: int = 100):
        cur = self._conn.cursor()
        cur.execute('SELECT id, type, text, metadata, embedding, created_at FROM memories ORDER BY created_at DESC LIMIT ?', (limit,))
        rows = cur.fetchall()
        out = []
        for r in rows:
            out.append({
                'id': r[0],
                'type': r[1],
                'text': r[2],
                'metadata': json.loads(r[3] or '{}'),
                'embedding': json.loads(r[4]) if r[4] else None,
                'created_at': r[5],
            })
        return out

    def _cosine_sim(self, a, b):
        if np is not None:
            a = np.array(a, dtype=float)
            b = np.array(b, dtype=float)
            if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
                return 0.0
            return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
        # pure python fallback
        dot = sum(x * y for x, y in zip(a, b))
        norma = sum(x * x for x in a) ** 0.5
        normb = sum(y * y for y in b) ** 0.5
        if norma == 0 or normb == 0:
            return 0.0
        return dot / (norma * normb)

    def query_similar(self, text: str, top_k: int = 5):
        """Return top_k similar memories to `text` using embeddings if available.

        Uses a vectorized numpy path when available for much faster similarity
        ranking on moderate-sized stores; falls back to a row-by-row cosine
        comparison or a simple substring match when embeddings are unavailable.
        """
        emb = self._get_embedding(text)
        cur = self._conn.cursor()

        # If we got a query embedding, prefer semantic (embedding) search
        if emb:
            cur.execute('SELECT id, type, text, metadata, embedding, created_at FROM memories WHERE embedding IS NOT NULL')
            rows = cur.fetchall()
            if rows:
                try:
                    if np is not None:
                        # Vectorized similarity computation (fast)
                        stored_embs = [json.loads(r[4]) for r in rows if r[4]]
                        stored_arr = np.array(stored_embs, dtype=float)
                        query_arr = np.array(emb, dtype=float)
                        # compute cosine similarities in batch
                        stored_norms = np.linalg.norm(stored_arr, axis=1)
                        query_norm = np.linalg.norm(query_arr) + 1e-12
                        sims = (stored_arr @ query_arr) / (stored_norms * query_norm + 1e-12)
                        idxs = np.argsort(sims)[::-1][:top_k]
                        result = []
                        for i in idxs:
                            r = rows[int(i)]
                            result.append({
                                'score': float(sims[int(i)]),
                                'id': r[0],
                                'type': r[1],
                                'text': r[2],
                                'metadata': json.loads(r[3] or '{}'),
                                'created_at': r[5],
                            })
                        return result
                    else:
                        # numpy not available: fall back to existing per-row scoring
                        scored = []
                        for r in rows:
                            stored_emb = json.loads(r[4])
                            if not stored_emb:
                                continue
                            sim = self._cosine_sim(emb, stored_emb)
                            scored.append((sim, r))
                        scored.sort(key=lambda x: x[0], reverse=True)
                        result = []
                        for sim, r in scored[:top_k]:
                            result.append({
                                'score': float(sim),
                                'id': r[0],
                                'type': r[1],
                                'text': r[2],
                                'metadata': json.loads(r[3] or '{}'),
                                'created_at': r[5],
                            })
                        return result
                except Exception:
                    # if something goes wrong with embeddings, fall back to substring search
                    pass

        # Fallback: simple substring match when embeddings are not available
        cur.execute('SELECT id, type, text, metadata, created_at FROM memories')
        rows = cur.fetchall()
        matches = []
        q = text.lower()
        for r in rows:
            t = (r[2] or '').lower()
            score = 1.0 if q in t else 0.0
            if score > 0:
                matches.append((score, r))
        matches.sort(key=lambda x: x[0], reverse=True)
        out = []
        for score, r in matches[:top_k]:
            out.append({'score': score, 'id': r[0], 'type': r[1], 'text': r[2], 'metadata': json.loads(r[3] or '{}'), 'created_at': r[4]})
        return out

    def rebuild_missing_embeddings(self, limit: int = 100):
        """Compute embeddings for records missing them (requires OPENAI_API_KEY).

        Returns the number of records updated. Useful when an API key is added
        after data was created.
        """
        cur = self._conn.cursor()
        cur.execute('SELECT id, text FROM memories WHERE embedding IS NULL LIMIT ?', (limit,))
        rows = cur.fetchall()
        updated = 0
        for r in rows:
            rid, txt = r
            emb = self._get_embedding(txt)
            if emb:
                cur.execute('UPDATE memories SET embedding = ? WHERE id = ?', (json.dumps(emb), rid))
                updated += 1
        self._conn.commit()
        return updated


# convenience singleton
_global_memory = None

def get_memory() -> Memory:
    global _global_memory
    if _global_memory is None:
        _global_memory = Memory()
    return _global_memory