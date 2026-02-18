#!/usr/bin/env python3
"""
Simple offline TTS helper using pyttsx3.
Provides a CLI to speak text and a small helper function `speak()` for other modules.
"""
import argparse
import pyttsx3
import time

_engine = None

def _get_engine():
    global _engine
    if _engine is None:
        _engine = pyttsx3.init()
        _engine.setProperty('rate', 160)
    return _engine


def speak(text: str):
    """Speak the given text (blocking)."""
    eng = _get_engine()
    eng.say(text)
    eng.runAndWait()


if __name__ == '__main__':
    ap = argparse.ArgumentParser(prog='voice_loop', description='TTS helper (pyttsx3)')
    ap.add_argument('text', nargs='*', help='Text to speak (or use --loop)')
    ap.add_argument('--loop', action='store_true', help='Say text repeatedly (demo)')
    ap.add_argument('--list-voices', action='store_true', help='List installed TTS voices and exit')
    ap.add_argument('--voice', help='Select voice by id or name keyword (e.g. Zira)')
    ap.add_argument('--hanna', action='store_true', help="Use Hanna's recommended female voice preset")
    ap.add_argument('--rate', type=int, help='Speech rate (words per minute)')
    args = ap.parse_args()

    eng = _get_engine()

    # list voices and exit
    if args.list_voices:
        voices = eng.getProperty('voices')
        for i, v in enumerate(voices):
            langs = getattr(v, 'languages', None)
            if langs:
                try:
                    langs_s = ','.join(l.decode('utf-8') if isinstance(l, bytes) else str(l) for l in langs)
                except Exception:
                    langs_s = str(langs)
            else:
                langs_s = ''
            print(f"{i}: {v.id} | {v.name} | {langs_s}")
        raise SystemExit(0)

    # apply Hanna preset (prefer a female-sounding voice)
    if args.hanna:
        voices = eng.getProperty('voices')
        chosen = None
        # heuristics for female/younger voices commonly available on Windows
        preferred_keywords = ['zira', 'anna', 'female', 'sara', 'sarah', 'siri']
        for v in voices:
            name = (v.name or '').lower()
            vid = (v.id or '').lower()
            if any(k in name or k in vid for k in preferred_keywords):
                chosen = v
                break
        if not chosen:
            # fallback: pick first voice that doesn't explicitly look male
            for v in voices:
                name = (v.name or '').lower()
                if 'david' not in name and 'male' not in name:
                    chosen = v
                    break
        if not chosen and voices:
            chosen = voices[0]
        if chosen:
            eng.setProperty('voice', chosen.id)
            eng.setProperty('rate', args.rate or 170)

    # explicit voice selection by keyword/id
    elif args.voice:
        voices = eng.getProperty('voices')
        kw = args.voice.lower()
        found = None
        for v in voices:
            if kw in (v.name or '').lower() or kw in (v.id or '').lower():
                found = v
                break
        if found:
            eng.setProperty('voice', found.id)

    # apply explicit rate if provided
    if args.rate:
        eng.setProperty('rate', args.rate)

    if not args.text:
        print('Usage: voice_loop.py "Hello world" (use --list-voices to see available voices)')
    else:
        text = ' '.join(args.text)
        if args.loop:
            while True:
                speak(text)
                time.sleep(1)
        else:
            speak(text)
