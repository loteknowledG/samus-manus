#!/usr/bin/env python3
"""
Hands — simple GUI automation CLI (move, click, type, screenshot, find-click).
Safe by default: simulates actions when `pyautogui` is not available.

Examples:
  python hands.py move --x 800 --y 450 --dur 0.2
  python hands.py click --x 800 --y 450
  python hands.py type "hello" --interval 0.02
  python hands.py screenshot --out screen.png
  python hands.py find-click --img path/to/img.png --confidence 0.9 --click
"""
from pathlib import Path
import argparse
import time

try:
    import pyautogui
except Exception:
    pyautogui = None


def move(x: int, y: int, dur: float):
    if pyautogui:
        pyautogui.moveTo(int(x), int(y), duration=float(dur or 0))
        return f"moved to ({x},{y})"
    return f"(sim) move to ({x},{y}) duration={dur}"


def click(x: int, y: int, button: str = "left"):
    if pyautogui:
        pyautogui.click(int(x), int(y), button=button)
        return f"clicked at ({x},{y})"
    return f"(sim) click at ({x},{y}) button={button}"


def type_text(text: str, interval: float = 0.02):
    if pyautogui:
        pyautogui.write(text, interval=float(interval or 0.02))
        return f"typed: {text!r}"
    return f"(sim) type: {text!r}"


def screenshot(out: str):
    out_p = Path(out)
    if pyautogui:
        pyautogui.screenshot(str(out_p))
        return str(out_p)
    try:
        from PIL import ImageGrab
        img = ImageGrab.grab()
        img.save(out_p)
        return str(out_p)
    except Exception:
        return f"(sim) screenshot -> {out}"


def find_click(img: str, confidence: float = 0.8, do_click: bool = False, timeout: float = 3.0):
    if not pyautogui:
        return f"(sim) find {img} (pyautogui unavailable)"
    end = time.time() + float(timeout or 3.0)
    while True:
        try:
            if hasattr(pyautogui, 'locateCenterOnScreen'):
                loc = pyautogui.locateCenterOnScreen(img, confidence=confidence)
            else:
                loc = pyautogui.locateCenterOnScreen(img)
            if loc:
                x, y = int(loc.x), int(loc.y)
                if do_click:
                    pyautogui.click(x, y)
                    return f"found and clicked {img} at ({x},{y})"
                return f"found {img} at ({x},{y})"
        except Exception:
            return f"find failed (dependency issue)"
        if time.time() > end:
            return f"not found: {img}"
        time.sleep(0.2)


def main():
    ap = argparse.ArgumentParser(prog='hands', description='Simple GUI automation CLI')
    sub = ap.add_subparsers(dest='cmd', required=True)

    p = sub.add_parser('move')
    p.add_argument('--x', type=int, required=True)
    p.add_argument('--y', type=int, required=True)
    p.add_argument('--dur', type=float, default=0.0)
    p.set_defaults(func=lambda args: print(move(args.x, args.y, args.dur)))

    p = sub.add_parser('click')
    p.add_argument('--x', type=int, required=True)
    p.add_argument('--y', type=int, required=True)
    p.add_argument('--button', choices=['left', 'right', 'middle'], default='left')
    p.set_defaults(func=lambda args: print(click(args.x, args.y, args.button)))

    p = sub.add_parser('type')
    p.add_argument('text', nargs='+')
    p.add_argument('--interval', type=float, default=0.02)
    p.set_defaults(func=lambda args: print(type_text(' '.join(args.text), args.interval)))

    p = sub.add_parser('screenshot')
    p.add_argument('--out', default='screen.png')
    p.set_defaults(func=lambda args: print(screenshot(args.out)))

    p = sub.add_parser('find-click')
    p.add_argument('--img', required=True)
    p.add_argument('--confidence', type=float, default=0.8)
    p.add_argument('--click', dest='do_click', action='store_true')
    p.add_argument('--timeout', type=float, default=3.0)
    p.set_defaults(func=lambda args: print(find_click(args.img, args.confidence, args.do_click, args.timeout)))

    args = ap.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
