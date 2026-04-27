import time
import pyautogui

print("Move mouse over the target pixel. Sampling in 3 seconds...")
time.sleep(3)
x, y = pyautogui.position()
img = pyautogui.screenshot()
rgb = img.getpixel((x, y))[:3]
print("Position:", {"x": x, "y": y})
print("RGB:", list(rgb))
