import time
import win32gui, win32con

def find_paint():
    target = []
    def enum(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title and 'paint' in title.lower():
                target.append(hwnd)
    win32gui.EnumWindows(enum, None)
    return target[0] if target else None

hwnd = find_paint()
if hwnd:
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        time.sleep(0.1)
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.1)
    except Exception:
        pass
print('focused' if hwnd else 'not-found')
