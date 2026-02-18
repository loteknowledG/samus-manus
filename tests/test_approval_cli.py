import json
import time

from samus_manus_mvp import approval_cli


def test_approval_cli_list_shows_action_summary(tmp_path, monkeypatch, capsys):
    tmp_dir = tmp_path / 'audit'
    tmp_dir.mkdir()

    audit_path = tmp_dir / 'approval_audit.log'
    entry = {
        'ts': time.time(),
        'auto': True,
        'approval': 'y',
        'task': 'Take a screenshot',
        'action': {'type': 'screenshot', 'out': 'samus_screenshot.png'},
        'step': 2,
    }
    audit_path.write_text(json.dumps(entry) + "\n")

    # redirect module AUDIT_PATH to our temp file
    monkeypatch.setattr(approval_cli, 'AUDIT_PATH', audit_path)

    approval_cli.cmd_list(limit=10, auto_only=False, task=None, since_seconds=0, raw=False)
    out = capsys.readouterr().out
    assert 'Take a screenshot' in out
    assert 'screenshot' in out or 'samus_screenshot.png' in out
    assert 'auto' in out
    assert 'y' in out