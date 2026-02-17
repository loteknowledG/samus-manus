from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

root = Path(__file__).resolve().parents[1]
assets = root / 'docs' / 'assets'
assets.mkdir(parents=True, exist_ok=True)

bg_path = assets / 'friends_colored_stamped.png'
if not bg_path.exists():
    # fallback to non-stamped
    bg_path = assets / 'friends_colored.png'
    if not bg_path.exists():
        bg_path = root / 'friends_colored_stamped.png'

W, H = 1200, 630
img = Image.new('RGB', (W, H), (24, 24, 32))

# paste background image centered
try:
    bg = Image.open(bg_path).convert('RGB')
    # fit into 1100x450
    max_w, max_h = 1100, 450
    ratio = min(max_w / bg.width, max_h / bg.height)
    bg = bg.resize((int(bg.width*ratio), int(bg.height*ratio)), Image.LANCZOS)
    x = (W - bg.width) // 2
    y = 110
    img.paste(bg, (x, y))
except Exception:
    pass

# header band
draw = ImageDraw.Draw(img)
draw.rectangle([0,0,W,90], fill=(111,66,193))

# text
title = 'Amanu — agents with hands and eyes'
subtitle = 'Samus‑Manus v0.1 · First Handshake · Feb 13, 2026'
try:
    font_title = ImageFont.truetype('arialbd.ttf', 54)
    font_sub = ImageFont.truetype('arial.ttf', 28)
except Exception:
    font_title = ImageFont.load_default()
    font_sub = ImageFont.load_default()

# center title in band
bbox = draw.textbbox((0,0), title, font=font_title)
tw = bbox[2] - bbox[0]
draw.text(((W - tw)//2, 18), title, font=font_title, fill=(255,255,255))

# bottom subtitle
sb = draw.textbbox((0,0), subtitle, font=font_sub)
sw = sb[2] - sb[0]
draw.rectangle([0,H-80,W,H], fill=(0,0,0,160))
draw.text(((W - sw)//2, H-60), subtitle, font=font_sub, fill=(220,220,220))

out = assets / 'og.png'
img.save(out, format='PNG')
print(out)
