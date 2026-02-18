#!/usr/bin/env python3
"""Open a Moltbook claim URL, fill owner email, click 'Send Verification Email'.

Usage:
  python tools/claim_moltbook.py <claim_url> --email you@example.com

Saves screenshots: claim_screen.png and claim_after_click.png
"""
import argparse
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError
import time


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('url')
    ap.add_argument('--email', required=True)
    ap.add_argument('--headful', action='store_true')
    args = ap.parse_args()

    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=not args.headful, args=['--start-maximized'])
    ctx = browser.new_context(viewport={"width":1280, "height":800})
    page = ctx.new_page()
    try:
        page.goto(args.url, wait_until='networkidle')
        time.sleep(0.6)
        page.screenshot(path='claim_screen.png', full_page=True)
        # try common email selectors
        selectors = ['input[type=email]', 'input[name=email]', 'input#email', 'input[type=text]', 'input']
        filled = False
        for sel in selectors:
            try:
                page.fill(sel, args.email, timeout=800)
                print('Filled selector:', sel)
                filled = True
                break
            except Exception:
                continue
        if not filled:
            print('Could not find an input to fill; continuing to click the button directly')

        # click the button by searching all <button> elements and matching visible text
        clicked = False
        try:
            btns = page.query_selector_all('button')
            for b in btns:
                txt = (b.inner_text() or '').strip().lower()
                if 'send verification' in txt or 'send verification email' in txt:
                    try:
                        b.click()
                        clicked = True
                        break
                    except Exception:
                        # try click via evaluate
                        try:
                            page.evaluate('(el) => el.click()', b)
                            clicked = True
                            break
                        except Exception:
                            continue
        except Exception:
            clicked = False

        print('Clicked send verification?', clicked)
        time.sleep(1.6)
        page.screenshot(path='claim_after_click.png', full_page=True)
        return 0
    finally:
        try:
            ctx.close()
            browser.close()
        finally:
            pw.stop()


if __name__ == '__main__':
    raise SystemExit(main())
