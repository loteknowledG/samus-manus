#!/usr/bin/env python3
"""
tools/web_hands.py — lightweight Playwright helpers for "web‑surfing hands".

Quick capabilities:
- open a page, click by text or selector, fill inputs, take screenshots
- CLI for quick manual runs and a small programmatic API for scripts/tests

Prerequisites (one-time):
  pip install playwright
  playwright install

Examples:
  python tools/web_hands.py open "https://example.com" --headful
  python tools/web_hands.py click-text "Send verification" --wait 2000
  python tools/web_hands.py fill "#email" "me@example.com"
  python tools/web_hands.py screenshot --out page.png

"""
import argparse
import sys
import time
from typing import Optional

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError
except Exception as e:
    raise SystemExit("Playwright is required. Run: pip install playwright && playwright install") from e


class WebHands:
    def __init__(self, headful: bool = True, viewport=(1280, 800)):
        self._pw = sync_playwright().start()
        self.browser = self._pw.chromium.launch(headless=not headful, args=["--start-maximized"])
        self.context = self.browser.new_context(viewport={"width": viewport[0], "height": viewport[1]})
        self.page = self.context.new_page()

    def goto(self, url: str, wait_until: str = "networkidle") -> None:
        print(f"→ Navigating to {url}")
        self.page.goto(url, wait_until=wait_until)

    def click_text(self, text: str, timeout: int = 5000) -> bool:
        """Click an element that contains visible `text`. Returns True on success."""
        # Prefer Playwright text selector, then fallback to xpath contains
        try:
            self.page.click(f'text="{text}"', timeout=timeout)
            return True
        except PWTimeoutError:
            xpath = f"//button[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), '{text.lower()}')]"
            try:
                self.page.click(f'xpath={xpath}', timeout=timeout)
                return True
            except PWTimeoutError:
                return False

    def click(self, selector: str, timeout: int = 5000) -> None:
        self.page.click(selector, timeout=timeout)

    def fill(self, selector: str, value: str, timeout: int = 5000) -> None:
        self.page.fill(selector, value, timeout=timeout)

    def screenshot(self, path: str = "webhands.png", full_page: bool = True) -> None:
        self.page.screenshot(path=path, full_page=full_page)
        print(f"Saved screenshot: {path}")

    def find_text(self, text: str) -> bool:
        try:
            return self.page.is_visible(f'text="{text}"')
        except Exception:
            return False

    def wait(self, seconds: float) -> None:
        time.sleep(seconds)

    def close(self) -> None:
        try:
            self.context.close()
            self.browser.close()
        finally:
            self._pw.stop()


def _cli_args() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Web‑surfing hands (Playwright helper)")
    sub = p.add_subparsers(dest="cmd", required=True)

    open_p = sub.add_parser("open", help="Open a URL")
    open_p.add_argument("url")
    open_p.add_argument("--headful", action="store_true", help="Show browser window")

    click_text_p = sub.add_parser("click-text", help="Click an element by visible text")
    click_text_p.add_argument("text")
    click_text_p.add_argument("--wait", type=int, default=800)
    click_text_p.add_argument("--headful", action="store_true")

    click_p = sub.add_parser("click", help="Click a CSS selector")
    click_p.add_argument("selector")
    click_p.add_argument("--headful", action="store_true")

    fill_p = sub.add_parser("fill", help="Fill an input")
    fill_p.add_argument("selector")
    fill_p.add_argument("value")
    fill_p.add_argument("--headful", action="store_true")

    screenshot_p = sub.add_parser("screenshot", help="Take a screenshot of current page")
    screenshot_p.add_argument("--out", default="webhands.png")
    screenshot_p.add_argument("--headful", action="store_true")

    return p


def main(argv: Optional[list] = None) -> int:
    args = _cli_args().parse_args(argv)
    headful = getattr(args, "headful", False)

    wh = WebHands(headful=headful)
    try:
        if args.cmd == "open":
            wh.goto(args.url)
            wh.wait(0.5)
            return 0

        if args.cmd == "click-text":
            success = wh.click_text(args.text)
            print("Clicked?", success)
            wh.wait(args.wait / 1000.0)
            return 0 if success else 2

        if args.cmd == "click":
            wh.click(args.selector)
            wh.wait(0.5)
            return 0

        if args.cmd == "fill":
            wh.fill(args.selector, args.value)
            wh.wait(0.2)
            return 0

        if args.cmd == "screenshot":
            wh.screenshot(path=args.out)
            return 0

        print('Unknown command')
        return 3

    finally:
        wh.close()


if __name__ == "__main__":
    raise SystemExit(main())
