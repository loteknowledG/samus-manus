#!/usr/bin/env python3
"""
tools/find_page_elements.py — scan a page for button-like elements and report
selectors/text to help automation (uses Playwright).

Usage:
  python tools/find_page_elements.py https://example.com

Outputs:
  - prints JSON to stdout
  - writes `molt_scan.png` (screenshot) and `molt_scan_results.json`
"""
import sys
import json
import re
from urllib.parse import urlparse

try:
    from playwright.sync_api import sync_playwright
except Exception:
    raise SystemExit('Playwright required. Run: pip install playwright && python -m playwright install')

KEYWORD_RE = re.compile(r'verify|verification|claim|confirm|send|email|activate', re.I)


def scan(url: str):
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until='networkidle')

        page.screenshot(path='molt_scan.png', full_page=True)

        sel = 'button, a, input[type=button], input[type=submit], [role="button"], [data-testid], [aria-label]'
        nodes = page.query_selector_all(sel)

        results = []
        matches = []
        for i, n in enumerate(nodes):
            try:
                tag = n.evaluate('(el)=>el.tagName')
                text = ''
                if tag.lower() == 'input':
                    text = (n.get_attribute('value') or '').strip()
                else:
                    text = (n.inner_text() or '').strip()
                eid = (n.get_attribute('id') or '').strip()
                cls = (n.get_attribute('class') or '').strip()
                visible = n.is_visible() if hasattr(n, 'is_visible') else True
                outer = (n.get_attribute('outerHTML') or '')[:400]
                selector_path = n.evaluate("(el)=>{let p=[];while(el && el.tagName && el.tagName!=='HTML'){let s=el.tagName.toLowerCase()+(el.id?('#'+el.id):'') + (el.className?('.'+el.className.split(/\\s+/).filter(Boolean).join('.')):''); p.unshift(s); el=el.parentElement;} return p.join(' > ');} ")
                obj = {'index': i, 'tag': tag, 'text': text, 'id': eid, 'class': cls, 'visible': visible, 'selector': selector_path, 'outer': outer}
                results.append(obj)
                if KEYWORD_RE.search(text) or KEYWORD_RE.search(outer):
                    matches.append(obj)
            except Exception:
                continue

        out = {'url': url, 'total_candidates': len(results), 'matched_by_keyword': len(matches), 'matches': matches, 'sample_candidates': results[:60]}
        with open('molt_scan_results.json', 'w', encoding='utf8') as f:
            json.dump(out, f, indent=2)
        print(json.dumps(out, indent=2))
        browser.close()


if __name__ == '__main__':
    url = sys.argv[1] if len(sys.argv) > 1 else 'https://example.com'
    scan(url)
