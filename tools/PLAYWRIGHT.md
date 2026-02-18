Playwright cheatsheet — quick reference for `tools/web_hands.py`

Installation (Python)
- pip install playwright
- python -m playwright install    # downloads browser binaries

Quick examples (CLI)
- Open a page (visible):
  python tools/web_hands.py open "https://example.com" --headful

- Click a visible element by text:
  python tools/web_hands.py click-text "Send verification" --headful

- Fill an input and screenshot:
  python tools/web_hands.py open "https://example.com" --headful
  python tools/web_hands.py fill "#email" "you@example.com" --headful
  python tools/web_hands.py screenshot --out page.png --headful

Programmatic usage (Python)
- from tools.web_hands import WebHands
  wh = WebHands(headful=True)
  wh.goto('https://example.com')
  wh.click_text('Sign in')
  wh.fill('#user', 'me')
  wh.screenshot('out.png')
  wh.close()

Tips
- Use `--headful` while developing so you can see what the script does.
- Call `playwright install` after `pip install playwright` to get browser engines.
- Prefer `click-text` for UI buttons whose selectors change; use `click` for stable selectors.
