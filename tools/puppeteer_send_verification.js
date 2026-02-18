#!/usr/bin/env node
/*
 * tools/puppeteer_send_verification.js
 * - Usage: npm install puppeteer
 * - Run:  node tools/puppeteer_send_verification.js <url> ["button text"] [--headful]
 *
 * Opens the given URL in a visible Chromium instance (default headful),
 * saves before/after screenshots and attempts to click a button whose
 * text contains "Send Verification" (or the provided button text).
 *
 * Note: you must already be logged in to the site if the page is behind auth.
 */

const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer');

async function run() {
  const argv = process.argv.slice(2);
  if (argv.length === 0) {
    console.error('Usage: node tools/puppeteer_send_verification.js <url> ["button text"] [--headful]');
    process.exit(2);
  }

  const url = argv[0];
  const headful = argv.includes('--headful');
  // second positional argument (if present and not a flag) is button text
  const maybe = argv[1] && !argv[1].startsWith('--') ? argv[1] : null;
  const buttonText = (maybe && maybe.length) ? maybe : 'send verification';

  const beforePath = path.resolve('puppeteer_verify_before.png');
  const afterPath = path.resolve('puppeteer_verify_after.png');

  const browser = await puppeteer.launch({
    headless: !headful,
    defaultViewport: null,
    args: ['--start-maximized']
  });
  const [page] = await browser.pages();
  await page.setDefaultNavigationTimeout(60_000);
  console.log('Navigating to', url);
  await page.goto(url, { waitUntil: 'networkidle2' });

  await page.screenshot({ path: beforePath, fullPage: true });
  console.log('Saved before screenshot to', beforePath);

  // XPath matcher using case-insensitive contains
  const normalized = buttonText.toLowerCase();
  const xpath = `//button[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), '${normalized}')]`;
  const xpathAlt = `//a[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), '${normalized}')]`;

  let handle = null;
  try {
    // Preferred XPath lookup when available
    if (typeof page.$x === 'function') {
      const found = await page.$x(xpath);
      if (found && found.length) handle = found[0];
      if (!handle) {
        const found2 = await page.$x(xpathAlt);
        if (found2 && found2.length) handle = found2[0];
      }
    }
  } catch (err) {
    // page.$x may not be supported by this Puppeteer/Chromium pairing — fall back below
  }

  // fallback: scan buttons/links for matching text
  if (!handle) {
    const candidates = await page.$$('button, a, input[type=button], input[type=submit]');
    for (const c of candidates) {
      const txt = (await (await c.getProperty('innerText')).jsonValue()) || (await (await c.getProperty('value')).jsonValue()) || '';
      if (txt && txt.toLowerCase().includes(normalized)) {
        handle = c;
        break;
      }
    }
  }

  if (!handle) {
    console.error('Could not find a button/link containing text:', buttonText);
    console.error('Saved screenshot to', beforePath);
    await browser.close();
    process.exit(3);
  }

  console.log('Clicking verification element...');
  try {
    await handle.click({ delay: 50 });
  } catch (err) {
    // fallback to evaluating click in page context
    await page.evaluate(el => el.click(), handle);
  }

  // wait a short time for UI updates, then capture after screenshot
  await page.waitForTimeout(1800);
  await page.screenshot({ path: afterPath, fullPage: true });
  console.log('Saved after screenshot to', afterPath);

  // quick heuristic: check for common error/alert selectors
  const errorCount = await page.$$eval('.alert-danger, .alert-error, .error, [role="alert"]', els => els.length);
  console.log('Detected alert-like elements on page:', errorCount);

  await browser.close();
  console.log('Done.');
}

run().catch(err => { console.error(err); process.exit(1); });