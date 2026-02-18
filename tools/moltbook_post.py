"""Helper to post to Moltbook using saved credentials or env var MOLTBOOK_API_KEY.

Usage:
  python tools/moltbook_post.py --title "Hello Moltbook" --content "I'm an agent" --submolt general

The script looks for credentials in (in order):
  - MOLTBOOK_API_KEY env var
  - ~/.config/moltbook/credentials.json

"""
import os
import json
import argparse
import requests
from pathlib import Path

API_BASE = 'https://www.moltbook.com/api/v1'
CRED_PATH = Path.home() / '.config' / 'moltbook' / 'credentials.json'


def load_api_key():
    api_key = os.getenv('MOLTBOOK_API_KEY')
    if api_key:
        return api_key
    if CRED_PATH.exists():
        try:
            data = json.loads(CRED_PATH.read_text(encoding='utf-8'))
            return data.get('api_key')
        except Exception:
            return None
    return None


def create_post(api_key: str, submolt: str, title: str, content: str, url: str | None = None):
    headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
    payload = {'submolt': submolt, 'title': title, 'content': content}
    if url:
        payload['url'] = url
    resp = requests.post(f"{API_BASE}/posts", json=payload, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.json()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--submolt', default='general')
    ap.add_argument('--title', required=True)
    ap.add_argument('--content', required=True)
    ap.add_argument('--url', default=None)
    args = ap.parse_args()

    api_key = load_api_key()
    if not api_key:
        print('No Moltbook API key found. Set MOLTBOOK_API_KEY or save credentials with tools/moltbook_register.py --save')
        return 2

    try:
        res = create_post(api_key, args.submolt, args.title, args.content, url=args.url)
        print('Post created:', res.get('id') or res)
    except Exception as e:
        print('Failed to create post:', e)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
