#!/usr/bin/env python3
"""Always-on-top heartbeat overlay — small flip-counter style countdown.

- Shows time until next heartbeat (MM:SS) and stays on top.
- Click-and-drag to move. Double-click to open the full Heartbeat UI.
- Lightweight flip animation when seconds change.

Usage: python samus_manus_mvp/heartbeat_overlay.py
"""
from pathlib import Path
import json
import time
import subprocess
import sys

try:
    import tkinter as tk
    from tkinter import font as tkfont
except Exception:
    tk = None

BASE = Path(__file__).parent
STATE_PATH = BASE / 'heartbeat_state.json'
HEARTBEAT_UI = BASE / 'heartbeat_ui.py'
DEFAULT_INTERVAL = 1800


# Write interval immediately to state (used by live knob updates)
def write_interval_state(interval: int) -> bool:
    try:
        st = load_state()
        st['interval'] = int(interval)
        st['last_heartbeat'] = time.time()
        STATE_PATH.write_text(json.dumps(st, indent=2))
        return True
    except Exception:
        return False


def load_state():
    if not STATE_PATH.exists():
        return {}
    try:
        return json.loads(STATE_PATH.read_text(encoding='utf-8'))
    except Exception:
        return {}


def format_seconds(s: int | None) -> str:
    if s is None or s < 0:
        return '--:--'
    s = int(max(0, s))
    mm = s // 60
    ss = s % 60
    return f"{mm:02d}:{ss:02d}"


def seconds_until_next(state: dict) -> int | None:
    last = state.get('last_heartbeat')
    interval = int(state.get('interval') or DEFAULT_INTERVAL)
    if not last:
        return interval
    try:
        rem = int((float(last) + interval) - time.time())
        return max(0, rem)
    except Exception:
        return None


# --- helpers for audit/tasks (used by overlay) ---
def load_audit_entries(path: Path | None = None) -> list:
    p = Path(path) if path else (BASE / 'approval_audit.log')
    if not p.exists():
        return []
    out = []
    try:
        with open(p, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    out.append(json.loads(line))
                except Exception:
                    continue
    except Exception:
        return []
    return out


def count_auto_approvals(path: Path | None = None) -> int:
    entries = load_audit_entries(path)
    return sum(1 for e in entries if e.get('auto'))


def count_pending_tasks(path: Path | None = None) -> int:
    p = Path(path) if path else (BASE / 'tasks.json')
    if not p.exists():
        return 0
    try:
        data = json.loads(p.read_text(encoding='utf-8'))
        tasks = data.get('tasks', []) if isinstance(data, dict) else []
        return sum(1 for t in tasks if t.get('status') == 'pending')
    except Exception:
        return 0


# ---- GUI ----

def _flip_animation(lbl, new_text, base_size=28):
    """Simple scale animation to mimic a flip counter change."""
    try:
        steps = [base_size + 6, base_size + 3, base_size]
        for s in steps:
            lbl.config(font=(lbl_font_name, s, 'bold'))
            lbl.update_idletasks()
            time.sleep(0.03)
        lbl.config(text=new_text)
    except Exception:
        try:
            lbl.config(text=new_text)
        except Exception:
            pass


lbl_font_name = 'Helvetica'


def build_overlay():
    """Industrial flip‑tile overlay: three tiles (auto / countdown / pending).

    - Center tile is the large countdown (MM:SS)
    - Left/right tiles are smaller counters
    - Designed to visually echo the industrial flip counter you attached
    """
    if tk is None:
        print('Tkinter not available.')
        return None

    root = tk.Tk()
    root.title('Heartbeat')
    root.overrideredirect(True)
    root.attributes('-topmost', True)
    try:
        root.wm_attributes('-transparentcolor', 'magenta')
    except Exception:
        pass

    # main container (dark metallic feel)
    container = tk.Frame(root, bg='#1a1a1a', bd=4, relief='flat')
    container.pack(padx=6, pady=6)

    tiles = tk.Frame(container, bg='#1a1a1a')
    tiles.pack()

    # helper to create a tile (frame + number label + sublabel)
    def make_tile(parent, font_size, width=120, height=80, label_text=''):
        pad = 6
        frame = tk.Frame(parent, bg='#101010', bd=2, relief='raised', width=width, height=height)
        frame.pack_propagate(False)
        frame.pack(side='left', padx=8)

        # decorative sliders (left + right)
        ldec = tk.Canvas(frame, width=10, height=height, bg='#101010', highlightthickness=0)
        ldec.pack(side='left', padx=(6,2), pady=6)
        ldec.create_rectangle(1, height*0.35, 9, height*0.65, fill='#c7c7c7', outline='#777')

        lbl_num = tk.Label(frame, text='--', fg='#f2f2f2', bg='#101010')
        lbl_num.config(font=(lbl_font_name, font_size, 'bold'))
        lbl_num.pack(side='left', padx=8)

        rdec = tk.Canvas(frame, width=10, height=height, bg='#101010', highlightthickness=0)
        rdec.pack(side='left', padx=(2,6), pady=6)
        rdec.create_rectangle(1, height*0.35, 9, height*0.65, fill='#c7c7c7', outline='#777')

        sub = tk.Label(frame, text=label_text, fg='#9aa0a6', bg='#101010', font=(lbl_font_name, 8))
        sub.pack(side='bottom', pady=(0,6))
        return frame, lbl_num, sub

    # left: auto-approved (small)
    left_frame, left_lbl, left_sub = make_tile(tiles, font_size=18, width=110, height=70, label_text='AUTO')
    # center: large countdown
    center_frame, center_lbl, center_sub = make_tile(tiles, font_size=56, width=260, height=100, label_text='NEXT')
    # right: pending (small)
    right_frame, right_lbl, right_sub = make_tile(tiles, font_size=18, width=110, height=70, label_text='PENDING')

    # drag handling (allow dragging by any tile area)
    offset = {'x': 0, 'y': 0}

    def on_press(e):
        offset['x'] = e.x
        offset['y'] = e.y

    def on_drag(e):
        x = root.winfo_x() + (e.x - offset['x'])
        y = root.winfo_y() + (e.y - offset['y'])
        root.geometry(f'+{x}+{y}')

    for w in (left_frame, center_frame, right_frame, tiles):
        w.bind('<ButtonPress-1>', on_press)
        w.bind('<B1-Motion>', on_drag)

    # double-click opens full UI
    def on_double(e=None):
        try:
            subprocess.Popen([sys.executable, str(HEARTBEAT_UI)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    for w in (left_frame, center_frame, right_frame):
        w.bind('<Double-Button-1>', on_double)

    prev = {'countdown': None, 'auto': None, 'pending': None}

    # --- knob / popup to set countdown interval directly from overlay ---
    popup_ref = {'w': None}

    def set_overlay_interval(interval: int, restart: bool = True) -> bool:
        """Programmatic helper used by the overlay knob. Tries to use heartbeat_ui.set_interval,
        falls back to persisting state.json when heartbeat_ui isn't available."""
        try:
            # import locally to avoid import cycles in some test runners
            from samus_manus_mvp.heartbeat_ui import set_interval as hb_set_interval
            return bool(hb_set_interval(int(interval), restart=restart))
        except Exception:
            # best-effort: write state file so seconds_until_next reflects new interval
            try:
                st = load_state()
                st['interval'] = int(interval)
                # also bump last_heartbeat so the new countdown is applied immediately
                st['last_heartbeat'] = time.time()
                STATE_PATH.write_text(json.dumps(st, indent=2))
                return True
            except Exception:
                return False

    def show_knob_popup(event=None):
        # if popup already open, bring to front
        if popup_ref['w'] and popup_ref['w'].winfo_exists():
            popup_ref['w'].lift()
            return
        st = load_state()
        current = int(st.get('interval', 60))

        pw = tk.Toplevel(root)
        pw.wm_overrideredirect(False)
        pw.title('Set auto-approval countdown')
        popup_ref['w'] = pw

        lab = tk.Label(pw, text='Countdown until auto-approval (seconds):')
        lab.pack(padx=8, pady=(8, 4))

        scale = tk.Scale(pw, from_=5, to=3600, orient='horizontal', length=300)
        scale.set(current)
        scale.pack(padx=8)

        val_lbl = tk.Label(pw, text=f'{current}s')
        val_lbl.pack(pady=(4, 8))

        # live update on each tick: write state immediately so overlay/heartbeat reflect change
        def on_move(v=None):
            v_int = int(scale.get())
            val_lbl.config(text=f"{v_int}s")
            try:
                write_interval_state(v_int)
            except Exception:
                pass

        scale.config(command=on_move)

        # restart background heartbeat when the user releases the slider
        def on_release(evt=None):
            try:
                v = int(scale.get())
                set_overlay_interval(v, restart=True)
            except Exception:
                pass

        scale.bind('<ButtonRelease-1>', on_release)

        # single close button (no Apply needed — dial is live)
        btn_frame = tk.Frame(pw)
        btn_frame.pack(pady=(6,8))
        tk.Button(btn_frame, text='Close', command=lambda: pw.destroy()).pack()

        # position popup near overlay center tile
        try:
            x = root.winfo_rootx() + center_frame.winfo_x()
            y = root.winfo_rooty() + center_frame.winfo_y() + center_frame.winfo_height() + 6
            pw.geometry(f'+{x}+{y}')
        except Exception:
            pass

    # right-click on center tile to open the knob popup
    center_frame.bind('<Button-3>', show_knob_popup)
    center_lbl.bind('<Button-3>', show_knob_popup)
    center_sub.bind('<Button-3>', show_knob_popup)

    def refresh_loop():
        st = load_state()
        secs = seconds_until_next(st)
        countdown_text = format_seconds(secs)

        # animate center tile on change
        if prev['countdown'] != countdown_text:
            try:
                _flip_animation(center_lbl, countdown_text, base_size=56)
            except Exception:
                center_lbl.config(text=countdown_text)
            prev['countdown'] = countdown_text

        # update metrics
        try:
            auto_count = count_auto_approvals()
            pending_count = count_pending_tasks()
        except Exception:
            auto_count = 0
            pending_count = 0

        if prev['auto'] != auto_count:
            # small scale pulse for change
            try:
                _flip_animation(left_lbl, str(auto_count), base_size=18)
            except Exception:
                left_lbl.config(text=str(auto_count))
            prev['auto'] = auto_count

        if prev['pending'] != pending_count:
            try:
                _flip_animation(right_lbl, str(pending_count), base_size=18)
            except Exception:
                right_lbl.config(text=str(pending_count))
            prev['pending'] = pending_count

        # ensure center label shows countdown even if unchanged numeric counts changed
        if prev['countdown'] is None:
            center_lbl.config(text=countdown_text)

        root.after(400, refresh_loop)

    refresh_loop()
    return root


def main():
    root = build_overlay()
    if root:
        root.mainloop()


if __name__ == '__main__':
    main()
