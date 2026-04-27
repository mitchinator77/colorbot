import json
import time
import pyautogui

print("Simple action recorder")
print("Commands:")
print("  c = record click at current mouse position")
print("  d = record double click at current mouse position")
print("  r = record right click at current mouse position")
print("  w = record wait")
print("  p = record key press")
print("  h = record hotkey")
print("  t = record typed text")
print("  q = finish")

script = []
while True:
    cmd = input("Action command: ").strip().lower()

    if cmd == "q":
        break
    elif cmd == "c":
        x, y = pyautogui.position()
        script.append({"type": "click", "x": x, "y": y})
        print("Added click", x, y)
    elif cmd == "d":
        x, y = pyautogui.position()
        script.append({"type": "double_click", "x": x, "y": y})
        print("Added double_click", x, y)
    elif cmd == "r":
        x, y = pyautogui.position()
        script.append({"type": "right_click", "x": x, "y": y})
        print("Added right_click", x, y)
    elif cmd == "w":
        seconds = float(input("Seconds: ").strip())
        script.append({"type": "wait", "seconds": seconds})
        print("Added wait", seconds)
    elif cmd == "p":
        key = input("Key name, e.g. enter, tab, esc: ").strip()
        script.append({"type": "press", "key": key})
        print("Added press", key)
    elif cmd == "h":
        keys = input("Keys separated by +, e.g. ctrl+s: ").strip().split("+")
        script.append({"type": "hotkey", "keys": [k.strip() for k in keys if k.strip()]})
        print("Added hotkey", keys)
    elif cmd == "t":
        text = input("Text to type: ")
        script.append({"type": "type", "text": text, "interval": 0.01})
        print("Added type")
    else:
        print("Unknown command")

print("\nActions JSON:")
print(json.dumps(script, indent=2))
