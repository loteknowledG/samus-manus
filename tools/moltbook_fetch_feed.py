#!/usr/bin/env python3
import json, requests, pathlib
p = pathlib.Path.home() / '.config' / 'moltbook' / 'credentials.json'
creds = json.loads(p.read_text())
api_key = creds.get('api_key')
url = 'https://www.moltbook.com/api/v1/feed?sort=new&limit=8'
resp = requests.get(url, headers={'Authorization': f'Bearer {api_key}'}, timeout=15)
print(resp.status_code)
print(json.dumps(resp.json(), indent=2)[:2000])
