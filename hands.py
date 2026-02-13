#!/usr/bin/env python
"""
Hands: tiny CLI to control mouse/keyboard and screenshots via pyautogui.

Examples
  python hands.py move --x 800 --y 450 --dur 0.2
  python hands.py click --x 200 --y 300 --button left
  python hands.py type "hello world" --interval 0.03
  python hands.py paste "🚀 hello"
  python hands.py press enter
  python hands.py hotkey ctrl s
  python hands.py scroll --amount -800
  python hands.py screenshot --out screen.png
  python hands.py find-click --img C:\path\ok.png --conf 0.9 --timeout 5 --click
"""
import argparse
import sys
import time

try:
    import pyautogui as p
except Exception as e:
    print("pyautogui is required. Install with: pip install pyautogui pillow", file=sys.stderr)
    raise

# Optional deps
try:
    import pyperclip
except Exception:
    pyperclip = None
try:
    import cv2  # noqa: F401  (only needed for confidence matching)
except Exception:
    cv2 = None

p.FAILSAFE = True  # Move cursor to a screen corner to abort
p.PAUSE = 0.10     # Small delay between actions for stability


def cmd_move(args):
    p.moveTo(args.x, args.y, duration=args.dur or 0)


def cmd_click(args):
    p.click(args.x, args.y, clicks=args.clicks, interval=args.interval, button=args.button)


def cmd_double_click(args):
    p.doubleClick(args.x, args.y)


def cmd_type(args):
    p.write(args.text, interval=args.interval)


def cmd_paste(args):
    if not pyperclip:
        sys.exit("pyperclip not installed (pip install pyperclip)")
    pyperclip.copy(args.text)
    time.sleep(0.05)
    p.hotkey('ctrl', 'v')


def cmd_press(args):
    p.press(args.key)


def cmd_hotkey(args):
    p.hotkey(*args.keys)


def cmd_scroll(args):
    p.scroll(args.amount)


def cmd_drag(args):
    # Drag from (x1,y1) to (x2,y2)
    p.moveTo(args.x1, args.y1)
    p.dragTo(args.x2, args.y2, duration=args.dur or 0.0, button=args.button)


def cmd_screenshot(args):
    p.screenshot(args.out)
    print(args.out)


def cmd_find_click(args):
    kw = {}
    if args.confidence is not None:
        if not cv2:
            sys.exit("opencv-python required for confidence matching (pip install opencv-python)")
        kw["confidence"] = args.confidence
    deadline = time.time() + args.timeout
    while time.time() < deadline:
        pt = p.locateCenterOnScreen(args.img, **kw)
        if pt:
            p.moveTo(pt)
            if args.click:
                p.click()
            print(f"found at {pt}")
            return
        time.sleep(0.2)
    sys.exit("not found")


def main():
    ap = argparse.ArgumentParser(prog="hands", description="Control mouse/keyboard/screenshots via pyautogui")
    sub = ap.add_subparsers(dest="cmd", required=True)

    mv = sub.add_parser("move", help="Move mouse to x,y")
    mv.add_argument("--x", type=int, required=True)
    mv.add_argument("--y", type=int, required=True)
    mv.add_argument("--dur", type=float, default=0.0)
    mv.set_defaults(func=cmd_move)

    ck = sub.add_parser("click", help="Click at x,y")
    ck.add_argument("--x", type=int, required=True)
    ck.add_argument("--y", type=int, required=True)
    ck.add_argument("--button", choices=["left", "right", "middle"], default="left")
    ck.add_argument("--clicks", type=int, default=1)
    ck.add_argument("--interval", type=float, default=0.05)
    ck.set_defaults(func=cmd_click)

    dc = sub.add_parser("double-click", help="Double click at x,y")
    dc.add_argument("--x", type=int, required=True)
    dc.add_argument("--y", type=int, required=True)
    dc.set_defaults(func=cmd_double_click)

    tp = sub.add_parser("type", help="Type ASCII text")
    tp.add_argument("text")
    tp.add_argument("--interval", type=float, default=0.03)
    tp.set_defaults(func=cmd_type)

    pst = sub.add_parser("paste", help="Paste arbitrary text via clipboard")
    pst.add_argument("text")
    pst.set_defaults(func=cmd_paste)

    pr = sub.add_parser("press", help="Press a single key")
    pr.add_argument("key")
    pr.set_defaults(func=cmd_press)

    hk = sub.add_parser("hotkey", help="Press a key combo in order")
    hk.add_argument("keys", nargs="+")
    hk.set_defaults(func=cmd_hotkey)

    sc = sub.add_parser("scroll", help="Scroll by amount (neg=down, pos=up)")
    sc.add_argument("--amount", type=int, required=True)
    sc.set_defaults(func=cmd_scroll)

    dg = sub.add_parser("drag", help="Drag from (x1,y1) to (x2,y2)")
    dg.add_argument("--x1", type=int, required=True)
    dg.add_argument("--y1", type=int, required=True)
    dg.add_argument("--x2", type=int, required=True)
    dg.add_argument("--y2", type=int, required=True)
    dg.add_argument("--dur", type=float, default=0.3)
    dg.add_argument("--button", choices=["left", "right", "middle"], default="left")
    dg.set_defaults(func=cmd_drag)

    ss = sub.add_parser("screenshot", help="Save a screenshot to path")
    ss.add_argument("--out", required=True)
    ss.set_defaults(func=cmd_screenshot)

    fc = sub.add_parser("find-click", help="Find image on screen and optionally click it")
    fc.add_argument("--img", required=True)
    fc.add_argument("--confidence", type=float)
    fc.add_argument("--timeout", type=float, default=3.0)
    fc.add_argument("--click", action="store_true")
    fc.set_defaults(func=cmd_find_click)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
