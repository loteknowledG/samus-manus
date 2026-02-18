#!/usr/bin/env python3
"""Locate the orange "Send Verification Email" button on screen and click it.
Saves a before/after screenshot and reports simple red/orange-region checks.
"""
from PIL import Image
import pygetwindow as gw
import pyautogui
import numpy as np
import time

OUT_BEFORE = 'molt_verify_before.png'
OUT_AFTER = 'molt_verify_after.png'

# focus Chrome window if present
for w in gw.getAllWindows():
    if w.title and ('chrome' in w.title.lower() or 'developer' in w.title.lower() or 'moltbook' in w.title.lower()):
        try:
            w.activate()
            break
        except Exception:
            pass

# take before screenshot
img = pyautogui.screenshot()
img.save(OUT_BEFORE)
arr = np.array(img)

h, w, _ = arr.shape
# detect orange-ish regions (button color)
mask_orange = (arr[:,:,0] > 180) & (arr[:,:,1] > 70) & (arr[:,:,2] < 140)
ys, xs = np.where(mask_orange)
if len(xs) == 0:
    print('No orange region found on screen (cannot locate button). Saved', OUT_BEFORE)
else:
    x0, x1 = xs.min(), xs.max()
    y0, y1 = ys.min(), ys.max()
    cx = int((x0 + x1) / 2)
    cy = int((y0 + y1) / 2)
    print('Orange bbox:', x0, y0, x1, y1, '-> clicking', cx, cy)
    pyautogui.click(cx, cy)
    time.sleep(2.0)

# save after screenshot
img2 = pyautogui.screenshot()
img2.save(OUT_AFTER)
arr2 = np.array(img2)

# simple red-error detection (red box like in screenshot)
mask_red = (arr2[:,:,0] > 150) & (arr2[:,:,1] < 90) & (arr2[:,:,2] < 90)
red_count = mask_red.sum()
print('After click: red-pixel count =', int(red_count))
print('Saved after screenshot to', OUT_AFTER)

# heuristic: if red_count decreased compared to before, verification might have progressed
mask_red_before = (arr[:,:,0] > 150) & (arr[:,:,1] < 90) & (arr[:,:,2] < 90)
red_before = mask_red_before.sum()
print('Before click: red-pixel count =', int(red_before))
if red_count < red_before:
    print('Error-message area appears smaller after click (good).')
elif red_count == red_before:
    print('No visible change in red/error area after click.')
else:
    print('Red/error area increased after clicking (still failing).')
