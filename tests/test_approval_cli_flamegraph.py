import json
import time

from samus_manus_mvp import approval_cli


def test_aa_default_is_last5_text(tmp_path, monkeypatch, capsys):
    tmp_dir = tmp_path / 'audit'
    tmp_dir.mkdir()
    audit_path = tmp_dir / 'approval_audit.log'

    # create 3 entries
    entries = []
    for i in range(3):
        entries.append({'ts': time.time(), 'auto': True, 'approval': 'y', 'task': f'T{i}', 'question': f'Q{i}', 'answer': 'y'})
    audit_path.write_text('\n'.join(json.dumps(e) for e in entries) + '\n')

    monkeypatch.setattr(approval_cli, 'AUDIT_PATH', audit_path)

    # call aa with no args -> should default to last 5 text-only
    approval_cli.cmd_aa('last', None, False, None)
    out = capsys.readouterr().out.strip().splitlines()
    # since text-only default, lines should equal questions
    assert out[0].strip() == 'Q0'


def test_aa_flamegraph_shows_histogram(tmp_path, monkeypatch, capsys):
    tmp_dir = tmp_path / 'audit'
    tmp_dir.mkdir()
    audit_path = tmp_dir / 'approval_audit.log'

    entries = []
    # T1 x5, T2 x2, T3 x1
    for _ in range(5):
        entries.append({'ts': time.time(), 'auto': True, 'approval': 'y', 'task': 'T1', 'question': 'Q', 'answer': 'y'})
    for _ in range(2):
        entries.append({'ts': time.time(), 'auto': True, 'approval': 'y', 'task': 'T2', 'question': 'Q', 'answer': 'y'})
    entries.append({'ts': time.time(), 'auto': True, 'approval': 'y', 'task': 'T3', 'question': 'Q', 'answer': 'y'})

    audit_path.write_text('\n'.join(json.dumps(e) for e in entries) + '\n')
    monkeypatch.setattr(approval_cli, 'AUDIT_PATH', audit_path)

    approval_cli.cmd_aa('flamegraph', 3, False, None)
    out = capsys.readouterr().out.strip().splitlines()
    # top line should be T1 with a bar and count 5
    assert any('T1' in l and '5' in l for l in out)
    assert any('T2' in l and '2' in l for l in out)
    assert any('T3' in l and '1' in l for l in out)