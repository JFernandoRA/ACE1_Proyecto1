"""
Prueba mínima y aislada del buzzer con el circuito de transistor
(GPIO27 -> resistencia 100 ohm -> base del transistor).
Correr en la Raspberry Pi con: python3 test_buzzer_rapido.py

Con este circuito la lógica es normal: HIGH = suena, LOW = silencio.
"""
import RPi.GPIO as GPIO
import time

PIN = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.OUT, initial=GPIO.LOW)  # LOW = apagado

print("Buzzer debería sonar 1 segundo...")
GPIO.output(PIN, GPIO.HIGH)  # HIGH = encendido
time.sleep(1)
GPIO.output(PIN, GPIO.LOW)   # LOW = apagado
print("Listo, debería haberse apagado.")

GPIO.cleanup()
