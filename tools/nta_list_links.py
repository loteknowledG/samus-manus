#!/usr/bin/env python3
from playwright.sync_api import sync_playwright

URL = 'https://nothumanallowed.com/'
with sync_playwright() as pw:
    b = pw.chromium.launch(headless=True)
    ctx = b.new_context(viewport={'width':1280, 'height':800})
    page = ctx.new_page()
    page.goto(URL, wait_until='networkidle')
    anchors = page.query_selector_all('a')
    results = []
    for a in anchors:
        try:
            if not a.is_visible():
                continue
            txt = (a.inner_text() or '').strip()
            href = a.get_attribute('href')
            results.append({'text': txt, 'href': href})
        except Exception:
            continue
    print(results)
    ctx.close()
    b.close()