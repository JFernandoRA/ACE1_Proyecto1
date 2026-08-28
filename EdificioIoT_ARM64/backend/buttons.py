"""
buttons.py
Lectura de los 4 botones físicos del panel de control, por INTERRUPCIÓN.

NOTA TÉCNICA: usamos la librería 'gpiozero' en vez de 'RPi.GPIO' para esto
específicamente. En Raspberry Pi OS reciente (Bookworm), RPi.GPIO no puede
hacer detección de eventos de forma confiable (falla con "Failed to add
edge detection" incluso con permisos de root) — es una incompatibilidad
conocida con el kernel nuevo. gpiozero sí funciona bien porque usa un
backend moderno (lgpio) por debajo. El resto del proyecto (LEDs, servo,
sensores) puede seguir usando RPi.GPIO sin problema; ambas librerías
conviven bien siempre que controlen pines distintos.

Conexión de CADA botón (idéntica para los 4):
    Un extremo del botón -> GPIO correspondiente (ver config.PINS)
    Otro extremo del botón -> GND

gpiozero usa pull-up interno por default, así que NO necesitas resistencias
externas. En reposo el pin lee HIGH; al presionar el botón se conecta a
GND, y gpiozero dispara automáticamente el evento "presionado".

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

_BOUNCE_SEG = 0.25  # tiempo mínimo entre pulsaciones válidas (anti-rebote)

# Guardamos los objetos Button aquí para que no los recoja el garbage
# collector (si se pierden, dejan de detectar pulsaciones sin avisar).
_botones_gpiozero = {}


def conectar(callback):
    """
    Registra los 4 botones para que, al presionarse, se llame
    callback(nombre_del_boton) automáticamente, sin necesidad de sondearlos
    desde el loop principal.
    """
    if config.USE_SIMULATION:
        logger.info("Botones en modo simulación (no hay hardware que leer)")
        return

    from gpiozero import Button

    for nombre in _BOTONES:
        pin = config.PINS[nombre]
        try:
            boton = Button(pin, pull_up=True, bounce_time=_BOUNCE_SEG)

            def _handler(nombre=nombre):
                logger.info("Botón presionado: %s", nombre)
                callback(nombre)

            boton.when_pressed = _handler
            _botones_gpiozero[nombre] = boton
        except Exception as e:
            logger.error(
                "No se pudo registrar el botón %s (GPIO%s): %s", nombre, pin, e
            )

    logger.info("Botones registrados por interrupción (gpiozero): %s", _BOTONES)
