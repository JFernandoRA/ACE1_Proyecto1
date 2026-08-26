"""
Prueba mínima y aislada de los 4 botones, sin sensores ni actuadores.
Correr en la Raspberry Pi con: python3 test_botones_rapido.py
Presiona cada botón y deberías ver un mensaje al instante. Ctrl+C para salir.
"""
import time
import buttons


def cuando_presionan(nombre):
    print(f">>> Detectado: {nombre}")


buttons.conectar(cuando_presionan)
print("Esperando que presiones los botones (Ctrl+C para salir)...")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nSaliendo.")
