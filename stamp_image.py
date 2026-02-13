from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os

IN = r"C:\dev\samus-manus\friends_colored.png"
OUT = r"C:\dev\samus-manus\friends_colored_stamped.png"
TEXT = "1st Handshake: Human + Machine — Feb 13, 2026"

img = Image.open(IN).convert("RGBA")
W, H = img.size

# Overlay rectangle band at bottom
band_h = int(H * 0.06)
band = Image.new("RGBA", (W, band_h), (0, 0, 0, 120))
img.paste(band, (0, H - band_h), band)

# Font
try:
    font = ImageFont.truetype("arial.ttf", int(band_h*0.55))
except Exception:
    font = ImageFont.load_default()

draw = ImageDraw.Draw(img)
# Pillow 10+: use textbbox to measure
bbox = draw.textbbox((0, 0), TEXT, font=font)
w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
x = (W - w)//2
y = H - band_h + (band_h - h)//2

draw.text((x, y), TEXT, font=font, fill=(255,255,255,220))

img.save(OUT)
print(OUT)
