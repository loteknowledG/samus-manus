#!/usr/bin/env python
import argparse, subprocess, sys, os, time, datetime, shlex

ROOT = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(ROOT)  # repo root


def speak(msg: str):
    try:
        import pyttsx3
        e = pyttsx3.init(); e.setProperty('rate', 180); e.say(msg); e.runAndWait()
    except Exception:
        pass


def run_draw_with_snaps(what: str, label: str, outdir: str, focus: bool, minimize: bool, speak_msg: str|None):
    py = sys.executable
    script = os.path.join(ROOT, 'tools', 'draw_with_snaps.py')
    args = [py, script, '--what', what, '--label', label, '--outdir', outdir]
    if focus:
        args.append('--focus')
    if minimize:
        args.append('--minimize')
    if speak_msg:
        args.extend(['--speak', speak_msg])
    proc = subprocess.run(args, capture_output=True, text=True)
    stdout = (proc.stdout or '').strip().splitlines()
    # draw_with_snaps prints two lines: before path, after path
    snaps = [line.strip() for line in stdout if line.strip().lower().endswith('.png')]
    before = snaps[0] if snaps else ''
    after  = snaps[1] if len(snaps) > 1 else ''
    return proc.returncode, before, after, stdout, (proc.stderr or '')


def ensure_app(app: str):
    # Try to launch the target app if not already open
    try:
        if app.lower() in ('mspaint', 'paint', 'mspaint.exe'):
            subprocess.Popen(['mspaint'])
        else:
            subprocess.Popen([app])
    except Exception:
        pass


def append_record(label: str, what: str, before: str, after: str):
    path = os.path.join(ROOT, 'RECORDS.md')
    ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M local')
    line = f"- {ts} — Warp jump '{label}' ({what}) — before: {os.path.basename(before)}, after: {os.path.basename(after)}\n"
    try:
        with open(path, 'a', encoding='utf-8') as f:
            f.write(line)
    except Exception:
        pass


def main():
    ap = argparse.ArgumentParser(description='Warp jump: announce, draw with snaps, log')
    ap.add_argument('--what', choices=['smiley','house','both'], default='smiley')
    ap.add_argument('--label', default='warp-jump')
    ap.add_argument('--app', default='mspaint')
    ap.add_argument('--outdir', default='.')
    ap.add_argument('--no-speak', action='store_true')
    args = ap.parse_args()

    if not args.no_speak:
        speak(f"Warp jump: {args.label} in {args.app}")

    ensure_app(args.app)
    time.sleep(1.2)

    code, before, after, out_lines, err = run_draw_with_snaps(
        what=args.what, label=args.label, outdir=os.path.abspath(args.outdir), focus=True, minimize=True,
        speak_msg=(None if args.no_speak else 'Done')
    )

    append_record(args.label, args.what, before, after)

    if not args.no_speak:
        speak(f"Warp jump complete: {args.label}")

    # Print a compact summary to stdout
    print({'code': code, 'before': before, 'after': after})


if __name__ == '__main__':
    main()
