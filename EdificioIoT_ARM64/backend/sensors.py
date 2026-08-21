"""
sensors.py
Lectura de sensores del edificio inteligente.

Cuando config.USE_SIMULATION = True, genera valores aleatorios realistas
para poder desarrollar y probar todo el sistema sin hardware conectado.

Cuando config.USE_SIMULATION = False, usa las librerías reales de GPIO.
Aquí se dejan marcados con TODO los puntos donde cada quien debe conectar
su sensor real, según el hardware que usen (DHT11/22, MQ-2/135, HC-SR04, LDR).
"""

import random
import logging

import config

logger = logging.getLogger("sensors")

if not config.USE_SIMULATION:
    # Importaciones reales, solo se cargan si NO estamos en modo simulación
    # para que el código corra en tu laptop sin necesitar estas librerías.
    import Adafruit_DHT           # pip install Adafruit_DHT (o adafruit-circuitpython-dht)
    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(config.PINS["hcsr04_trigger"], GPIO.OUT)
    GPIO.setup(config.PINS["hcsr04_echo"], GPIO.IN)
    # TODO: setup de MQ-2/MQ-135 y LDR según si usan salida digital o un ADC (MCP3008, ADS1115, etc.)


# ---------------------------------------------------------------------------
# Temperatura y Humedad (DHT11 / DHT22)
# ---------------------------------------------------------------------------
def leer_temperatura_humedad():
    if config.USE_SIMULATION:
        temperatura = round(random.uniform(20.0, 35.0), 1)
        humedad = round(random.uniform(25.0, 75.0), 1)
        return temperatura, humedad

    # TODO: reemplazar Adafruit_DHT.DHT22 por DHT11 si ese es tu sensor
    humedad, temperatura = Adafruit_DHT.read_retry(
        Adafruit_DHT.DHT22, config.PINS["dht"]
    )
    if humedad is None or temperatura is None:
        logger.warning("No se pudo leer el sensor DHT")
        return None, None
    return round(temperatura, 1), round(humedad, 1)


# ---------------------------------------------------------------------------
# Gas / Humo (MQ-2 / MQ-135)
# ---------------------------------------------------------------------------
def leer_gas():
    if config.USE_SIMULATION:
        # La mayoría del tiempo valores normales, ocasionalmente un pico
        if random.random() < 0.05:
            return random.randint(400, 700)  # simula evento de emergencia
        return random.randint(50, 250)

    # TODO: leer valor analógico real (vía ADC) o digital (GPIO.input) del MQ-2/MQ-135
    raise NotImplementedError("Conectar lectura real del sensor de gas aquí")


# ---------------------------------------------------------------------------
# Distancia (HC-SR04)
# ---------------------------------------------------------------------------
def leer_distancia():
    if config.USE_SIMULATION:
        return round(random.uniform(5.0, 200.0), 1)

    import time
    trigger = config.PINS["hcsr04_trigger"]
    echo = config.PINS["hcsr04_echo"]

    GPIO.output(trigger, False)
    time.sleep(0.05)
    GPIO.output(trigger, True)
    time.sleep(0.00001)
    GPIO.output(trigger, False)

    timeout = time.time() + 0.04
    while GPIO.input(echo) == 0 and time.time() < timeout:
        start = time.time()
    timeout = time.time() + 0.04
    while GPIO.input(echo) == 1 and time.time() < timeout:
        stop = time.time()

    try:
        elapsed = stop - start
        distancia_cm = (elapsed * 34300) / 2
        return round(distancia_cm, 1)
    except NameError:
        logger.warning("Timeout leyendo HC-SR04")
        return None


# ---------------------------------------------------------------------------
# Nivel de luz (LDR)
# ---------------------------------------------------------------------------
def leer_luz():
    if config.USE_SIMULATION:
        return random.randint(0, 1023)

    # TODO: leer valor analógico real del LDR (vía ADC, ej. MCP3008)
    raise NotImplementedError("Conectar lectura real del sensor LDR aquí")


def leer_todos_los_sensores() -> dict:
    """Devuelve un snapshot con todas las lecturas actuales."""
    temperatura, humedad = leer_temperatura_humedad()
    return {
        "temperatura": temperatura,
        "humedad": humedad,
        "gas": leer_gas(),
        "distancia": leer_distancia(),
        "luz": leer_luz(),
    }
