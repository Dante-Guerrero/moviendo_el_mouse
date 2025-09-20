import pyautogui
import time

print("Presiona Ctrl+C para salir.\n")

try:
    while True:
        x, y = pyautogui.position()  # obtiene coordenadas actuales
        print(f"Posición del mouse: X={x}, Y={y}", end="\r")  
        time.sleep(0.1)  # refresca cada 0.1 segundos
except KeyboardInterrupt:
    print("\nPrograma terminado.")