"""
Prueba mínima y aislada del buzzer activo-bajo (I/O -> GPIO27 / pin físico 13).
Correr en la Raspberry Pi con: python3 test_buzzer_rapido.py
"""
import RPi.GPIO as GPIO
import time

PIN = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.OUT, initial=GPIO.HIGH)  # HIGH = apagado en este módulo

print("Buzzer debería sonar 1 segundo...")
GPIO.output(PIN, GPIO.LOW)   # LOW = encendido
time.sleep(1)
GPIO.output(PIN, GPIO.HIGH)  # HIGH = apagado
print("Listo, debería haberse apagado.")

GPIO.cleanup()
