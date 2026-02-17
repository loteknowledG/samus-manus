import time, math
import pyautogui as p

p.FAILSAFE = True
p.PAUSE = 0.01

# Maximize current window (Paint) just in case
try:
    p.hotkey('alt','space'); time.sleep(0.2); p.press('x'); time.sleep(0.2)
except Exception:
    pass

# Use center of screen as canvas center
W, H = p.size()
cx, cy = W//2, H//2

# Ensure canvas focus
for _ in range(2):
    p.click(cx, cy); time.sleep(0.05)

R = max(80, min(W, H)//6)
step = 4

# Head (drag small segments)
p.moveTo(cx + R, cy)
for a in range(0, 361, step):
    x = cx + int(R*math.cos(math.radians(a)))
    y = cy + int(R*math.sin(math.radians(a)))
    p.dragTo(x, y, duration=0.01)

# Eyes
er = max(10, R//8)
for ox in (-R//2, R//2):
    p.moveTo(cx + ox + er, cy - R//3)
    for a in range(0, 361, 12):
        x = cx + ox + int(er*math.cos(math.radians(a)))
        y = cy - R//3 + int(er*math.sin(math.radians(a)))
        p.dragTo(x, y, duration=0.008)

# Smile (arc)
mr = R//2
p.moveTo(cx - mr, cy + R//3)
for a in range(0, 181, 6):
    x = cx - mr + int(2*mr*(a/180.0))
    y = cy + R//3 + int((mr//2)*math.sin(math.radians(a)))
    p.dragTo(x, y, duration=0.01)

print('draw_smiley_drag complete')
