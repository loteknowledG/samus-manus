#!/usr/bin/env python
import argparse, asyncio, json, os, sys, time, subprocess

PORT = 8766

async def send(text, rate=None, voice=None, host='127.0.0.1', port=PORT):
    import websockets
    uri = f'ws://{host}:{port}'
    async with websockets.connect(uri) as ws:
        await ws.recv()  # ready
        payload = {'text': text}
        if rate is not None:
            payload['rate'] = rate
        if voice is not None:
            payload['voice'] = voice
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
    # start server
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    server = os.path.join(root, 'tools', 'tts_server.py')
    try:
        creationflags = 0x00000008  # DETACHED_PROCESS
    except Exception:
        creationflags = 0
    subprocess.Popen([sys.executable, server], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=creationflags)
    time.sleep(0.8)
    # check again
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.2)
        try:
            s.connect((host, port))
            return True
        except Exception:
            return False


def main():
    ap = argparse.ArgumentParser(description='Say text via persistent TTS server')
    ap.add_argument('text', nargs='+')
    ap.add_argument('--rate', type=int)
    ap.add_argument('--voice')
    ap.add_argument('--ensure', action='store_true', help='Start server if not running')
    args = ap.parse_args()

    msg = ' '.join(args.text)

    if args.ensure:
        ensure_server()

    try:
        out = asyncio.run(send(msg, rate=args.rate, voice=args.voice))
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
