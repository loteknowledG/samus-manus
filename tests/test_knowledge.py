import json
import time

from samus_manus_mvp import knowledge
from samus_manus_mvp.memory import Memory


def test_retrieve_memories_and_approvals(tmp_path, monkeypatch):
    # create temporary memory DB
    mem_path = tmp_path / 'mem.db'
    m = Memory(str(mem_path))
    # add persona + a few memories
    m.add('persona', 'cautious, audit-first')
    m.add('note', 'I like saving screenshots of UI', metadata={'task': 'Take a screenshot'})

    # write an approval audit log
    audit = tmp_path / 'approval_audit.log'
    entry = {'ts': time.time(), 'auto': True, 'answer': 'y', 'question': 'Screenshot ok?', 'task': 'Take a screenshot'}
    audit.write_text(json.dumps(entry) + '\n')

    # patch module paths so knowledge reads from our temp files
    monkeypatch.setattr(knowledge, 'AUDIT_PATH', audit)
    monkeypatch.setattr('samus_manus_mvp.knowledge.get_memory', lambda: m, raising=False)

    res = knowledge.retrieve('screenshot', top_k=5)
    assert res.get('persona') is not None
    assert isinstance(res.get('memory'), list)
    assert len(res.get('approvals', [])) == 1
    assert 'Screenshot' in res['approvals'][0].get('question')
