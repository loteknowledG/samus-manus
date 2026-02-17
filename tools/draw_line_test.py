import time
import pyautogui as p

p.FAILSAFE = True
p.PAUSE = 0.02

# Maximize window (Paint)
try:
    p.hotkey('alt','space'); time.sleep(0.2); p.press('x'); time.sleep(0.2)
except Exception:
    pass

W, H = p.size()
cx, cy = W//2, H//2

# Click canvas center a couple times to ensure focus
for _ in range(2):
    p.click(cx, cy); time.sleep(0.05)

# Big rectangle by drags (more reliable than moveTo)
margin = int(min(W, H) * 0.15)
x1, y1 = margin, int(H*0.25)
x2, y2 = W - margin, int(H*0.75)

p.moveTo(x1, y1); p.mouseDown(); p.dragTo(x2, y1, duration=0.35); p.dragTo(x2, y2, duration=0.35); p.dragTo(x1, y2, duration=0.35); p.dragTo(x1, y1, duration=0.35); p.mouseUp()

# Plus sign in the middle
p.moveTo(cx - 120, cy); p.mouseDown(); p.dragTo(cx + 120, cy, duration=0.35); p.mouseUp()
p.moveTo(cx, cy - 120); p.mouseDown(); p.dragTo(cx, cy + 120, duration=0.35); p.mouseUp()

print('draw_line_test complete')
