import time, math
import pyautogui as p

p.FAILSAFE = True
p.PAUSE = 0.02

# Maximize current window (Paint) just in case
try:
    p.hotkey('alt','space'); time.sleep(0.2); p.press('x'); time.sleep(0.2)
except Exception:
    pass

# Use center of screen as canvas center
W, H = p.size()
cx, cy = W//2, H//2

# Ensure canvas focus
p.click(cx, cy)

# Head circle
R = min(W, H)//6
p.moveTo(cx + R, cy)
p.mouseDown()
for a in range(0, 361, 6):
    x = cx + int(R*math.cos(math.radians(a)))
    y = cy + int(R*math.sin(math.radians(a)))
    p.moveTo(x, y)
p.mouseUp()

# Eyes
er = max(8, R//10)
for ox in (-R//2, R//2):
    p.moveTo(cx + ox + er, cy - R//3)
    p.mouseDown()
    for a in range(0, 361, 12):
        x = cx + ox + int(er*math.cos(math.radians(a)))
        y = cy - R//3 + int(er*math.sin(math.radians(a)))
        p.moveTo(x, y)
    p.mouseUp()

# Smile (arc)
mr = R//2
p.moveTo(cx - mr, cy + R//3)
p.mouseDown()
for a in range(0, 181, 6):
    x = cx - mr + int(2*mr*(a/180.0))
    y = cy + R//3 + int((mr//2)*math.sin(math.radians(a)))
    p.moveTo(x, y)
p.mouseUp()
