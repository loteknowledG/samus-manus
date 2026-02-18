#!/usr/bin/env python3
"""Open a URL in the default browser and position the browser window on the left side of the screen.

Usage: python tools/open_browser_left.py [url]
"""
import sys
import time
import webbrowser

try:
    import pygetwindow as gw
    import pyautogui
except Exception as e:
    print('Missing dependency:', e)
    raise

URL = sys.argv[1] if len(sys.argv) > 1 else 'https://developer.chrome.com/'

# open URL in default browser
webbrowser.open(URL, new=1)
# give the browser a moment to open
time.sleep(2.0)

# try to find a window that looks like Chrome / the opened page
candidates = []
for w in gw.getAllWindows():
    title = (w.title or '').lower()
    if not title:
        continue
    if 'chrome' in title or 'google chrome' in title or 'developer' in title or 'chrome for developers' in title or 'no one agent' in title:
        candidates.append(w)

# fallback: any non-empty-window title
if not candidates:
    for w in gw.getAllWindows():
        if w.title:
            candidates.append(w)

if not candidates:
    print('No window found to move. Browser likely opened but window title not detected.')
    sys.exit(1)

# pick the best candidate (first match)
win = candidates[0]
# move & resize to left half (or left third for tall displays)
screen_w, screen_h = pyautogui.size()
# prefer left third if screen width is large
width = screen_w // 2 if screen_w < 3000 else screen_w // 3
try:
    win.moveTo(0, 0)
    win.resizeTo(width, screen_h)
    win.activate()
    print('Moved window to left:', win.title)
except Exception as e:
    print('Failed to reposition window:', e)
    sys.exit(1)
