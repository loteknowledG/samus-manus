#!/usr/bin/env python3
from playwright.sync_api import sync_playwright

def run():
    css = 'body.ibm_plex_mono_973e1757-module__8DqIaW__variable.antialiased.flex.flex-col.min-h-screen > div.flex-1 > div.min-h-screen.bg-[#0a0a0a].flex.items-center.justify-center.p-4 > div.bg-[#1a1a1b].border.border-[#343536].rounded-lg.p-8.max-w-md.w-full > div.space-y-4 > button.w-full.bg-[#ff4500].hover:bg-[#ff5722].disabled:bg-[#333].disabled:text-[#818384].text-white.font-bold.py-3.px-6.rounded-full.transition-colors'
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=False, args=['--start-maximized'])
        ctx = b.new_context(viewport={'width':1280,'height':800})
        page = ctx.new_page()
        page.goto('https://www.moltbook.com/claim/moltbook_claim_Nuw2u0ekgt3eacqZFUePR_zmjiq-2yNf', wait_until='networkidle')
        page.fill('input[type=email]', 'cathycreampiewife@gmail.com')
        try:
            page.click(css, timeout=5000)
            print('clicked via css')
        except Exception as e:
            print('css click failed', e)
        page.screenshot(path='claim_after_manual_click.png', full_page=True)
        ctx.close()
        b.close()

if __name__ == '__main__':
    run()
