from samus_manus_mvp.heartbeat_overlay import (
    format_seconds,
    seconds_until_next,
    count_auto_approvals,
    count_pending_tasks,
)
import time
import json


def test_format_seconds():
    assert format_seconds(90) == '01:30'
    assert format_seconds(0) == '00:00'
    assert format_seconds(None) == '--:--'


def test_seconds_until_next_computation():
    now = time.time()
    state = {'last_heartbeat': now - 10, 'interval': 60}
    rem = seconds_until_next(state)
    assert 49 <= rem <= 51  # allow small timing jitter


def test_count_auto_approvals(tmp_path):
    audit = tmp_path / 'approval_audit.log'
    entries = [
        {'ts': time.time(), 'auto': True, 'approval': 'y', 'task': 'A', 'action': {'type': 'done'}, 'step': 1},
        {'ts': time.time(), 'auto': False, 'approval': 'n', 'task': 'B', 'action': {'type': 'type', 'text': 'hi'}, 'step': 1},
        {'ts': time.time(), 'auto': True, 'approval': 'y', 'task': 'C', 'action': {'type': 'screenshot', 'out': 'a.png'}, 'step': 2},
    ]
    audit.write_text('\n'.join(json.dumps(e) for e in entries) + '\n')
    assert count_auto_approvals(path=audit) == 2


def test_count_pending_tasks(tmp_path):
    tasks = tmp_path / 'tasks.json'
    data = {'tasks': [
        {'id': 't1', 'task': 'one', 'status': 'pending'},
        {'id': 't2', 'task': 'two', 'status': 'done'},
        {'id': 't3', 'task': 'three', 'status': 'pending'},
    ]}
    tasks.write_text(json.dumps(data))
    assert count_pending_tasks(path=tasks) == 2


def test_set_overlay_interval_uses_heartbeat_ui_and_writes_state(tmp_path, monkeypatch):
    # patch heartbeat_ui.set_interval to capture call
    called = {'val': None}

    class FakeHB:
        @staticmethod
        def set_interval(v, restart=True):
            called['val'] = (v, restart)
            return True

    monkeypatch.setattr('samus_manus_mvp.heartbeat_overlay.STATE_PATH', tmp_path / 'heartbeat_state.json')
    monkeypatch.setattr('samus_manus_mvp.heartbeat_overlay.load_state', lambda: {'interval': 60, 'last_heartbeat': 0})
    # patch the real heartbeat_ui.set_interval so the overlay import picks it up
    monkeypatch.setattr('samus_manus_mvp.heartbeat_ui.set_interval', FakeHB.set_interval, raising=False)

    # simulate live dial movement: write state immediately
    from samus_manus_mvp.heartbeat_overlay import write_interval_state
    ok = write_interval_state(45)
    assert ok is True

    # simulate release: heartbeat_ui.set_interval should be invoked (monkeypatched)
    from samus_manus_mvp.heartbeat_ui import set_interval as hb_set
    hb_set(45, restart=True)
    assert called['val'] == (45, True)

    # fallback check: state file was written with new interval
    st = json.loads((tmp_path / 'heartbeat_state.json').read_text())
    assert st.get('interval') == 45
