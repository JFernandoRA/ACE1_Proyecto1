"""
buttons.py
Lectura de los 4 botones físicos del panel de control, por INTERRUPCIÓN
(no por sondeo). Esto es importante: el loop principal de hardware_test.py
lee sensores cada varios segundos, y un botón presionado con la mano dura
una fracción de segundo — si solo revisáramos el estado del pin dentro de
ese loop lento, casi nunca lo alcanzaríamos a detectar. Por eso usamos
GPIO.add_event_detect, que reacciona al instante sin importar en qué esté
el loop principal.

Conexión de CADA botón (idéntica para los 4):
    Un extremo del botón -> GPIO correspondiente (ver config.PINS)
    Otro extremo del botón -> GND

Usamos la resistencia pull-up interna de la Raspberry Pi (PUD_UP), así que
NO necesitas resistencias externas. En reposo el pin lee HIGH (1); al
presionar el botón se conecta a GND y el pin lee LOW (0), lo cual es el
flanco de bajada (FALLING) que detectamos.

Botones:
    boton_puerta        -> abrir/cerrar puerta manualmente
    boton_modo_luz       -> alternar modo AUTOMATICO/MANUAL de iluminación
    boton_silenciar      -> silenciar el buzzer
    boton_reset_alerta   -> resetear la alerta cuando ya no hay peligro
"""

import logging

import config

logger = logging.getLogger("buttons")

_BOTONES = [
    "boton_puerta",
    "boton_modo_luz",
    "boton_silenciar",
    "boton_reset_alerta",
]

_BOUNCETIME_MS = 250  # tiempo mínimo entre pulsaciones válidas (anti-rebote)


def conectar(callback):
    """
    Registra los 4 botones para que, al presionarse, se llame
    callback(nombre_del_boton) automáticamente, sin necesidad de sondearlos
    desde el loop principal.
    """
    if config.USE_SIMULATION:
        logger.info("Botones en modo simulación (no hay hardware que leer)")
        return

    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    for nombre in _BOTONES:
        pin = config.PINS[nombre]
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # Usamos una función que captura "nombre" correctamente (evita el
        # clásico bug de que todos los callbacks terminen usando el último
        # valor de la variable del for).
        def _handler(channel, nombre=nombre):
            logger.info("Botón presionado: %s (GPIO%s)", nombre, channel)
            callback(nombre)

        try:
            GPIO.add_event_detect(
                pin, GPIO.FALLING, callback=_handler, bouncetime=_BOUNCETIME_MS
            )
        except RuntimeError as e:
            logger.error(
                "No se pudo registrar el evento para %s (GPIO%s): %s",
                nombre,
                pin,
                e,
            )

    logger.info("Botones registrados por interrupción: %s", _BOTONES)
