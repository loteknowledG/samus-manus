import time, math
import pyautogui as p

p.FAILSAFE = True
p.PAUSE = 0.01

# Assume Paint is focused. Maximize for consistent coords
try:
    p.hotkey('alt','space'); time.sleep(0.15); p.press('x')
except Exception:
    pass

W, H = p.size()
cx, cy = W//2, H//2

# Thicken outline by tracing two offset rings
R = max(80, min(W, H)//6)
for off in (2, 4):
    p.moveTo(cx + R + off, cy)
    for a in range(0, 361, 4):
        x = cx + int((R+off)*math.cos(math.radians(a)))
        y = cy + int((R+off)*math.sin(math.radians(a)))
        p.dragTo(x, y, duration=0.005)

# Attempt color pick (yellow) and bucket fill using approximate UI positions.
# These coordinates are heuristic and may vary; safe to ignore if they miss.
try:
    # Pick a yellow swatch from the Colors palette (roughly top-right area)
    y_palette = int(H*0.145)
    x_yellow  = int(W*0.63)
    p.moveTo(x_yellow, y_palette); p.click()
    time.sleep(0.05)
    # Select Fill tool (bucket) roughly under Tools section left-top
    x_bucket, y_bucket = int(W*0.235), int(H*0.145)
    p.moveTo(x_bucket, y_bucket); p.click()
    time.sleep(0.05)
    # Click inside the face to fill
    p.moveTo(cx, cy); p.click()
except Exception:
    pass

print('enhance_smiley done')
