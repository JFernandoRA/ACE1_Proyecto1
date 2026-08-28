"""
Prueba aislada y directa del DHT11 (DATA -> GPIO4 / pin físico 7).
Correr en la Raspberry Pi con: python3 test_dht_rapido.py

IMPORTANTE mientras corre: sopla aire tibio sobre el sensor, o cúbrelo con
la mano un rato, y mira si el número cambia. Si NO cambia ni un poco pase
lo que pase, el sensor está atascado o mal conectado, no es lectura real.
"""
import time
import board
import adafruit_dht

dht = adafruit_dht.DHT11(board.D4, use_pulseio=False)

print("Ctrl+C para salir. Prueba soplar aire tibio sobre el sensor...")
for i in range(20):
    try:
        temp = dht.temperature
        hum = dht.humidity
        print(f"Lectura {i+1}: Temp={temp}C  Hum={hum}%")
    except RuntimeError as e:
        print(f"Lectura {i+1}: FALLÓ ({e})")
    time.sleep(2.5)  # dejar más tiempo del mínimo que pide el DHT11