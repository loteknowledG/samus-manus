from samus_manus_mvp.memory import Memory
from pathlib import Path
import tempfile
p = Path(tempfile.gettempdir()) / 'test_mem_local.db'
try:
    p.unlink()
except Exception:
    pass
m = Memory(str(p))
m.add('note','Remember to water plants', metadata={'tag':'test'})
all_items = m.all(limit=10)
print('all count', len(all_items))
assert len(all_items) == 1
print('query fallback', m.query_similar('remember'))
print('rebuild_missing_embeddings', m.rebuild_missing_embeddings(limit=10))
print('OK')
