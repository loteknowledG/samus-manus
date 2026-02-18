import json
import time
import subprocess

from samus_manus_mvp import heartbeat_ui


def test_set_interval_updates_state_and_restarts(tmp_path, monkeypatch):
    # prepare temp state file
    tmp_state = tmp_path / 'heartbeat_state.json'
    monkeypatch.setattr(heartbeat_ui, 'STATE_PATH', tmp_state)

    # capture subprocess.run calls
    calls = []

    def fake_run(cmd, check=False, capture_output=False):
        calls.append(cmd)
        class R: pass
        return R()

    monkeypatch.setattr(subprocess, 'run', fake_run)

    # call set_interval with restart
    ok = heartbeat_ui.set_interval(60, restart=True)
    assert ok

    # verify state updated
    st = json.loads(tmp_state.read_text())
    assert st.get('interval') == 60

    # verify stop and background start were invoked
    assert any('--stop' in c for c in calls[0]) or any('heartbeat.py' in str(c) for c in calls[0])
    # background start should include --background and --interval 60
    start_call = [c for c in calls if '--background' in c]
    assert start_call
    assert '60' in [str(x) for x in start_call[0]]


def test_set_interval_no_restart_writes_state_only(tmp_path, monkeypatch):
    tmp_state = tmp_path / 'heartbeat_state.json'
    monkeypatch.setattr(heartbeat_ui, 'STATE_PATH', tmp_state)

    called = False

    def fake_run(*a, **k):
        nonlocal called
        called = True

    monkeypatch.setattr(subprocess, 'run', fake_run)

    ok = heartbeat_ui.set_interval(120, restart=False)
    assert ok
    st = json.loads(tmp_state.read_text())
    assert st.get('interval') == 120
    assert not called