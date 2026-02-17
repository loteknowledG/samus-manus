#!/usr/bin/env python3
"""
Local heartbeat watcher + task runner (no external services).
- Announces via local TTS (pyttsx3) if available.
- Periodically checks `tasks.json` for pending tasks and runs them (simulated by default).
- Stores last heartbeat timestamp in `heartbeat_state.json`.
"""
import json
import time
import argparse
from pathlib import Path
import subprocess

# local helper TTS (optional)
try:
    from voice_loop import speak
except Exception:
    def speak(text):
        print("[TTS disabled]", text)

BASE = Path(__file__).parent
STATE_PATH = BASE / 'heartbeat_state.json'
TASKS_PATH = BASE / 'tasks.json'


def load_state():
    if not STATE_PATH.exists():
        return {'last_heartbeat': None, 'last_task_check': None}
    try:
        return json.loads(STATE_PATH.read_text())
    except Exception:
        return {'last_heartbeat': None, 'last_task_check': None}


def save_state(state: dict):
    STATE_PATH.write_text(json.dumps(state, indent=2))


def load_tasks():
    if not TASKS_PATH.exists():
        TASKS_PATH.write_text(json.dumps({'tasks': []}, indent=2))
        return []
    try:
        data = json.loads(TASKS_PATH.read_text())
        return data.get('tasks', [])
    except Exception:
        return []


def run_task_sim(task_text: str):
    """Run the samus agent in simulation mode for a task (subprocess)."""
    try:
        proc = subprocess.run([
            'python', str(BASE / 'samus_agent.py'), 'run', task_text, '--no-approve'
        ], capture_output=True, text=True, timeout=120)
        return proc.stdout + proc.stderr
    except Exception as e:
        return f'Error running task: {e}'


def check_once(announce: bool = False):
    state = load_state()
    tasks = load_tasks()

    # announce heartbeat
    ts = time.strftime('%Y-%m-%d %H:%M:%S')
    msg = f"Samus‑Manus heartbeat at {ts}. Pending tasks: {sum(1 for t in tasks if t.get('status')=='pending')}"
    print(msg)
    if announce:
        try:
            speak(msg)
        except Exception as e:
            print('TTS failed:', e)

    # handle pending tasks
    changed = False
    for t in tasks:
        if t.get('status') == 'pending':
            print('Found pending task:', t.get('id'), t.get('task'))
            if announce:
                speak(f"Running task: {t.get('task')}")
            result = run_task_sim(t.get('task'))
            t['status'] = 'done'
            t['result'] = result
            t['completed_at'] = time.time()
            changed = True
            print('Task result:', result.splitlines()[:5])

    if changed:
        save_tasks(tasks)

    state['last_heartbeat'] = time.time()
    state['last_task_check'] = time.time()
    save_state(state)
    return True


def main():
    ap = argparse.ArgumentParser(prog='heartbeat', description='Samus‑Manus local heartbeat')
    ap.add_argument('--interval', type=int, default=1800, help='Interval seconds (default 1800)')
    ap.add_argument('--announce', action='store_true', help='Use TTS to announce heartbeat and tasks')
    ap.add_argument('--once', action='store_true', help='Run one check and exit')
    args = ap.parse_args()

    if args.once:
        check_once(announce=args.announce)
        return

    print(f'Starting local heartbeat (interval={args.interval}s) — press Ctrl+C to stop')
    try:
        while True:
            check_once(announce=args.announce)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print('\nHeartbeat stopped by user')
