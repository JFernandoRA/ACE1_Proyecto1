"""
buttons.py
Lectura de los 4 botones físicos del panel de control.

Conexión de CADA botón (idéntica para los 4):
    Un extremo del botón -> GPIO correspondiente (ver config.PINS)
    Otro extremo del botón -> GND

Usamos la resistencia pull-up interna de la Raspberry Pi (PUD_UP), así que
NO necesitas resistencias externas. En reposo el pin lee HIGH (1); al
presionar el botón se conecta a GND y el pin lee LOW (0).

Botones:
    boton_puerta        -> abrir/cerrar puerta manualmente
    boton_modo_luz       -> alternar modo AUTOMATICO/MANUAL de iluminación
    boton_silenciar      -> silenciar el buzzer
    boton_reset_alerta   -> resetear la alerta cuando ya no hay peligro
"""

import logging
import time

import config

logger = logging.getLogger("buttons")

_BOTONES = [
    "boton_puerta",
    "boton_modo_luz",
    "boton_silenciar",
    "boton_reset_alerta",
]

# Para hacer debounce por software: guardamos el último estado leído
# y el momento del último cambio válido de cada botón.
_ultimo_estado = {b: 1 for b in _BOTONES}
_ultimo_cambio = {b: 0.0 for b in _BOTONES}
_DEBOUNCE_SEG = 0.2


def conectar():
    if config.USE_SIMULATION:
        logger.info("Botones en modo simulación (no hay hardware que leer)")
        return

    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    for nombre in _BOTONES:
        GPIO.setup(config.PINS[nombre], GPIO.IN, pull_up_down=GPIO.PUD_UP)


def leer_botones_presionados() -> list:
    """
    Revisa los 4 botones y devuelve una lista con los nombres de los que
    se acaban de presionar en este instante (con debounce aplicado).
    Debe llamarse periódicamente dentro del loop principal.
    """
    if config.USE_SIMULATION:
        return []

    import RPi.GPIO as GPIO

    presionados = []
    ahora = time.time()

    for nombre in _BOTONES:
        pin = config.PINS[nombre]
        estado = GPIO.input(pin)  # 1 = suelto, 0 = presionado (pull-up)

        if estado == 0 and _ultimo_estado[nombre] == 1:
            # Flanco de bajada: posible pulsación
            if ahora - _ultimo_cambio[nombre] > _DEBOUNCE_SEG:
                presionados.append(nombre)
                _ultimo_cambio[nombre] = ahora

        _ultimo_estado[nombre] = estado

    return presionados
