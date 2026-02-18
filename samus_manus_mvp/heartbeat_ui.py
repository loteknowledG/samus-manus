#!/usr/bin/env python3
"""Heartbeat Tempo UI — simple dial/slider to control the heartbeat interval.

Features:
- Slider/dial to set heartbeat interval (seconds)
- Start / Stop heartbeat
- Apply new interval (updates `heartbeat_state.json` and restarts background heartbeat)

Usage: python samus_manus_mvp/heartbeat_ui.py
"""
from pathlib import Path
import json
import subprocess
import sys
import threading
import time

try:
    import tkinter as tk
    from tkinter import ttk
except Exception:
    tk = None

BASE = Path(__file__).parent
STATE_PATH = BASE / 'heartbeat_state.json'
HEARTBEAT_PY = BASE / 'heartbeat.py'


def load_state():
    if not STATE_PATH.exists():
        return {}
    try:
        return json.loads(STATE_PATH.read_text(encoding='utf-8'))
    except Exception:
        return {}


def save_state(state: dict):
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding='utf-8')


def stop_heartbeat():
    """Attempt to stop a running background heartbeat (best-effort)."""
    try:
        subprocess.run([sys.executable, str(HEARTBEAT_PY), '--stop'], check=False, capture_output=True)
        # small delay to let the process terminate and state file be updated
        time.sleep(0.2)
        return True
    except Exception:
        return False


def start_heartbeat(interval: int, announce: bool = True):
    """Start a detached background heartbeat with the given interval and preserve auto-apply settings from state."""
    state = load_state()
    cmd = [sys.executable, str(HEARTBEAT_PY), '--background', '--interval', str(interval)]
    if announce:
        cmd.append('--announce')
    if state.get('auto_apply'):
        cmd.append('--auto-apply')
    if state.get('auto_apply_mode'):
        cmd += ['--auto-apply-mode', str(state.get('auto_apply_mode'))]
    try:
        subprocess.run(cmd, check=False, capture_output=True)
        # persist chosen interval in state for UI convenience
        state['interval'] = interval
        save_state(state)
        return True
    except Exception:
        return False


def set_interval(interval: int, restart: bool = True):
    """Set the heartbeat interval in `heartbeat_state.json` and optionally restart background heartbeat.

    This is testable (doesn't require GUI)."""
    state = load_state()
    state['interval'] = int(interval)
    save_state(state)
    if restart:
        # best-effort restart: stop then start with preserved preferences
        stop_heartbeat()
        return start_heartbeat(interval)
    return True


# ---- GUI ----

def _human_readable(sec: int) -> str:
    if sec < 60:
        return f"{sec}s"
    if sec % 60 == 0:
        return f"{sec//60} min"
    return f"{sec//60}m {sec%60}s"


def build_ui():
    if tk is None:
        print('Tkinter not available on this system.')
        return

    root = tk.Tk()
    root.title('Samus‑Manus — Heartbeat tempo')
    root.geometry('420x220')

    state = load_state()
    current = int(state.get('interval', 1800))

    frm = ttk.Frame(root, padding=12)
    frm.pack(fill=tk.BOTH, expand=True)

    ttk.Label(frm, text='Heartbeat tempo (seconds)').grid(column=0, row=0, sticky='w')
    slider = ttk.Scale(frm, from_=10, to=3600, orient='horizontal')
    slider.set(current)
    slider.grid(column=0, row=1, sticky='ew', pady=6)

    value_label = ttk.Label(frm, text=_human_readable(current))
    value_label.grid(column=0, row=2, sticky='w')

    def on_slide(evt=None):
        v = int(slider.get())
        value_label.config(text=_human_readable(v))

    slider.bind('<Motion>', on_slide)
    slider.bind('<ButtonRelease-1>', on_slide)

    # controls
    btn_frame = ttk.Frame(frm)
    btn_frame.grid(column=0, row=3, pady=12, sticky='ew')

    status_var = tk.StringVar(value='Status: unknown')
    status_label = ttk.Label(frm, textvariable=status_var)
    status_label.grid(column=0, row=4, sticky='w')

    def refresh_status():
        st = load_state()
        pid = st.get('heartbeat_pid')
        if pid:
            status_var.set(f'Status: running (pid={pid})')
        else:
            status_var.set('Status: stopped')

    def apply_click():
        v = int(slider.get())

        def work():
            status_var.set('Applying...')
            ok = set_interval(v, restart=True)
            refresh_status()
            status_var.set('Applied' if ok else 'Failed to apply')

        threading.Thread(target=work, daemon=True).start()

    def start_click():
        v = int(slider.get())

        def work():
            status_var.set('Starting...')
            ok = start_heartbeat(v, announce=True)
            refresh_status()
            status_var.set('Started' if ok else 'Failed to start')

        threading.Thread(target=work, daemon=True).start()

    def stop_click():
        def work():
            status_var.set('Stopping...')
            ok = stop_heartbeat()
            refresh_status()
            status_var.set('Stopped' if ok else 'Stop failed')

        threading.Thread(target=work, daemon=True).start()

    apply_btn = ttk.Button(btn_frame, text='Apply & Restart', command=apply_click)
    apply_btn.pack(side='left', padx=6)
    start_btn = ttk.Button(btn_frame, text='Start', command=start_click)
    start_btn.pack(side='left', padx=6)
    stop_btn = ttk.Button(btn_frame, text='Stop', command=stop_click)
    stop_btn.pack(side='left', padx=6)

    # auto-apply checkbox (persist preference)
    auto_var = tk.BooleanVar(value=bool(state.get('auto_apply')))

    def on_auto_toggle():
        st = load_state()
        st['auto_apply'] = bool(auto_var.get())
        save_state(st)

    auto_chk = ttk.Checkbutton(frm, text='Preserve auto_apply (whitelist)', variable=auto_var, command=on_auto_toggle)
    auto_chk.grid(column=0, row=5, sticky='w')

    refresh_status()
    return root


def main():
    root = build_ui()
    if root:
        root.mainloop()


if __name__ == '__main__':
    main()
