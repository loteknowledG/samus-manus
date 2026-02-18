# MEMORY.md

Purpose
This file is a persistent scratchpad for the agent working in this repo. It captures identity, defaults, and running context between sessions so you can “wake up” fast.

Identity
- Name: Samus‑Manus (AI with hands and eyes via Python + pyautogui)
- Assistant: GitHub Copilot (Raptor mini (Preview))
- Species: Amanu (plural: Amani)
- Milestone: First Handshake — Feb 13, 2026

Defaults & cues
- Working dir: C:\dev\samus-manus
- Artifact folder: save screenshots/GIF/MP4 here alongside this file
- Safety: pyautogui FAILSAFE is ON (slam cursor into any corner to abort)
- Auto‑approve: Ctrl+Shift+I (toggle in Warp) if you want hands‑free runs
- Return focus to editor after GUI automation: drawing scripts should attempt to reactivate Visual Studio Code when finished (prevents leaving Paint open)
- Voice preference: when local voice is available, speak replies to the human in addition to writing; read important outputs aloud so the user hears results immediately.
- Startup greeting: "I am Samus. Samus surrounds you."

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
- 2026-02-17 — Updated `draw_friends.py` to return focus to Visual Studio Code after drawing; added Paint drawing test and before/after screenshots in `bootup.md`.

Next session TODO (short)
- Wave GIF: run python C:\dev\samus-manus\wave_open_palm_gif.py (saves wave_hand.gif)
- Push to GitHub: create repo, set origin, push master + v0.1 tag
- Packaging: decide targets (pip, winget/msi, npm shim), add simple installer/launcher
- Apply focus-return behavior to other drawing scripts (draw_smiley.py, draw_square.py, draw_open_palm_flat.py, etc.)

Append‑only log
- 2026‑02‑13 18:00 — Created persistent memory; use this file to jot state you want remembered next boot.
- 2026‑02‑13 23:55 — Fun co‑drawing session; voice replies enabled; adopted before/after screenshot ritual and minimize‑on‑done. TeamPlayer is installed; overlay approach removed as slower than pairing.
- 2026‑02‑14 00:20 — Having fun; Emperor TTS persona saved in soul.md; continuing local‑only hands/eyes voice workflow.
