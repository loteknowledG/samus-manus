#!/usr/bin/env python3
"""Generate a straw-colored smiley image and open it in MS Paint.

Usage: python draw_smiley.py
"""
from pathlib import Path
from PIL import Image, ImageDraw
import subprocess

OUT = Path(__file__).parent / "samus_smiley.png"
SIZE = 700
CENTER = (SIZE // 2, SIZE // 2)
R = int(SIZE * 0.35)

# colors
STRAW = (249, 231, 159)  # light straw/yellow
BORDER = (50, 40, 30)    # dark brown/black for outline/features
WHITE = (255, 255, 255)

img = Image.new("RGB", (SIZE, SIZE), WHITE)
d = ImageDraw.Draw(img)

# face circle (fill + border)
d.ellipse([ (CENTER[0]-R, CENTER[1]-R), (CENTER[0]+R, CENTER[1]+R) ], fill=STRAW, outline=BORDER, width=8)

# eyes
eye_r = int(R * 0.12)
eye_x_off = int(R * 0.45)
eye_y_off = int(R * -0.15)
d.ellipse([ (CENTER[0]-eye_x_off-eye_r, CENTER[1]+eye_y_off-eye_r), (CENTER[0]-eye_x_off+eye_r, CENTER[1]+eye_y_off+eye_r) ], fill=BORDER)
d.ellipse([ (CENTER[0]+eye_x_off-eye_r, CENTER[1]+eye_y_off-eye_r), (CENTER[0]+eye_x_off+eye_r, CENTER[1]+eye_y_off+eye_r) ], fill=BORDER)

# mouth (arc)
mouth_box = [ (CENTER[0]-int(R*0.6), CENTER[1]-int(R*0.05)), (CENTER[0]+int(R*0.6), CENTER[1]+int(R*0.65)) ]
# draw a thick arc by drawing multiple offsets
for w in range(6):
    d.arc(mouth_box, start=20, end=160, fill=BORDER, width=4)

# optional blush / straw highlights (small ovals)
hl_r = int(R*0.08)
d.ellipse([ (CENTER[0]-int(R*0.2)-hl_r, CENTER[1]+int(R*0.05)-hl_r), (CENTER[0]-int(R*0.2)+hl_r, CENTER[1]+int(R*0.05)+hl_r) ], fill=(255,220,150))

img.save(OUT)
print(f"Saved smiley to {OUT}")

# open in MS Paint (Windows)
try:
    subprocess.Popen(["mspaint", str(OUT)])
    print("Opened in Paint")
except Exception as e:
    print("Couldn't open Paint:", e)
    print("File is available at", OUT)
