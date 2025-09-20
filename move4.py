import pyautogui
import time

time.sleep(2)  # te da un par de segundos para cambiarte de ventana

# abre Spotlight (Command + Space)
pyautogui.hotkey("command", "space")

time.sleep(0.5)  # medio segundo para que aparezca Spotlight

# escribe el nombre de la aplicación
pyautogui.write("TextEdit", interval=0.05)

time.sleep(0.3)

# presiona Enter para abrirla
pyautogui.press("enter")

print("Aplicación lanzada.")