import time, math
import pyautogui as p

p.FAILSAFE = True
p.PAUSE = 0.02

# Ensure Paint is front and maximized
try:
    p.hotkey('alt','space'); time.sleep(0.2); p.press('x')
except Exception:
    pass

W, H = p.size()

# 1) Pick a bright color (tap a few palette spots near the Colors bar)
y_top = int(H*0.13)
for frac in (0.73, 0.76, 0.79):
    x = int(W*frac)
    p.click(x, y_top)
    time.sleep(0.05)

# 2) Draw/overdraw a heart in the middle using the selected color
cx = int(W*0.50)
cy = int(H*0.60)
r = int(min(W, H) * 0.025)

p.moveTo(cx + r, cy)
p.mouseDown()
for a in range(0, 361, 6):
    x = int(cx + r*math.cos(math.radians(a)))
    y = int(cy + r*math.sin(math.radians(a)))
    p.dragTo(x, y, duration=0.01)
p.mouseUp()

# 3) Select the Text tool (approx position of the 'A' icon in the Tools group)
text_x = int(W*0.30)
text_y = int(H*0.13)
p.click(text_x, text_y)

# 4) Click on canvas bottom center and type label
label_x = int(W*0.50)
label_y = int(H*0.78)
p.click(label_x, label_y)
msg = "Man + Machine = Friends"
p.write(msg, interval=0.03)

# 5) Screenshot proof
out = r"C:\dev\samus-manus\friends_colored.png"
p.screenshot(out)
print(out)
