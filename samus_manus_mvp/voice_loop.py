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
    args = ap.parse_args()

    if not args.text:
        print('Usage: voice_loop.py "Hello world"')
    else:
        text = ' '.join(args.text)
        if args.loop:
            while True:
                speak(text)
                time.sleep(1)
        else:
            speak(text)
