import time
import pyautogui as p

p.FAILSAFE = True
p.PAUSE = 0.01

try:
    p.hotkey('alt','space'); time.sleep(0.15); p.press('x')
except Exception:
    pass

W, H = p.size()
cx, cy = W//2, H//2

# Base rectangle to the right of the smiley
bx = cx + int(W*0.18)
by = cy + 60
w, h = 260, 180

# Ensure inside canvas
bx = min(W-50, max(50, bx))
by = min(H-50, max(50, by))

# House body
p.moveTo(bx, by)
p.mouseDown()
p.dragTo(bx+w, by, duration=0.25)
p.dragTo(bx+w, by+h, duration=0.25)
p.dragTo(bx, by+h, duration=0.25)
p.dragTo(bx, by, duration=0.25)
p.mouseUp()

# Roof (triangle)
rx1, ry1 = bx, by
rx2, ry2 = bx+w, by
rtx, rty = bx + w//2, by - int(h*0.6)

p.moveTo(rx1, ry1)
p.mouseDown()
p.dragTo(rtx, rty, duration=0.22)
p.dragTo(rx2, ry2, duration=0.22)
p.dragTo(rx1, ry1, duration=0.22)
p.mouseUp()

# Door
dx, dy = bx + w//2 - 25, by + h - 80
p.moveTo(dx, dy)
p.mouseDown()
p.dragTo(dx, dy+80, duration=0.18)
p.dragTo(dx+50, dy+80, duration=0.18)
p.dragTo(dx+50, dy, duration=0.18)
p.dragTo(dx, dy, duration=0.18)
p.mouseUp()

print('draw_house_right done')
