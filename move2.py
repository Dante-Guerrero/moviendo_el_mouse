from pynput import mouse

def on_click(x, y, button, pressed):
    if pressed:  # solo cuando haces click (no cuando sueltas)
        print(f"Click detectado en: X={x}, Y={y}")

# iniciar el listener
with mouse.Listener(on_click=on_click) as listener:
    print("Escuchando clics... (Ctrl+C para salir)")
    listener.join()