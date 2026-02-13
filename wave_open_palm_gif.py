import os, time, threading, subprocess
import mss
from PIL import Image
import numpy as np
import imageio.v2 as imageio
import pyautogui as p

OUT = r"C:\dev\samus-manus\wave_hand.gif"
FPS = 10
DURATION = 5
WIDTH = 1280

stop = threading.Event()

def record_screen(path: str, fps: int, duration: int, target_w: int):
    interval = 1.0 / fps
    end = time.time() + duration
    with mss.mss() as sct:
        mon = sct.monitors[1]
        with imageio.get_writer(path, mode='I', duration=interval, loop=0) as writer:
            while time.time() < end and not stop.is_set():
                t0 = time.time()
                raw = sct.grab(mon)
                img = Image.frombytes('RGB', raw.size, raw.rgb)
                if img.width > target_w:
                    h = int(img.height * (target_w / img.width))
                    img = img.resize((target_w, h), Image.LANCZOS)
                writer.append_data(np.asarray(img))
                dt = interval - (time.time() - t0)
                if dt > 0:
                    time.sleep(dt)

def bring_paint():
    try:
        subprocess.Popen(["mspaint"])  # if not open, start it
    except Exception:
        os.system("start mspaint")
    time.sleep(1.4)
    try:
        p.hotkey('alt','space'); time.sleep(0.2); p.press('x')
    except Exception:
        pass

def wave_motion():
    W, H = p.size()
    cx, cy = W//2, int(H*0.60)
    # Select tool (approx toolbar position)
    p.click(int(W*0.05), int(H*0.13))
    # Drag a selection around the hand region (center-lower area)
    sel_w, sel_h = int(W*0.18), int(H*0.22)
    x1, y1 = cx - sel_w//2, cy - sel_h//2
    x2, y2 = cx + sel_w//2, cy + sel_h//2
    p.moveTo(x1, y1); p.dragTo(x2, y2, duration=0.25)
    # Cut/paste to make it movable, then nudge left/right to wave
    p.hotkey('ctrl','x'); time.sleep(0.05); p.hotkey('ctrl','v'); time.sleep(0.1)
    for _ in range(2):
        for _ in range(18):
            p.press('right'); time.sleep(0.03)
        for _ in range(18):
            p.press('left'); time.sleep(0.03)

if __name__ == '__main__':
    bring_paint()
    rec = threading.Thread(target=record_screen, args=(OUT, FPS, DURATION, WIDTH), daemon=True)
    rec.start()
    try:
        wave_motion()
        time.sleep(max(0, DURATION - 3))
    finally:
        stop.set(); rec.join()
    print(OUT)
