import time, math, subprocess, os
import pyautogui as p

# Open/bring up Paint
try:
    subprocess.Popen(["mspaint"])  # non-blocking if not already open
except Exception:
    os.system("start mspaint")

time.sleep(1.4)
try:
    p.hotkey('alt','space'); time.sleep(0.2); p.press('x')
except Exception:
    pass

p.PAUSE = 0.02
p.FAILSAFE = True

W, H = p.size()
# Canvas center a bit lower than exact middle
cx, cy = W//2, int(H*0.60)

# Basic helpers

def line(x1, y1, x2, y2, d=0.12):
    p.moveTo(int(x1), int(y1))
    p.dragTo(int(x2), int(y2), duration=d)


def rect(x, y, w, h, d=0.15):
    p.moveTo(int(x), int(y))
    p.mouseDown()
    p.dragTo(int(x+w), int(y), duration=d)
    p.dragTo(int(x+w), int(y+h), duration=d)
    p.dragTo(int(x), int(y+h), duration=d)
    p.dragTo(int(x), int(y), duration=d)
    p.mouseUp()

# Dimensions (relative to screen)
palm_w, palm_h = int(W*0.12), int(H*0.14)
finger_len = int(H*0.12)
finger_gap = palm_w // 5

# Palm rect centered
px = cx - palm_w//2
py = cy - palm_h//2
rect(px, py, palm_w, palm_h)

# Four fingers (index..pinky) rising from top of palm
base_y = py
for i in range(4):
    fx = px + int((i+0.5)*finger_gap)
    line(fx, base_y, fx, base_y - finger_len)

# Thumb on left as an angled line
thumb_base_x = px + int(0.15*palm_w)
thumb_base_y = py + int(0.25*palm_h)
thumb_tip_x  = px - int(0.25*palm_w)
thumb_tip_y  = py + int(0.05*palm_h)
line(thumb_base_x, thumb_base_y, thumb_tip_x, thumb_tip_y)

# Wrist below palm
wrist_w = int(palm_w*0.55)
wrist_h = int(palm_h*0.25)
wx = cx - wrist_w//2
wy = py + palm_h
rect(wx, wy, wrist_w, wrist_h)

# Select Text tool and add label
try:
    text_x = int(W*0.30)
    text_y = int(H*0.13)
    p.click(text_x, text_y)
except Exception:
    pass

label_x = cx
label_y = int(H*0.83)
p.click(label_x, label_y)
msg = "IRON HAND — hi • halt • empty hands • shield"
p.write(msg, interval=0.02)

# Screenshot proof
out = r"C:\dev\samus-manus\iron_hand.png"
p.screenshot(out)
print(out)
