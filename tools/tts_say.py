#!/usr/bin/env python
import argparse, asyncio, json, os, sys, time, subprocess

PORT = 8766

async def send(text, rate=None, voice=None, wait=False, host='127.0.0.1', port=PORT):
    import websockets
    uri = f'ws://{host}:{port}'
    async with websockets.connect(uri) as ws:
        await ws.recv()  # ready
        payload = {'text': text}
        if rate is not None:
            payload['rate'] = rate
        if voice is not None:
            payload['voice'] = voice
        if wait:
            payload['wait'] = True
        await ws.send(json.dumps(payload))
        return await ws.recv()


def ensure_server(host='127.0.0.1', port=PORT):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.2)
        try:
            s.connect((host, port))
            return True
        except Exception:
            pass

    # Start the TTS server in a foreground-capable mode so audio playback is reliable.
    # Write stdout/stderr to a rolling log file so playback can be diagnosed.
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    server = os.path.join(root, 'tools', 'tts_server.py')
    log_path = os.path.join(root, 'tools', 'tts_server.log')

    # Use non-detached creationflags on Windows so the process has a normal
    # audio/session context. Capture stdout/stderr to the log file for debugging.
    try:
        logf = open(log_path, 'a', buffering=1, encoding='utf-8')
        try:
            proc = subprocess.Popen([sys.executable, server], stdout=logf, stderr=subprocess.STDOUT, creationflags=0)
        except TypeError:
            # creationflags may not be supported on some platforms — fall back
            proc = subprocess.Popen([sys.executable, server], stdout=logf, stderr=subprocess.STDOUT)
    except Exception:
        # Best-effort fallback to detached start if logging can't be opened
        try:
            subprocess.Popen([sys.executable, server], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    # Wait up to ~3s for the server to accept connections
    for _ in range(12):
        time.sleep(0.25)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.2)
            try:
                s.connect((host, port))
                return True
            except Exception:
                continue
    return False


def main():
    ap = argparse.ArgumentParser(description='Say text via persistent TTS server')
    ap.add_argument('text', nargs='+')
    ap.add_argument('--rate', type=int)
    ap.add_argument('--voice')
    ap.add_argument('--ensure', action='store_true', help='Start server if not running')
    ap.add_argument('--wait', action='store_true', help='Wait until playback completes (server will acknowledge after audio finishes)')
    args = ap.parse_args()

    msg = ' '.join(args.text)

    if args.ensure:
        ensure_server()

    try:
        out = asyncio.run(send(msg, rate=args.rate, voice=args.voice, wait=args.wait))
        if out:
            print(out)
    except Exception:
        # Fallback one-shot if server unavailable
        try:
            import pyttsx3
            e = pyttsx3.init(); 
            if args.rate: e.setProperty('rate', args.rate)
            if args.voice: e.setProperty('voice', args.voice)
            e.say(msg); e.runAndWait()
        except Exception as e:
            print({'ok': False, 'error': str(e)})

if __name__ == '__main__':
    main()
