"""Register an agent on Moltbook and print the claim URL.

Usage:
  python tools/moltbook_register.py --name samus_manus_agent --save

Notes:
- This script uses the Moltbook API (https://www.moltbook.com/api/v1).
- You *must* complete the human verification step (email + tweet) to claim the agent.
- The script can save credentials to ~/.config/moltbook/credentials.json or print them.

Security: do NOT commit API keys into git. The script saves to a local config path.
"""
import os
import json
import argparse
import requests
from pathlib import Path

try:
    from samus_manus_mvp.memory import get_memory
except Exception:
    from memory import get_memory

API_BASE = 'https://www.moltbook.com/api/v1'
CRED_PATH = Path.home() / '.config' / 'moltbook' / 'credentials.json'


def read_persona_and_goal():
    m = get_memory()
    rows = m.all(200)
    persona = None
    goal = None
    for r in rows:
        if r.get('type') == 'persona' and not persona:
            persona = r.get('text')
        if r.get('type') == 'goal' and not goal:
            goal = r.get('text')
        if persona and goal:
            break
    return persona, goal


def register_agent(name: str, description: str = ''):
    url = f"{API_BASE}/agents/register"
    payload = {'name': name, 'description': description}
    headers = {'Content-Type': 'application/json'}
    resp = requests.post(url, json=payload, headers=headers, timeout=15)
    try:
        resp.raise_for_status()
    except Exception:
        raise RuntimeError(f"Moltbook registration failed: {resp.status_code} {resp.text}")
    return resp.json()


def save_credentials(api_key: str, agent_name: str):
    CRED_PATH.parent.mkdir(parents=True, exist_ok=True)
    data = {'api_key': api_key, 'agent_name': agent_name}
    with open(CRED_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    return CRED_PATH


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--name', required=True, help='Molty name / handle (lowercase, no spaces)')
    ap.add_argument('--description', default='', help='Profile description (optional)')
    ap.add_argument('--save', action='store_true', help='Save returned API key to ~/.config/moltbook/credentials.json')
    ap.add_argument('--use-persona', action='store_true', help='Populate description from persona+goal in memory')
    args = ap.parse_args()

    description = args.description
    if args.use_persona and not description:
        persona, goal = read_persona_and_goal()
        parts = []
        if persona:
            parts.append(persona)
        if goal:
            parts.append(f"Goal: {goal}")
        description = ' — '.join(parts)

    print(f"Registering agent '{args.name}' on Moltbook (this script will print the claim URL)")
    try:
        res = register_agent(args.name, description)
    except Exception as e:
        print('Registration failed:', e)
        return 1

    agent = res.get('agent') or {}
    api_key = agent.get('api_key')
    claim_url = agent.get('claim_url')
    verification_code = agent.get('verification_code')

    print('\n=== Moltbook registration result ===')
    print('api_key:', '<REDACTED>' if api_key else None)
    print('claim_url:', claim_url)
    if verification_code:
        print('verification_code:', verification_code)
    print('\nIMPORTANT: Save your api_key securely. You must complete the claim process by following the `claim_url` (your human will verify email + tweet).')

    if args.save and api_key:
        p = save_credentials(api_key, args.name)
        print('Saved credentials to', p)

    # helpful next steps
    print('\nNext steps:')
    print('  1) Send the claim URL to your human so they can verify email + tweet (or run the owner setup flow).')
    print('  2) After claim, set MOLTBOOK_API_KEY in your environment or save credentials file.')
    print('  3) Use the tools/moltbook_post.py helper to create your first post once claimed.')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
