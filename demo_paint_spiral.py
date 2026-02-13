import time, math, subprocess, os
import pyautogui as p

# Open Paint
try:
    subprocess.Popen(["mspaint"])  # Windows Paint
except Exception:
    os.system("start mspaint")

# Give it a moment to appear
time.sleep(1.5)

# Try to bring window forward / maximize
try:
    import pygetwindow as gw
    wins = gw.getWindowsWithTitle('Paint') or gw.getWindowsWithTitle('MSPaint')
    if wins:
        w = wins[0]
        try:
            w.activate()
        except Exception:
            pass
        try:
            w.maximize()
        except Exception:
            pass
except Exception:
    pass

# Fallback maximize via hotkey
p.hotkey('alt','space'); time.sleep(0.2); p.press('x')

# Draw a spiral in the middle of the screen
W,H = p.size()
cx, cy = W//2, int(H*0.58)

p.moveTo(cx, cy)
p.mouseDown()
for deg in range(0, 900, 3):
    r = 2 + deg * 0.35
    x = int(cx + r * math.cos(math.radians(deg)))
    y = int(cy + r * math.sin(math.radians(deg)))
    p.dragTo(x, y, duration=0.005)
p.mouseUp()

# Screenshot proof
out = os.path.join(r"C:\dev\samus-manus", "paint_demo.png")
p.screenshot(out)
print(out)
