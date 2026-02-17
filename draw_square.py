import pyautogui
import time

print("Preparing to draw a square. Please switch to your drawing application now.")
time.sleep(5) # Give the user 5 seconds to switch to a drawing application

distance = 200

# Move to a starting point (relative to current mouse position)
pyautogui.moveRel(50, 50, duration=0.1) # Move a bit to ensure clean start

# Draw a square
pyautogui.dragRel(distance, 0, duration=0.2)   # Move right
pyautogui.dragRel(0, distance, duration=0.2)   # Move down
pyautogui.dragRel(-distance, 0, duration=0.2)  # Move left
pyautogui.dragRel(0, -distance, duration=0.2)  # Move up

print("Square drawing complete.")