"""
Samus-Manus: Desktop automation powered by AI vision (Gemini version)
"""

import pyautogui
import base64
import io
import time
import json
import re
import os
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Safety: allow user to abort by moving mouse to corner
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5  # Add small delay between actions


def capture_screenshot() -> bytes:
    """Capture the screen and return as bytes."""
    screenshot = pyautogui.screenshot()
    buffer = io.BytesIO()
    screenshot.save(buffer, format="PNG")
    return buffer.getvalue()


def execute_action(action: dict) -> str:
    """Execute a single action from the AI."""
    action_type = action.get("type")
    
    if action_type == "click":
        x, y = action.get("x"), action.get("y")
        button = action.get("button", "left")
        pyautogui.click(x, y, button=button)
        return f"Clicked at ({x}, {y}) with {button} button"
    
    elif action_type == "double_click":
        x, y = action.get("x"), action.get("y")
        pyautogui.doubleClick(x, y)
        return f"Double-clicked at ({x}, {y})"
    
    elif action_type == "type":
        text = action.get("text", "")
        pyautogui.write(text, interval=0.02)
        return f"Typed: {text}"
    
    elif action_type == "press":
        key = action.get("key", "")
        pyautogui.press(key)
        return f"Pressed key: {key}"
    
    elif action_type == "hotkey":
        keys = action.get("keys", [])
        pyautogui.hotkey(*keys)
        return f"Pressed hotkey: {'+'.join(keys)}"
    
    elif action_type == "scroll":
        amount = action.get("amount", 0)
        pyautogui.scroll(amount)
        return f"Scrolled: {amount}"
    
    elif action_type == "move":
        x, y = action.get("x"), action.get("y")
        pyautogui.moveTo(x, y)
        return f"Moved mouse to ({x}, {y})"
    
    elif action_type == "wait":
        seconds = action.get("seconds", 1)
        time.sleep(seconds)
        return f"Waited {seconds} seconds"
    
    elif action_type == "done":
        return "DONE"
    
    else:
        return f"Unknown action type: {action_type}"


def parse_actions(response_text: str) -> list[dict]:
    """Parse AI response to extract actions."""
    # Look for JSON array in code block
    json_match = re.search(r'```(?:json)?\s*(\[[\s\S]*?\])\s*```', response_text)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Look for JSON array without code block
    json_match = re.search(r'\[[\s\S]*?\]', response_text)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
    
    # Try to find individual action objects
    actions = []
    for match in re.finditer(r'\{[^{}]+\}', response_text):
        try:
            action = json.loads(match.group())
            if "type" in action:
                actions.append(action)
        except json.JSONDecodeError:
            continue
    
    return actions


class SamusManus:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment. Create a .env file with your API key.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        self.chat = None
        
        self.system_prompt = """You are Samus-Manus, an AI that controls a computer through mouse and keyboard.

You will receive screenshots and instructions. Respond with actions to accomplish the task.

Available actions (respond with JSON array):
- {"type": "click", "x": 100, "y": 200, "button": "left"}  (button: "left", "right", "middle")
- {"type": "double_click", "x": 100, "y": 200}
- {"type": "type", "text": "hello world"}
- {"type": "press", "key": "enter"}  (keys: enter, tab, escape, etc.)
- {"type": "hotkey", "keys": ["ctrl", "c"]}
- {"type": "scroll", "amount": -3}  (negative = down, positive = up)
- {"type": "move", "x": 100, "y": 200}
- {"type": "wait", "seconds": 2}
- {"type": "done"}  (when task is complete)

Rules:
1. Look at the screenshot carefully to identify UI elements
2. Provide precise x,y coordinates for clicks based on what you see
3. Break complex tasks into simple steps (1-3 actions at a time)
4. Use "done" when the task is complete
5. If unsure, describe what you see and ask for clarification

Respond with:
1. Brief explanation of what you're doing
2. JSON array of actions (in a code block)"""

    def run(self, task: str, max_steps: int = 20):
        """Run the automation loop for a given task."""
        print(f"\n🤖 Samus-Manus activated")
        print(f"📋 Task: {task}")
        print(f"⚠️  Move mouse to corner to abort\n")
        
        # Start new chat
        self.chat = self.model.start_chat(history=[])
        
        for step in range(max_steps):
            print(f"--- Step {step + 1} ---")
            
            # Capture screenshot
            print("📸 Capturing screenshot...")
            screenshot_bytes = capture_screenshot()
            
            # Create image part
            image_part = {
                'mime_type': 'image/png',
                'data': screenshot_bytes
            }
            
            # Build prompt
            prompt = f"{self.system_prompt}\n\nTask: {task}\n\nWhat should I do next? Provide actions as JSON."
            
            # Get AI response
            print("🧠 Thinking...")
            try:
                response = self.chat.send_message([prompt, image_part])
                assistant_message = response.text
                
                print(f"💭 {assistant_message[:300]}...")
                
                # Parse and execute actions
                actions = parse_actions(assistant_message)
                
                if not actions:
                    print("⚠️  No actions found in response. AI might be asking for clarification.")
                    print(f"Full response: {assistant_message}")
                    
                    # Ask user for input
                    user_input = input("\n📝 Your response (or 'skip' to continue, 'quit' to exit): ").strip()
                    if user_input.lower() == 'quit':
                        print("👋 Aborted by user")
                        return False
                    elif user_input.lower() == 'skip':
                        continue
                    else:
                        # Send user response
                        self.chat.send_message(user_input)
                        continue
                
                for action in actions:
                    print(f"⚡ Executing: {action}")
                    result = execute_action(action)
                    print(f"   → {result}")
                    
                    if result == "DONE":
                        print("\n✅ Task completed!")
                        return True
                    
                    time.sleep(0.3)  # Brief pause between actions
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                return False
        
        print("\n⏰ Max steps reached")
        return False


def main():
    print("""
    ╔═══════════════════════════════════════╗
    ║       🎮 SAMUS-MANUS 🤖               ║
    ║   Desktop Automation via AI Vision    ║
    ║          (Gemini Edition)             ║
    ╚═══════════════════════════════════════╝
    """)
    
    # Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ Error: GOOGLE_API_KEY not found")
        print("Create a .env file with: GOOGLE_API_KEY=your_key_here")
        return
    
    manus = SamusManus()
    
    while True:
        task = input("\n📝 Enter task (or 'quit' to exit): ").strip()
        
        if task.lower() in ('quit', 'exit', 'q'):
            print("👋 Goodbye!")
            break
        
        if task:
            try:
                manus.run(task)
            except KeyboardInterrupt:
                print("\n⏸️  Interrupted by user")
            except Exception as e:
                print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
