#!/usr/bin/env python3
"""
Samus‑Manus — minimal local agent MVP (safe defaults).
- Human‑in‑the‑loop by default (no destructive actions without --apply).
- Uses OpenAI if OPENAI_API_KEY is present; otherwise falls back to a tiny planner.
- Actions are simulated unless `--apply` is passed and `pyautogui` is available.

Usage:
  python samus_agent.py run "Install dependencies and take a screenshot"
  python samus_agent.py run "Open Notepad and type hello" --apply
"""
import os
import re
import json
import time
import argparse
import logging

try:
    import openai
except Exception:
    openai = None

try:
    import pyautogui
except Exception:
    pyautogui = None

# optional persistent memory (if present)
try:
    from memory import get_memory
except Exception:
    try:
        from samus_manus_mvp.memory import get_memory
    except Exception:
        get_memory = None

logging.basicConfig(level=logging.INFO, format="%(message)s")


def parse_actions(text: str) -> list[dict]:
    """Extract a JSON array of action objects from model output (best‑effort)."""
    # try to find JSON array in code block or raw
    m = re.search(r'```(?:json)?\s*(\[[\s\S]*?\])\s*```', text)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    m = re.search(r'(\[[\s\S]*?\])', text)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    # fallback: find individual objects
    actions = []
    for match in re.finditer(r'\{[^{}]+\}', text):
        try:
            obj = json.loads(match.group())
            if "type" in obj:
                actions.append(obj)
        except Exception:
            continue
    return actions


def fallback_plan(task: str) -> list[dict]:
    """Very small deterministic planner used when no LLM is available."""
    actions = []
    # simple heuristics
    if "screenshot" in task.lower():
        actions.append({"type": "wait", "seconds": 0.5})
        actions.append({"type": "screenshot", "out": "samus_screenshot.png"})
    if "open" in task.lower() and "notepad" in task.lower():
        actions.append({"type": "press", "key": "win"})
        actions.append({"type": "type", "text": "notepad"})
        actions.append({"type": "press", "key": "enter"})
    if not actions:
        actions.append({"type": "type", "text": task})
    actions.append({"type": "done"})
    return actions


def plan_with_openai(task: str) -> list[dict]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not openai or not api_key:
        return fallback_plan(task)

    openai.api_key = api_key
    prompt = (
        "You are a safe local agent planner. Break the user's task into a short JSON array "
        "of low‑level actions. Allowed actions: click, double_click, find_click, type, press, hotkey, "
        "screenshot (out), wait (seconds), done. Return ONLY a JSON array.\nTask: "
        + task
    )
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.0,
        )
        text = resp.choices[0].message.content
        actions = parse_actions(text)
        if actions:
            return actions
    except Exception as e:
        logging.info("OpenAI plan failed — falling back: %s", e)
    return fallback_plan(task)


# optional eyes helpers (capture/find). Provide safe fallbacks if unavailable
try:
    # prefer local module import
    from eyes import capture_screenshot, find_on_screen
except Exception:
    try:
        from samus_manus_mvp.eyes import capture_screenshot, find_on_screen
    except Exception:
        def capture_screenshot(out):
            raise RuntimeError('eyes.capture_screenshot not available')
        def find_on_screen(img, confidence=0.8, timeout=3.0):
            return None

def execute_action(action: dict, apply: bool) -> str:
    t = action.get("type")
    if t == "wait":
        s = float(action.get("seconds", 1))
        time.sleep(s)
        return f"waited {s}s"

    if t == "screenshot":
        out = action.get("out", "screen.png")
        # prefer eyes.capture_screenshot when available
        try:
            path = capture_screenshot(out)
            return f"screenshot saved {path}"
        except Exception:
            if apply and pyautogui:
                pyautogui.screenshot(out)
                return f"screenshot saved {out}"
            return f"(sim) screenshot -> {out}"

    if t == "click":
        x = action.get("x")
        y = action.get("y")
        button = action.get("button", "left")
        if x is None or y is None:
            return "click: missing coordinates"
        if apply and pyautogui:
            pyautogui.click(int(x), int(y), button=button)
            return f"clicked at ({x},{y})"
        return f"(sim) click at ({x},{y})"

    if t == "double_click":
        x = action.get("x")
        y = action.get("y")
        if x is None or y is None:
            return "double_click: missing coordinates"
        if apply and pyautogui:
            pyautogui.doubleClick(int(x), int(y))
            return f"double-clicked at ({x},{y})"
        return f"(sim) double-click at ({x},{y})"

    if t == "find_click" or t == "find-click":
        img = action.get("img")
        confidence = action.get("confidence", 0.8)
        timeout = action.get("timeout", 3.0)
        button = action.get("button", "left")
        if not img:
            return "find_click: missing img path"
        pos = find_on_screen(img, confidence=confidence, timeout=timeout)
        if not pos:
            return f"image not found: {img}"
        x, y = pos
        if apply and pyautogui:
            pyautogui.click(x, y, button=button)
            return f"found and clicked {img} at ({x},{y})"
        return f"(sim) found {img} at ({x},{y})"

    if t == "type":
        txt = action.get("text", "")
        if apply and pyautogui:
            pyautogui.write(txt, interval=0.02)
            return f"typed: {txt!r}"
        return f"(sim) type: {txt!r}"

    if t == "press":
        key = action.get("key", "enter")
        if apply and pyautogui:
            pyautogui.press(key)
            return f"pressed: {key}"
        return f"(sim) press: {key}"

    if t == "hotkey":
        keys = action.get("keys", [])
        if apply and pyautogui and isinstance(keys, list):
            pyautogui.hotkey(*keys)
            return f"hotkey: {'+'.join(keys)}"
        return f"(sim) hotkey: {keys}"

    if t == "done":
        return "DONE"

    return f"Unknown action type: {t}"


def run_task(task: str, apply: bool, approve_each: bool, max_steps: int = 20):
    print(f"Task: {task}\n")
    # persist incoming task to memory (best-effort)
    try:
        if get_memory is not None:
            get_memory().add('task', task, metadata={'source': 'samus_agent'})
    except Exception:
        pass

    actions = plan_with_openai(task)
    # persist produced plan
    try:
        if get_memory is not None:
            get_memory().add('plan', json.dumps(actions), metadata={'task': task})
    except Exception:
        pass

    if not actions:
        print("No actions produced by planner.")
        return

    step = 0
    for action in actions:
        step += 1
        if step > max_steps:
            print("Max steps reached")
            break
        print(f"> action {step}: {json.dumps(action)}")
        if approve_each:
            ans = input("Approve this action? (y/N) ").strip().lower()
            # persist approval decision (best-effort)
            try:
                if get_memory is not None:
                    get_memory().add('approval', ans, metadata={'task': task, 'action': action, 'step': step})
            except Exception:
                pass
            if ans not in ("y", "yes"):
                print("Skipped")
                continue
        result = execute_action(action, apply=apply)
        print("  →", result)
        # record action result to memory (best-effort)
        try:
            if get_memory is not None:
                get_memory().add('action', result, metadata={'task': task, 'action': action, 'step': step, 'applied': apply})
        except Exception:
            pass
        if result == "DONE":
            try:
                if get_memory is not None:
                    get_memory().add('task_result', 'done', metadata={'task': task})
            except Exception:
                pass
            print("Task complete")
            break


def main():
    ap = argparse.ArgumentParser(prog="samus-agent", description="Samus‑Manus MVP (safe)")
    # startup restore: load memory + speak a summary when present (enabled by default)
    ap.add_argument('--restore', dest='restore', action='store_true', help='Load memory and speak a startup summary (default)')
    ap.add_argument('--no-restore', dest='restore', action='store_false', help='Do not run startup restore')
    ap.set_defaults(restore=True)
    ap.add_argument('--rebuild-embeddings', action='store_true', help='Rebuild missing embeddings on startup (requires OPENAI_API_KEY)')
    sub = ap.add_subparsers(dest="cmd", required=True)

    runp = sub.add_parser("run", help="Plan and run a task")
    runp.add_argument("task", help="Natural language task", nargs="+")
    runp.add_argument("--apply", action="store_true", help="Execute real actions (requires pyautogui)")
    runp.add_argument("--no-approve", dest="approve", action="store_false", help="Don't ask before each action")
    runp.add_argument("--max-steps", type=int, default=20)
    runp.set_defaults(func=lambda args: run_task(" ".join(args.task), args.apply, args.approve, args.max_steps))

    args = ap.parse_args()

    # perform optional startup restore (best-effort)
    if getattr(args, 'restore', False):
        try:
            from samus_manus_mvp.startup_restore import restore_and_speak
        except Exception:
            try:
                from startup_restore import restore_and_speak
            except Exception:
                restore_and_speak = None
        if restore_and_speak:
            try:
                restore_and_speak(rebuild_embeddings=getattr(args, 'rebuild_embeddings', False))
            except Exception:
                pass

    args.func(args)


if __name__ == "__main__":
    main()