import cv2
import numpy as np
from pathlib import Path

SRC = Path('claim_screen.png')
OUT = Path('tools/refresh_btn_template.png')
if not SRC.exists():
    print('claim_screen.png not found')
    raise SystemExit(1)

img = cv2.imread(str(SRC))
h, w = img.shape[:2]
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (5,5), 0)
edged = cv2.Canny(blur, 30, 150)

contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

candidates = []
for c in contours:
    x,y,ww,hh = cv2.boundingRect(c)
    # filter plausible button sizes (relative to image)
    if ww < 60 or hh < 20 or ww > 600 or hh > 200:
        continue
    ar = ww/float(hh)
    if ar < 1.2 or ar > 8.0:
        continue
    # prefer candidates in the vertical middle/lower part where API panel sits
    if not (int(h*0.35) < y < int(h*0.7)):
        continue
    candidates.append((x,y,ww,hh))

# If no candidates, relax vertical constraint
if not candidates:
    for c in contours:
        x,y,ww,hh = cv2.boundingRect(c)
        if ww < 60 or hh < 20 or ww > 600 or hh > 200:
            continue
        ar = ww/float(hh)
        if ar < 1.2 or ar > 8.0:
            continue
        candidates.append((x,y,ww,hh))

if not candidates:
    print('no button-like candidates found')
    raise SystemExit(2)

# score candidates by darkness (buttons tend to be darker than background)
best = None
best_score = 1e9
for (x,y,ww,hh) in candidates:
    crop = gray[y:y+hh, x:x+ww]
    mean = float(crop.mean())
    # lower mean -> darker -> prefer
    score = mean
    if score < best_score:
        best_score = score
        best = (x,y,ww,hh)

(x,y,ww,hh) = best
padx = max(4, int(ww*0.08))
pady = max(4, int(hh*0.15))
xs = max(0, x-padx)
ys = max(0, y-pady)
xe = min(w, x+ww+padx)
ye = min(h, y+hh+pady)
patch = img[ys:ye, xs:xe]
OUT.parent.mkdir(parents=True, exist_ok=True)
cv2.imwrite(str(OUT), patch)
print('wrote', OUT, 'bbox=', (xs, ys, xe-xs, ye-ys))
