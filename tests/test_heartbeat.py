import json
import time

from samus_manus_mvp import heartbeat


def test_heartbeat_includes_approval_question(tmp_path, monkeypatch, capsys):
    # prepare isolated task + audit files in a temp directory
    tmp_dir = tmp_path / 'hb'
    tmp_dir.mkdir()

    # create a pending task
    tasks = [
        {"id": "task-1", "task": "Take a screenshot", "status": "pending", "created_at": int(time.time())}
    ]
    tasks_path = tmp_dir / 'tasks.json'
    tasks_path.write_text(json.dumps({'tasks': tasks}))

    # write an audit entry that contains the action (the "question" we want reported)
    audit_entry = {
        'ts': time.time(),
        'auto': True,
        'approval': 'y',
        'task': 'Take a screenshot',
        'action': {'type': 'screenshot', 'out': 'samus_screenshot.png'},
        'step': 1,
    }
    audit_path = tmp_dir / 'approval_audit.log'
    audit_path.write_text(json.dumps(audit_entry) + '\n')

    # redirect heartbeat module paths to tmp files
    monkeypatch.setattr(heartbeat, 'BASE', tmp_dir)
    monkeypatch.setattr(heartbeat, 'TASKS_PATH', tasks_path)
    monkeypatch.setattr(heartbeat, 'STATE_PATH', tmp_dir / 'heartbeat_state.json')

    # run heartbeat once (no TTS announce) and capture stdout
    heartbeat.check_once(announce=False)
    out = capsys.readouterr().out

    # verify the task and the audit "question" (action summary) appear in the output
    assert 'Take a screenshot' in out
    assert 'audit' in out
    assert 'screenshot' in out or 'samus_screenshot.png' in out