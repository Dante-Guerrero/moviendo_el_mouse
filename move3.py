import pyautogui
import time

# posición a la que quieres mover el mouse
x = 416.51171875
y = 99.18359375

print(f"Moviendo el mouse a ({x}, {y}) en 2 segundos...")
time.sleep(2)  # pequeña espera para que veas el movimiento

# mueve el mouse con una animación de 1 segundo
pyautogui.moveTo(x, y, duration=1)

# hace clic izquierdo
pyautogui.click()

print("Click realizado.")

pyautogui.keyDown('option')
pyautogui.press('3')   # en muchos layouts AltGr+3 es #
pyautogui.keyUp('option')

texto = " Esto es un comentario"

# escribe el texto como si fueras tú
pyautogui.write(texto, interval=0.05)  # interval controla la velocidad

print("Texto escrito.")

# presiona Enter
pyautogui.press("enter")