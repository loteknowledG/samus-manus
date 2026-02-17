#!/usr/bin/env python
import asyncio, json, threading, queue, sys

PORT = 8766

class TTSServer:
    def __init__(self, rate=180, voice_id=None):
        import pyttsx3
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', rate)
        if voice_id is not None:
            try:
                self.engine.setProperty('voice', voice_id)
            except Exception:
                pass
        self.q: queue.Queue = queue.Queue()
        self._stop = threading.Event()
        self.worker = threading.Thread(target=self._run, daemon=True)
        self.worker.start()

    def _run(self):
        while not self._stop.is_set():
            item = self.q.get()
            if item is None:
                break
            try:
                text = item.get('text','')
                if not text:
                    continue
                r = item.get('rate')
                v = item.get('voice')
                if r is not None:
                    try: self.engine.setProperty('rate', int(r))
                    except Exception: pass
                if v is not None:
                    try: self.engine.setProperty('voice', v)
                    except Exception: pass
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception:
                # swallow errors so the thread stays alive
                pass

    def enqueue(self, payload: dict):
        self.q.put(payload)

    def stop(self):
        self._stop.set()
        self.q.put(None)


async def serve():
    import websockets
    tts = TTSServer()

    async def handler(ws):
        await ws.send(json.dumps({'ok': True, 'ready': True}))
        async for message in ws:
            try:
                data = None
                try:
                    data = json.loads(message)
                except Exception:
                    data = {'text': str(message)}
                cmd = (data.get('cmd') or '').lower()
                if cmd == 'stop':
                    try:
                        tts.engine.stop()
                    except Exception:
                        pass
                    await ws.send(json.dumps({'ok': True, 'stopped': True}))
                    continue
                if cmd == 'shutdown':
                    tts.stop()
                    await ws.send(json.dumps({'ok': True, 'shutdown': True}))
                    await ws.close()
                    break
                text = data.get('text')
                if not text:
                    await ws.send(json.dumps({'ok': False, 'error': 'no text'}))
                    continue
                tts.enqueue(data)
                await ws.send(json.dumps({'ok': True}))
            except Exception as e:
                await ws.send(json.dumps({'ok': False, 'error': str(e)}))

    async with websockets.serve(handler, '127.0.0.1', PORT):
        print(f'TTS server listening on ws://127.0.0.1:{PORT}', flush=True)
        while True:
            await asyncio.sleep(3600)


if __name__ == '__main__':
    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        pass
