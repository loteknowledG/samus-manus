import time, math
import pyautogui as p

p.FAILSAFE = True
p.PAUSE = 0.01

# Maximize current window (Paint)
try:
    p.hotkey('alt','space'); time.sleep(0.15); p.press('x')
except Exception:
    pass

W, H = p.size()
cx, cy = W//2, H//2

# Ensure canvas focus
for _ in range(2):
    p.click(cx, cy); time.sleep(0.05)

# Eyes (drag small circles)
R = max(80, min(W, H)//6)
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

# Try to pick yellow + bucket fill (heuristic positions)
try:
    # Select yellow swatch (top palette area)
    y_palette = int(H*0.145)
    x_yellow  = int(W*0.63)
    p.moveTo(x_yellow, y_palette); p.click()
    time.sleep(0.05)
    # Select bucket (Tools group)
    x_bucket, y_bucket = int(W*0.234), int(H*0.145)
    p.moveTo(x_bucket, y_bucket); p.click()
    time.sleep(0.05)
    # Fill inside face
    p.moveTo(cx, cy); p.click()
except Exception:
    pass

print('complete_smiley_and_fill done')
