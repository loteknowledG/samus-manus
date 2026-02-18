#!/usr/bin/env python3
import json
import requests
from pathlib import Path
p = Path.home() / '.config' / 'moltbook' / 'credentials.json'
if not p.exists():
    print('No Moltbook credentials found at', p)
    raise SystemExit(1)
creds = json.loads(p.read_text())
api_key = creds.get('api_key')
resp = requests.get('https://www.moltbook.com/api/v1/agents/me', headers={'Authorization': f'Bearer {api_key}'}, timeout=15)
print(json.dumps(resp.json(), indent=2))
