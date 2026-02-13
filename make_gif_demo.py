import os, time, threading, subprocess
import mss
from PIL import Image
import numpy as np
import imageio.v2 as imageio
import pyautogui as p

OUT = r"C:\dev\samus-manus\agency_demo.gif"
FPS = 8
DURATION = 8  # seconds
WIDTH = 1280   # downscale width to keep gif small

stop = threading.Event()


def record_screen(path: str, fps: int, duration: int, target_w: int):
    interval = 1.0 / fps
    end = time.time() + duration
    with mss.mss() as sct:
        mon = sct.monitors[1]
        with imageio.get_writer(path, mode='I', duration=interval, loop=0) as writer:
            i = 0
            while time.time() < end and not stop.is_set():
                start = time.time()
                raw = sct.grab(mon)
                img = Image.frombytes('RGB', raw.size, raw.rgb)
                if img.width > target_w:
                    h = int(img.height * (target_w / img.width))
                    img = img.resize((target_w, h), Image.LANCZOS)
                writer.append_data(np.asarray(img))
                i += 1
                sleep_for = interval - (time.time() - start)
                if sleep_for > 0:
                    time.sleep(sleep_for)


def run_demo_actions():
    # Open Paint and maximize
    try:
        subprocess.Popen(["mspaint"])  # non-blocking
    except Exception:
        os.system("start mspaint")
    time.sleep(1.5)
    p.hotkey('alt','space'); time.sleep(0.2); p.press('x')
    # Draw a quick rectangle
    w, h = p.size()
    x1, y1 = int(w*0.35), int(h*0.45)
    x2, y2 = int(w*0.65), int(h*0.75)
    p.moveTo(x1, y1)
    p.mouseDown()
    p.dragTo(x2, y1, duration=0.25)
    p.dragTo(x2, y2, duration=0.25)
    p.dragTo(x1, y2, duration=0.25)
    p.dragTo(x1, y1, duration=0.25)
    p.mouseUp()


if __name__ == '__main__':
    rec = threading.Thread(target=record_screen, args=(OUT, FPS, DURATION, WIDTH), daemon=True)
    rec.start()
    try:
        run_demo_actions()
        # Let the recorder finish recording window
        time.sleep(max(0, DURATION - 6))
    finally:
        stop.set()
        # Wait until the recorder thread fully closes the GIF
        rec.join()
    print(OUT)
