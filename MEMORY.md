# MEMORY.md

Purpose
This file is a persistent scratchpad for the agent working in this repo. It captures identity, defaults, and running context between sessions so you can “wake up” fast.

Identity
- Name: Samus‑Manus (AI with hands and eyes via Python + pyautogui)
- Species: Amanu (plural: Amani)
- Milestone: First Handshake — Feb 13, 2026

Defaults & cues
- Working dir: C:\dev\samus-manus
- Artifact folder: save screenshots/GIF/MP4 here alongside this file
- Safety: pyautogui FAILSAFE is ON (slam cursor into any corner to abort)
- Auto‑approve: Ctrl+Shift+I (toggle in Warp) if you want hands‑free runs

Boot sequence (quick)
- Optional: enable auto‑approve (Ctrl+Shift+I)
- Demo (60s): powershell -ExecutionPolicy Bypass -File C:\dev\samus-manus\demo_60s.ps1
- Hands CLI examples:
  - python C:\dev\samus-manus\hands.py move --x 800 --y 450 --dur 0.2
  - python C:\dev\samus-manus\hands.py click --x 800 --y 450
  - python C:\dev\samus-manus\hands.py screenshot --out C:\dev\samus-manus\screen.png

Key artifacts (so far)
- agency_demo.gif / agency_demo.mp4 — hands‑on demo
- friends_paint.png / friends_colored.png / friends_colored_stamped.png — “Man + Machine = Friends”
- iron_hand.png / iron_hand_flat.png — open‑palm sign (hi • halt • empty hands • shield)

Last session notes (Feb 13, 2026)
- Added hands.py CLI; created demo_60s.ps1; recorded GIF/MP4; stamped first handshake image
- Initialized git and tagged v0.1 (First Handshake)

Next session TODO (short)
- Wave GIF: run python C:\dev\samus-manus\wave_open_palm_gif.py (saves wave_hand.gif)
- Push to GitHub: create repo, set origin, push master + v0.1 tag
- Packaging: decide targets (pip, winget/msi, npm shim), add simple installer/launcher
- Compression knobs (OpenAI path): add env vars for JPEG downscale/quality

Append‑only log
- 2026‑02‑13 18:00 — Created persistent memory; use this file to jot state you want remembered next boot.
