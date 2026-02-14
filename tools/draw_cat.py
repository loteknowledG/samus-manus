import time, math, subprocess, os, sys
import pyautogui as p

p.FAILSAFE = True
p.PAUSE = 0.03

# Ensure Paint is open and focused (follow `soul.md` defaults)
try:
    subprocess.Popen(['mspaint'])
except Exception:
    os.system('start mspaint')
# give Paint time to appear and stabilize
time.sleep(1.1)
try:
    p.hotkey('alt','space')
    time.sleep(0.25)
    p.press('x')
    time.sleep(0.3)
except Exception:
    pass

# BEFORE screenshot (saved to repo root)
ts_before = time.strftime("%Y%m%d_%H%M%S")
before_path = f"cat_before_{ts_before}.png"
p.screenshot(before_path)
print('Saved before:', before_path)

# Compute canvas center (use screen center)
w, h = p.size()
cx, cy = w//2, h//2

# Click once to ensure canvas focus
p.click(cx, cy)

# Head (circle)
radius = 120
p.moveTo(cx + radius, cy)
p.mouseDown()
for i in range(1, 361, 6):
    ang = math.radians(i)
    x = cx + int(radius * math.cos(ang))
    y = cy + int(radius * math.sin(ang))
    p.moveTo(x, y)
p.mouseUp()

# Ears (triangles)
# Left
p.moveTo(cx-90, cy-90); p.mouseDown()
p.moveTo(cx-120, cy-180)
p.moveTo(cx-50,  cy-120)
p.moveTo(cx-90,  cy-90);  p.mouseUp()
# Right
p.moveTo(cx+90, cy-90); p.mouseDown()
p.moveTo(cx+120, cy-180)
p.moveTo(cx+50,  cy-120)
p.moveTo(cx+90,  cy-90);  p.mouseUp()

# Eyes (small circles)
for ox in (-50, 50):
    r = 14
    p.moveTo(cx+ox+r, cy-30)
    p.mouseDown()
    for i in range(1, 361, 20):
        ang = math.radians(i)
        x = cx + ox + int(r * math.cos(ang))
        y = cy - 30   + int(r * math.sin(ang))
        p.moveTo(x, y)
    p.mouseUp()

# Nose (triangle)
p.moveTo(cx, cy+10); p.mouseDown()
p.moveTo(cx-12, cy+30)
p.moveTo(cx+12, cy+30)
p.moveTo(cx,   cy+10); p.mouseUp()

# Mouth
p.moveTo(cx, cy+30); p.mouseDown(); p.moveTo(cx-30, cy+55); p.mouseUp()
p.moveTo(cx, cy+30); p.mouseDown(); p.moveTo(cx+30, cy+55); p.mouseUp()

# Whiskers
for dy, dx in ((20,95),(30,95),(40,95)):
    # left
    p.moveTo(cx-40, cy+dy); p.mouseDown(); p.moveTo(cx-40-dx, cy+dy-15 if dy==20 else cy+dy); p.mouseUp()
    # right
    p.moveTo(cx+40, cy+dy); p.mouseDown(); p.moveTo(cx+40+dx, cy+dy-15 if dy==20 else cy+dy); p.mouseUp()

# AFTER screenshot (saved to repo root)
ts_after = time.strftime("%Y%m%d_%H%M%S")
after_path = f"cat_after_{ts_after}.png"
p.screenshot(after_path)
print('Saved after:', after_path)

# TTS announcement (non-fatal)
try:
    tts_script = os.path.join(os.path.dirname(__file__), 'tts_say.py')
    subprocess.Popen([sys.executable, tts_script, 'Cat', 'drawn', '--ensure'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
except Exception:
    pass

print('Cat drawn')
