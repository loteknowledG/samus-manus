import json
import time

from samus_manus_mvp import heartbeat


def test_heartbeat_writes_audit_for_auto_approved_task(tmp_path, monkeypatch, capsys):
    # prepare temp state + tasks + audit files
    tmp_dir = tmp_path / 'hb'
    tmp_dir.mkdir()

    tasks = [
        {"id": "task-x", "task": "make an approval", "status": "pending", "created_at": int(time.time()), "auto_approve": True}
    ]
    (tmp_dir / 'tasks.json').write_text(json.dumps({'tasks': tasks}))

    # empty audit file
    audit_path = tmp_dir / 'approval_audit.log'
    audit_path.write_text('')

    # redirect module paths
    monkeypatch.setattr(heartbeat, 'BASE', tmp_dir)
    monkeypatch.setattr(heartbeat, 'TASKS_PATH', tmp_dir / 'tasks.json')
    monkeypatch.setattr(heartbeat, 'STATE_PATH', tmp_dir / 'heartbeat_state.json')

    # run heartbeat once (whitelist mode)
    heartbeat.check_once(announce=False, global_auto_apply=False, mode='whitelist')

    # verify pending task was processed
    data = json.loads((tmp_dir / 'tasks.json').read_text())
    assert data['tasks'][0]['status'] == 'done'

    # verify audit entry was appended for auto-approval
    lines = [l for l in (tmp_dir / 'approval_audit.log').read_text().splitlines() if l.strip()]
    assert len(lines) >= 1
    entry = json.loads(lines[-1])
    assert entry.get('auto') is True
    # new fields: answer + question should be present
    assert entry.get('answer') == 'y'
    assert 'question' in entry and 'make an approval' in entry.get('question')
    assert entry.get('task') == 'make an approval'