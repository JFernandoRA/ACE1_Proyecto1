"""
actuators.py
Control de actuadores: puerta (servo), luces, buzzer, ventilador y LEDs de estado.

Igual que sensors.py, funciona en modo simulación (solo imprime en consola / mantiene
estado en memoria) o en modo real usando RPi.GPIO.
"""

import logging
import config

logger = logging.getLogger("actuators")

# Estado interno (útil tanto en modo real como simulado, para exponerlo al dashboard)
estado_actuadores = {
    "puerta": "CERRADA",       # ABIERTA | CERRADA
    "luces": False,
    "modo_iluminacion": "AUTOMATICO",  # AUTOMATICO | MANUAL
    "ventilador": False,
    "alarma": False,
}

if not config.USE_SIMULATION:
    import RPi.GPIO as GPIO
    import time

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(config.PINS["servo_puerta"], GPIO.OUT)
    # Con el transistor añadido para controlar el buzzer, la lógica ya es
    # normal (HIGH = suena), así que arrancamos en LOW = silencio.
    GPIO.setup(config.PINS["buzzer"], GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(config.PINS["led_rojo"], GPIO.OUT)
    GPIO.setup(config.PINS["led_puerta"], GPIO.OUT)
    GPIO.setup(config.PINS["led_estado_verde"], GPIO.OUT)
    GPIO.setup(config.PINS["led_estado_amarillo"], GPIO.OUT)
    GPIO.setup(config.PINS["led_estado_rojo"], GPIO.OUT)
    # Estado inicial seguro: apagado (LOW), confirmado con hardware real.
    GPIO.setup(config.PINS["ventilador"], GPIO.OUT, initial=GPIO.LOW)
    for pin in config.PINS["leds_iluminacion"]:
        GPIO.setup(pin, GPIO.OUT)

    servo = GPIO.PWM(config.PINS["servo_puerta"], 50)  # 50Hz típico para SG90
    servo.start(0)


def _set_pin(pin_name, value: bool):
    if config.USE_SIMULATION:
        return
    GPIO.output(config.PINS[pin_name], GPIO.HIGH if value else GPIO.LOW)


def _set_buzzer(activo: bool):
    """
    Con el circuito de transistor (GPIO27 -> resistencia 100 ohm -> base;
    emisor -> GND; colector -> GND del módulo buzzer; I/O del módulo fijo a
    GND), el GPIO ya no habla directo con la lógica activa-baja de la
    placa: ahora solo controla si existe un camino a tierra para el módulo.
    Por eso aquí la lógica es normal: HIGH = suena, LOW = silencio.
    """
    if config.USE_SIMULATION:
        return
    GPIO.output(config.PINS["buzzer"], GPIO.HIGH if activo else GPIO.LOW)


# ---------------------------------------------------------------------------
# Puerta
# ---------------------------------------------------------------------------
def abrir_puerta():
    estado_actuadores["puerta"] = "ABIERTA"
    _set_pin("led_puerta", True)
    if not config.USE_SIMULATION:
        servo.ChangeDutyCycle(7.5)  # ~90 grados, ajustar según el servo
        time.sleep(0.5)
        servo.ChangeDutyCycle(0)
    logger.info("Puerta ABIERTA")


def cerrar_puerta():
    estado_actuadores["puerta"] = "CERRADA"
    _set_pin("led_puerta", False)
    if not config.USE_SIMULATION:
        servo.ChangeDutyCycle(2.5)  # ~0 grados
        time.sleep(0.5)
        servo.ChangeDutyCycle(0)
    logger.info("Puerta CERRADA")


# ---------------------------------------------------------------------------
# Iluminación
# ---------------------------------------------------------------------------
def set_luces(encender: bool):
    estado_actuadores["luces"] = encender
    if config.USE_SIMULATION:
        return
    for pin in config.PINS["leds_iluminacion"]:
        GPIO.output(pin, GPIO.HIGH if encender else GPIO.LOW)


def set_modo_iluminacion(modo: str):
    """modo: 'AUTOMATICO' | 'MANUAL'"""
    estado_actuadores["modo_iluminacion"] = modo


# ---------------------------------------------------------------------------
# Ventilador
# ---------------------------------------------------------------------------
def set_ventilador(encender: bool):
    """
    Controla el relé del ventilador.
    Confirmado con hardware real: HIGH = relé activado (ventilador encendido),
    LOW = relé apagado. Fijo directo en código, sin depender de ningún flag
    de .env, para no volver a toparnos con variables de entorno que no se
    estaban aplicando.
    """
    estado_actuadores["ventilador"] = encender
    if config.USE_SIMULATION:
        return
    GPIO.output(config.PINS["ventilador"], GPIO.HIGH if encender else GPIO.LOW)


# ---------------------------------------------------------------------------
# Alarma / Buzzer / LED rojo
# ---------------------------------------------------------------------------
def activar_alarma():
    estado_actuadores["alarma"] = True
    _set_buzzer(True)
    _set_pin("led_rojo", True)
    logger.warning("ALARMA ACTIVADA")


def silenciar_alarma():
    estado_actuadores["alarma"] = False
    _set_buzzer(False)
    _set_pin("led_rojo", False)
    logger.info("Alarma silenciada")


# ---------------------------------------------------------------------------
# LEDs de estado global (verde / amarillo / rojo)
# ---------------------------------------------------------------------------
def set_leds_estado(estado: str):
    """estado: 'NORMAL' | 'ADVERTENCIA' | 'EMERGENCIA'"""
    _set_pin("led_estado_verde", estado == "NORMAL")
    _set_pin("led_estado_amarillo", estado == "ADVERTENCIA")
    _set_pin("led_estado_rojo", estado == "EMERGENCIA")


def get_estado_actuadores() -> dict:
    return dict(estado_actuadores)