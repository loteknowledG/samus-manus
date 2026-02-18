#!/usr/bin/env python3
"""Open nothumanallowed.com, click the largest visible clickable element (CTA),
and save before/after screenshots.
"""
from playwright.sync_api import sync_playwright
import time

URL = 'https://nothumanallowed.com/'

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=False, args=['--start-maximized'])
    ctx = browser.new_context(viewport={'width':1280, 'height':800})
    page = ctx.new_page()
    page.goto(URL, wait_until='networkidle')
    time.sleep(0.5)
    page.screenshot(path='nothuman_before.png', full_page=True)

    # collect visible buttons/links with bounding boxes
    handles = page.query_selector_all('button, a')
    candidates = []
    for h in handles:
        try:
            if not h.is_visible():
                continue
            box = page.evaluate('(el) => { const r = el.getBoundingClientRect(); return {x: r.x, y: r.y, w: r.width, h: r.height, text: (el.innerText || el.value || "").trim()}; }', h)
            area = (box.get('w') or 0) * (box.get('h') or 0)
            if area > 5:  # ignore tiny elements
                candidates.append((area, box.get('text',''), h))
        except Exception:
            continue

    if not candidates:
        print('No visible clickable elements found on page.')
    else:
        candidates.sort(reverse=True, key=lambda x: x[0])
        area, text, handle = candidates[0]
        print('Clicking element:', repr(text[:120]), 'area=', area)
        try:
            handle.click(timeout=5000)
            time.sleep(1.0)
            page.screenshot(path='nothuman_after.png', full_page=True)
            print('Clicked and saved nothuman_after.png')
        except Exception as e:
            print('Click failed:', e)

    try:
        ctx.close()
        browser.close()
    finally:
        pw.stop()
