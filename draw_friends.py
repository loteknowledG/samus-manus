import time, math, subprocess, os
import pyautogui as p

# Ensure Paint is open and maximized
try:
    subprocess.Popen(["mspaint"])  # non-blocking if not open
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
cy = int(H*0.60)
left_x = int(W*0.40)
right_x = int(W*0.60)


def circle(cx, cy, r):
    p.moveTo(cx + r, cy)
    p.mouseDown()
    for a in range(0, 361, 8):
        x = int(cx + r*math.cos(math.radians(a)))
        y = int(cy + r*math.sin(math.radians(a)))
        p.dragTo(x, y, duration=0.01)
    p.mouseUp()


def square(cx, cy, s):
    p.moveTo(cx - s, cy - s)
    p.mouseDown()
    p.dragTo(cx + s, cy - s, duration=0.15)
    p.dragTo(cx + s, cy + s, duration=0.15)
    p.dragTo(cx - s, cy + s, duration=0.15)
    p.dragTo(cx - s, cy - s, duration=0.15)
    p.mouseUp()


def line(x1, y1, x2, y2, d=0.15):
    p.moveTo(x1, y1)
    p.dragTo(x2, y2, duration=d)

# Human (left): circle head, stick body
head_y = cy - 120
circle(left_x, head_y, 28)
line(left_x, head_y+30, left_x, cy+20)
line(left_x, cy-10, left_x-45, cy+25)  # left arm
# Handshake target in the middle
hx = int((left_x + right_x)/2)
hy = cy+10
line(left_x, cy-10, hx, hy)  # right arm to handshake
line(left_x, cy+20, left_x-35, cy+80)  # left leg
line(left_x, cy+20, left_x+35, cy+80)  # right leg

# Robot (right): square head, stick body with box torso feel
square(right_x, head_y, 26)
line(right_x, head_y+26, right_x, cy+20)
line(right_x, cy-10, hx, hy)  # left arm to handshake
line(right_x, cy-10, right_x+50, cy+25)  # right arm
line(right_x, cy+20, right_x-35, cy+80)
line(right_x, cy+20, right_x+35, cy+80)

# Small heart between hands
heart_cx, heart_cy = hx, hy-25
r = 14
# left lobe
p.moveTo(heart_cx, heart_cy)
p.mouseDown()
for a in range(140, 320, 10):
    x = int(heart_cx - r + r*math.cos(math.radians(a)))
    y = int(heart_cy + r*math.sin(math.radians(a)))
    p.dragTo(x, y, duration=0.01)
p.mouseUp()
# right lobe
p.moveTo(heart_cx, heart_cy)
p.mouseDown()
for a in range(40, 220, 10):
    x = int(heart_cx + r - r*math.cos(math.radians(a)))
    y = int(heart_cy + r*math.sin(math.radians(a)))
    p.dragTo(x, y, duration=0.01)
p.mouseUp()

# Save a quick screenshot proof
out = r"C:\dev\samus-manus\friends_paint.png"
p.screenshot(out)
print(out)
