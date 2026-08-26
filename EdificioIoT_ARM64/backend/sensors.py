"""
sensors.py
Lectura de sensores del edificio inteligente.

Cuando config.USE_SIMULATION = True, genera valores aleatorios realistas
para poder desarrollar y probar todo el sistema sin hardware conectado.

Cuando config.USE_SIMULATION = False, usa hardware real:
  - Temperatura/Humedad (DHT11/DHT22): directo en un GPIO de la Raspberry Pi.
  - Distancia (HC-SR04): directo en dos GPIO de la Raspberry Pi.
  - Gas (MQ-2) y Luz (LDR): NO se leen desde la Pi (no tiene entradas
    analógicas). Se leen desde arduino_bridge.py, que recibe los valores
    de un Arduino Uno conectado por USB.
"""

import random
import logging

import config

logger = logging.getLogger("sensors")

if not config.USE_SIMULATION:
    # Importaciones reales, solo se cargan si NO estamos en modo simulación
    # para que el código corra en tu laptop sin necesitar estas librerías.
    import RPi.GPIO as GPIO
    import adafruit_dht
    import board
    import arduino_bridge

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(config.PINS["hcsr04_trigger"], GPIO.OUT)
    GPIO.setup(config.PINS["hcsr04_echo"], GPIO.IN)

    # adafruit_dht necesita el pin como objeto "board.Dxx", no como número BCM.
    # board.D4 == BCM 4 (ajusta si cambias config.PINS["dht"]).
    _dht_device = adafruit_dht.DHT11(board.D4, use_pulseio=False)


# ---------------------------------------------------------------------------
# Temperatura y Humedad (DHT11 / DHT22)
# ---------------------------------------------------------------------------
def leer_temperatura_humedad():
    if config.USE_SIMULATION:
        temperatura = round(random.uniform(20.0, 35.0), 1)
        humedad = round(random.uniform(25.0, 75.0), 1)
        return temperatura, humedad

    try:
        temperatura = _dht_device.temperature
        humedad = _dht_device.humidity
        if temperatura is None or humedad is None:
            logger.warning("Lectura del DHT vino vacía, se reintentará luego")
            return None, None
        return round(temperatura, 1), round(humedad, 1)
    except RuntimeError as e:
        # El DHT falla una lectura de vez en cuando, es normal, no truena el programa.
        logger.debug("Lectura fallida del DHT (normal ocasionalmente): %s", e)
        return None, None


# ---------------------------------------------------------------------------
# Gas / Humo (MQ-2) -- vía Arduino
# ---------------------------------------------------------------------------
def leer_gas():
    if config.USE_SIMULATION:
        # La mayoría del tiempo valores normales, ocasionalmente un pico
        if random.random() < 0.05:
            return random.randint(400, 700)  # simula evento de emergencia
        return random.randint(50, 250)

    if not arduino_bridge.datos_frescos():
        logger.warning(
            "No hay datos recientes del Arduino (gas). "
            "Revisa el cable USB / que el sketch esté corriendo."
        )
    return arduino_bridge.get_gas()


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

    start = time.time()
    stop = time.time()

    timeout = time.time() + 0.04
    while GPIO.input(echo) == 0 and time.time() < timeout:
        start = time.time()
    timeout = time.time() + 0.04
    while GPIO.input(echo) == 1 and time.time() < timeout:
        stop = time.time()

    elapsed = stop - start
    if elapsed <= 0:
        logger.warning("Timeout leyendo HC-SR04")
        return None

    distancia_cm = (elapsed * 34300) / 2
    if distancia_cm > 400 or distancia_cm < 0:
        # Fuera del rango físico real del HC-SR04, descartar lectura
        return None
    return round(distancia_cm, 1)


# ---------------------------------------------------------------------------
# Nivel de luz (LDR) -- vía Arduino
# ---------------------------------------------------------------------------
def leer_luz():
    if config.USE_SIMULATION:
        return random.randint(0, 1023)

    if not arduino_bridge.datos_frescos():
        logger.warning(
            "No hay datos recientes del Arduino (luz). "
            "Revisa el cable USB / que el sketch esté corriendo."
        )
    return arduino_bridge.get_luz()


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
