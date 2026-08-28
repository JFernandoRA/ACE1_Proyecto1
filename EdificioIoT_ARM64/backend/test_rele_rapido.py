"""
test_rele_rapido.py
Prueba aislada del relé JQC3-05VDC-C (IN -> GPIO25 / pin físico 22) para
confirmar, solo mirando y escuchando, si tu módulo es activo-bajo o
activo-alto.

Cómo usarlo:
  1. Conecta SOLO el relé: VCC->5V, GND->GND, IN->GPIO25. No hace falta
     tener el ventilador conectado todavía.
  2. Corre: python3 test_rele_rapido.py
  3. Observa el LED que trae la placa del relé (se prende cuando la bobina
     está energizada) y escucha el "clic" mecánico del contacto.

Correr en la Raspberry Pi.
"""
import RPi.GPIO as GPIO
import time

PIN = 25

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.OUT, initial=GPIO.HIGH)

input("Presiona Enter para poner el pin en LOW...")
GPIO.output(PIN, GPIO.LOW)
print(">>> Pin en LOW. ¿Se prendió el LED del relé / hizo clic? (mira/escucha ahora)")
time.sleep(4)

input("\nPresiona Enter para poner el pin en HIGH...")
GPIO.output(PIN, GPIO.HIGH)
print(">>> Pin en HIGH. ¿Se prendió el LED del relé / hizo clic? (mira/escucha ahora)")
time.sleep(4)

GPIO.cleanup()
print("\nSi el relé se activó (LED prendido / clic) durante el LOW:")
print("  -> Es activo-bajo. Ya está configurado así por default, no cambies nada.")
print("Si se activó durante el HIGH:")
print("  -> Es activo-alto. Pon esto en tu .env: RELE_VENTILADOR_ACTIVE_LOW=False")
