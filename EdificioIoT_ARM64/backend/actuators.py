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
    # initial=GPIO.HIGH porque este buzzer es activo-bajo (se apaga en HIGH);
    # sin esto, el pin podría arrancar en LOW y sonar solo al iniciar el programa.
    GPIO.setup(config.PINS["buzzer"], GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(config.PINS["led_rojo"], GPIO.OUT)
    GPIO.setup(config.PINS["led_puerta"], GPIO.OUT)
    GPIO.setup(config.PINS["led_estado_verde"], GPIO.OUT)
    GPIO.setup(config.PINS["led_estado_amarillo"], GPIO.OUT)
    GPIO.setup(config.PINS["led_estado_rojo"], GPIO.OUT)
    # Estado inicial seguro: "apagado", sea cual sea la polaridad del relé.
    _rele_pin_apagado = GPIO.HIGH if config.RELE_VENTILADOR_ACTIVE_LOW else GPIO.LOW
    GPIO.setup(config.PINS["ventilador"], GPIO.OUT, initial=_rele_pin_apagado)
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
    El módulo de buzzer activo (tipo MH-FMD, marcado '低电平触发' = disparo por
    nivel bajo) enciende con el pin I/O en LOW y se apaga con HIGH. Es al
    revés de un LED normal, así que invertimos aquí para que el resto del
    código solo piense en "activo / no activo", sin preocuparse por la
    polaridad del módulo.
    """
    if config.USE_SIMULATION:
        return
    GPIO.output(config.PINS["buzzer"], GPIO.LOW if activo else GPIO.HIGH)


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
    Controla el relé del ventilador. El módulo JQC3-05VDC-C (como el buzzer)
    normalmente es activo-bajo: IN en LOW energiza la bobina y cierra el
    contacto COM-NO. Si tu módulo resulta ser al revés, cambia
    RELE_VENTILADOR_ACTIVE_LOW=False en el .env (ver test_rele_rapido.py
    para confirmar cuál es tu caso).
    """
    estado_actuadores["ventilador"] = encender
    if config.USE_SIMULATION:
        return
    if config.RELE_VENTILADOR_ACTIVE_LOW:
        GPIO.output(config.PINS["ventilador"], GPIO.LOW if encender else GPIO.HIGH)
    else:
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
