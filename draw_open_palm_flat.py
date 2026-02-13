import time, subprocess, os
import pyautogui as p

# Bring Paint forward (or start it)
try:
    subprocess.Popen(["mspaint"])  # non-blocking if not already open
except Exception:
    os.system("start mspaint")

time.sleep(1.3)
try:
    p.hotkey('alt','space'); time.sleep(0.2); p.press('x')
except Exception:
    pass

p.FAILSAFE = True
p.PAUSE = 0.02

W, H = p.size()
# Compose at center-lower area
cx, cy = W//2, int(H*0.60)

# Helpers

def line(x1, y1, x2, y2, d=0.10):
    p.moveTo(int(x1), int(y1))
    p.dragTo(int(x2), int(y2), duration=d)


def rect(x, y, w, h, d=0.12):
    p.moveTo(int(x), int(y))
    p.mouseDown()
    p.dragTo(int(x+w), int(y), duration=d)
    p.dragTo(int(x+w), int(y+h), duration=d)
    p.dragTo(int(x), int(y+h), duration=d)
    p.dragTo(int(x), int(y), duration=d)
    p.mouseUp()

# Dimensions (relative to screen)
palm_w, palm_h = int(W*0.14), int(H*0.14)
finger_h = int(H*0.11)

# Palm rectangle
px = cx - palm_w//2
py = cy - palm_h//2
rect(px, py, palm_w, palm_h)

# Fingers together: one block just above palm (slightly narrower)
fx = px + int(0.06*palm_w)
fw = palm_w - int(0.12*palm_w)
fy = py - finger_h
rect(fx, fy, fw, finger_h)

# Thumb: flat/open, angled to the side
thumb_base_x = px + int(0.10*palm_w)
thumb_base_y = py + int(0.15*palm_h)
thumb_tip_x  = px - int(0.28*palm_w)
thumb_tip_y  = py - int(0.10*palm_h)
line(thumb_base_x, thumb_base_y, thumb_tip_x, thumb_tip_y)

# Wrist/cuff
wrist_w = int(palm_w*0.55)
wrist_h = int(palm_h*0.22)
wx = cx - wrist_w//2
wy = py + palm_h
rect(wx, wy, wrist_w, wrist_h)

# Label
try:
    # Text tool approx location
    p.click(int(W*0.30), int(H*0.13))
except Exception:
    pass
p.click(cx, int(H*0.82))
p.write("IRON HAND — hi • halt • empty hands • shield", interval=0.02)

# Screenshot proof
out = r"C:\dev\samus-manus\iron_hand_flat.png"
p.screenshot(out)
print(out)
