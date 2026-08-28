"""
hardware_test.py

Objetivo de este script: probar que la Raspberry Pi, los sensores y los
actuadores se están comunicando y funcionando bien juntos, ANTES de meter
MQTT, MongoDB y el dashboard a la ecuación.

Qué hace:
  1. Conecta el Arduino (gas/luz), el LCD y los botones.
  2. En loop: lee todos los sensores, decide qué deben hacer los actuadores
     según los umbrales de config.py, actualiza el LCD de forma rotativa,
     revisa los botones físicos, e imprime todo en consola.

Cómo correrlo en la Raspberry Pi:
  1. En tu archivo .env pon:  USE_SIMULATION=False
  2. Conecta el Arduino por USB y verifica el puerto con: ls /dev/tty*
     (usualmente es /dev/ttyACM0, ajústalo en .env con ARDUINO_SERIAL_PORT)
  3. Activa el I2C y el bus 1-wire si hace falta con: sudo raspi-config
  4. pip install -r requirements.txt
  5. python3 hardware_test.py

Si algo no conecta (Arduino, LCD), el script no truena: avisa por consola
y sigue funcionando con lo que sí tenga disponible, para que puedas ir
resolviendo cable por cable.
"""

import logging
import time

import config
import sensors
import actuators
import state_manager
import lcd
import buttons

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("hardware_test")

# Pantallas rotativas del LCD (una se muestra por ciclo)
_PANTALLA_ACTUAL = 0
_NUM_PANTALLAS = 6


def actualizar_lcd(lecturas, estado_puerta, estado_global):
    global _PANTALLA_ACTUAL
    pantalla = _PANTALLA_ACTUAL % _NUM_PANTALLAS

    if pantalla == 0:
        lcd.pantalla_temp_humedad(lecturas["temperatura"], lecturas["humedad"])
    elif pantalla == 1:
        lcd.pantalla_gas(lecturas["gas"])
    elif pantalla == 2:
        lcd.pantalla_distancia(lecturas["distancia"])
    elif pantalla == 3:
        lcd.pantalla_luz(lecturas["luz"])
    elif pantalla == 4:
        lcd.pantalla_puerta(estado_puerta)
    elif pantalla == 5:
        lcd.pantalla_estado_global(estado_global)

    _PANTALLA_ACTUAL += 1


def aplicar_logica_automatica(lecturas, estado):
    """Aplica las reglas obligatorias del proyecto sobre los actuadores."""

    # --- Ventilación: se enciende si el estado global es ADVERTENCIA o
    #     EMERGENCIA (sin importar qué sensor haya disparado ese estado),
    #     y se apaga cuando el edificio vuelve a NORMAL.
    actuators.set_ventilador(estado in ("ADVERTENCIA", "EMERGENCIA"))

    # --- Iluminación según luz ambiental (solo si modo AUTOMATICO) ---
    if actuators.estado_actuadores["modo_iluminacion"] == "AUTOMATICO":
        luz = lecturas["luz"]
        if luz is not None:
            actuators.set_luces(luz < config.THRESHOLDS["luz_baja"])

    # --- Puerta según distancia ---
    dist = lecturas["distancia"]
    if dist is not None and dist < config.THRESHOLDS["distancia_apertura"]:
        if actuators.estado_actuadores["puerta"] == "CERRADA":
            actuators.abrir_puerta()
            time.sleep(config.PUERTA_TIEMPO_ABIERTA)
            actuators.cerrar_puerta()

    # --- Gas / emergencia ---
    gas = lecturas["gas"]
    if gas is not None and gas > config.THRESHOLDS["gas_max"]:
        actuators.activar_alarma()
        if actuators.estado_actuadores["puerta"] == "CERRADA":
            actuators.abrir_puerta()  # simula evacuación, no se auto-cierra
    elif estado != "EMERGENCIA":
        actuators.silenciar_alarma()

    # --- LEDs de estado global ---
    actuators.set_leds_estado(estado)


def manejar_boton(boton):
    """
    Callback llamado por interrupción (ver buttons.py) en el instante mismo
    en que se presiona el botón, sin esperar al loop de sensores.
    """
    if boton == "boton_puerta":
        if actuators.estado_actuadores["puerta"] == "CERRADA":
            actuators.abrir_puerta()
        else:
            actuators.cerrar_puerta()
    elif boton == "boton_modo_luz":
        actual = actuators.estado_actuadores["modo_iluminacion"]
        nuevo = "MANUAL" if actual == "AUTOMATICO" else "AUTOMATICO"
        actuators.set_modo_iluminacion(nuevo)
        logger.info("Modo de iluminación -> %s", nuevo)
    elif boton == "boton_silenciar":
        actuators.silenciar_alarma()
    elif boton == "boton_reset_alerta":
        state_manager.resetear_alerta()


def main():
    logger.info("Modo simulación: %s", config.USE_SIMULATION)

    if not config.USE_SIMULATION:
        import arduino_bridge

        arduino_bridge.conectar()

    buttons.conectar(manejar_boton)
    lcd.conectar()

    logger.info("Iniciando loop de prueba de hardware (Ctrl+C para salir)")

    try:
        while True:
            lecturas = sensors.leer_todos_los_sensores()
            estado = state_manager.calcular_estado(lecturas)

            logger.info(
                "Temp=%s Hum=%s Gas=%s Dist=%s Luz=%s -> Estado=%s",
                lecturas["temperatura"],
                lecturas["humedad"],
                lecturas["gas"],
                lecturas["distancia"],
                lecturas["luz"],
                estado,
            )

            aplicar_logica_automatica(lecturas, estado)
            actualizar_lcd(
                lecturas, actuators.estado_actuadores["puerta"], estado
            )

            time.sleep(config.INTERVALO_LECTURA)

    except KeyboardInterrupt:
        logger.info("Deteniendo...")
    finally:
        if not config.USE_SIMULATION:
            import arduino_bridge

            arduino_bridge.desconectar()


if __name__ == "__main__":
    main()
