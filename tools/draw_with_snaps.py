#!/usr/bin/env python
import argparse, time, math, os, datetime
try:
    import win32gui, win32con
except Exception:
    win32gui = None
try:
    import winsound
except Exception:
    winsound = None
import pyautogui as p

p.FAILSAFE = True
p.PAUSE = 0.01


def _find_paint():
    if not win32gui:
        return None
    targets = []
    def enum(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            t = win32gui.GetWindowText(hwnd)
            if t and 'paint' in t.lower():
                targets.append(hwnd)
    win32gui.EnumWindows(enum, None)
    return targets[0] if targets else None


def focus_paint():
    hwnd = _find_paint()
    if hwnd:
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            time.sleep(0.1)
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.1)
            return True
        except Exception:
            pass
    # Fallback: try Alt+Space -> X (maximize current window)
    try:
        p.hotkey('alt','space'); time.sleep(0.2); p.press('x')
    except Exception:
        pass
    return False


def minimize_paint():
    hwnd = _find_paint()
    if hwnd:
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            return True
        except Exception:
            pass
    return False


def snap(path):
    p.screenshot(path)
    print(path)


def draw_smiley():
    W, H = p.size(); cx, cy = W//2, H//2
    for _ in range(2):
        p.click(cx, cy); time.sleep(0.05)
    R = max(80, min(W, H)//6)
    # head
    p.moveTo(cx + R, cy)
    for a in range(0, 361, 4):
        x = cx + int(R*math.cos(math.radians(a)))
        y = cy + int(R*math.sin(math.radians(a)))
        p.dragTo(x, y, duration=0.008)
    # eyes
    er = max(10, R//8)
    for ox in (-R//2, R//2):
        p.moveTo(cx + ox + er, cy - R//3)
        for a in range(0, 361, 12):
            x = cx + ox + int(er*math.cos(math.radians(a)))
            y = cy - R//3 + int(er*math.sin(math.radians(a)))
            p.dragTo(x, y, duration=0.008)
    # mouth
    mr = R//2
    p.moveTo(cx - mr, cy + R//3)
    for a in range(0, 181, 6):
        x = cx - mr + int(2*mr*(a/180.0))
        y = cy + R//3 + int((mr//2)*math.sin(math.radians(a)))
        p.dragTo(x, y, duration=0.01)


def draw_house_right():
    W, H = p.size(); cx, cy = W//2, H//2
    bx = cx + int(W*0.18); by = cy + 60; w, h = 260, 180
    bx = min(W-50, max(50, bx)); by = min(H-50, max(50, by))
    # body
    p.moveTo(bx, by); p.mouseDown(); p.dragTo(bx+w, by, duration=0.25); p.dragTo(bx+w, by+h, duration=0.25); p.dragTo(bx, by+h, duration=0.25); p.dragTo(bx, by, duration=0.25); p.mouseUp()
    # roof
    rx1, ry1 = bx, by; rx2, ry2 = bx+w, by; rtx, rty = bx + w//2, by - int(h*0.6)
    p.moveTo(rx1, ry1); p.mouseDown(); p.dragTo(rtx, rty, duration=0.22); p.dragTo(rx2, ry2, duration=0.22); p.dragTo(rx1, ry1, duration=0.22); p.mouseUp()
    # door
    dx, dy = bx + w//2 - 25, by + h - 80
    p.moveTo(dx, dy); p.mouseDown(); p.dragTo(dx, dy+80, duration=0.18); p.dragTo(dx+50, dy+80, duration=0.18); p.dragTo(dx+50, dy, duration=0.18); p.dragTo(dx, dy, duration=0.18); p.mouseUp()


def main():
    ap = argparse.ArgumentParser(description='Draw with pre/post screenshots')
    ap.add_argument('--what', choices=['smiley','house','both'], default='smiley')
    ap.add_argument('--label', default='draw')
    ap.add_argument('--outdir', default='.')
    ap.add_argument('--focus', action='store_true')
    ap.add_argument('--minimize', action='store_true', help='Minimize Paint when done')
    ap.add_argument('--beep', action='store_true', help='Play a short beep when done')
    ap.add_argument('--speak', default='', help='Speak a custom done message (requires pyttsx3)')
    args = ap.parse_args()

    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    outdir = os.path.abspath(args.outdir)
    os.makedirs(outdir, exist_ok=True)
    before = os.path.join(outdir, f'{args.label}_before_{ts}.png')
    after  = os.path.join(outdir, f'{args.label}_after_{ts}.png')

    if args.focus:
        focus_paint()
        time.sleep(0.2)

    snap(before)

    if args.what in ('smiley','both'):
        draw_smiley()
    if args.what in ('house','both'):
        draw_house_right()

    time.sleep(0.1)
    snap(after)

    if args.minimize:
        minimize_paint()

    if args.speak:
        try:
            import pyttsx3
            e = pyttsx3.init(); e.setProperty('rate', 180); e.say(args.speak); e.runAndWait()
        except Exception:
            pass
    elif args.beep and winsound:
        try:
            winsound.Beep(880, 200)
        except Exception:
            pass

if __name__ == '__main__':
    main()
