import time
import pyautogui

print("Move mouse to TOP-LEFT corner of region. Capturing in 3 seconds...")
time.sleep(3)
x1, y1 = pyautogui.position()
print("Top-left:", x1, y1)

print("Move mouse to BOTTOM-RIGHT corner of region. Capturing in 3 seconds...")
time.sleep(3)
x2, y2 = pyautogui.position()
print("Bottom-right:", x2, y2)

left = min(x1, x2)
top = min(y1, y2)
width = abs(x2 - x1)
height = abs(y2 - y1)

print("Region JSON:")
print({"left": left, "top": top, "width": width, "height": height})
