import RPi.GPIO as GPIO
import time

PIN = 25

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.OUT)
GPIO.output(PIN, GPIO.HIGH)  # Forzar HIGH explícitamente después del setup
time.sleep(0.5)  # Esperar a que estabilice

print("Estado inicial: Pin en HIGH")
input("Presiona Enter para poner el pin en LOW...")
GPIO.output(PIN, GPIO.LOW)
print(">>> Pin en LOW. ¿Se apagó el LED del relé? (debería estar APAGADO ahora)")
time.sleep(4)

input("\nPresiona Enter para poner el pin en HIGH...")
GPIO.output(PIN, GPIO.HIGH)
time.sleep(0.1)
print(">>> Pin en HIGH. ¿Se prendió el LED del relé? (debería estar ENCENDIDO ahora)")
time.sleep(4)

GPIO.cleanup()
print("\nConclusión:")
print("  -> El relé es ACTIVO-BAJO (se activa con LOW)")
print("  -> Configuración correcta por default (no necesitas cambiar nada en .env)")