"""
Loop principal del sistema de Edificio Inteligente IoT.

Flujo por cada ciclo de lectura:
  1. Leer sensores (real o simulado).
  2. Publicar lecturas por MQTT.
  3. Guardar lecturas en MongoDB.
  4. Calcular estado global y actuar en consecuencia (LEDs, buzzer, puerta, etc.).
  5. Actualizar el LCD rotativo del panel físico.
  6. Cada N lecturas, disparar el flujo con el módulo ARM64.
  7. Escuchar y ejecutar comandos remotos que lleguen del dashboard.
  8. Escuchar los 4 botones físicos del panel (por interrupción).
"""

import logging
import time

import config
import db
import mqtt_client
import sensors
import actuators
import state_manager
import arm64_bridge
import lcd
import buttons

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("main")

# Buffer de temperaturas reales para alimentar al módulo ARM64
_buffer_temperaturas: list[float] = []
_puerta_abierta_desde: float | None = None

# Última lectura de sensores conocida, para que el botón físico de "reset"
# (que llega por interrupción, fuera del loop principal) pueda consultar el
# valor de gas más reciente en vez de trabajar a ciegas.
_ultimas_lecturas: dict = {}

# Pantallas rotativas del LCD (una se muestra por ciclo)
_pantalla_actual = 0
_NUM_PANTALLAS = 6


def manejar_comando_remoto(payload: dict):
    action = payload.get("action")
    logger.info("Comando remoto recibido: %s", payload)
    db.save_command("dashboard", action, payload)

    global _puerta_abierta_desde
    if action == "abrir_puerta":
        actuators.abrir_puerta()
        _puerta_abierta_desde = time.time()
    elif action == "cerrar_puerta":
        actuators.cerrar_puerta()
        _puerta_abierta_desde = None
    elif action == "toggle_luces":
        actuators.set_luces(bool(payload.get("value", True)))
    elif action == "set_modo_iluminacion":
        actuators.set_modo_iluminacion(payload.get("value", "AUTOMATICO"))
    elif action == "toggle_ventilador":
        actuators.set_ventilador(bool(payload.get("value", True)))
    elif action == "silenciar_alarma":
        actuators.silenciar_alarma()
    elif action == "resetear_alerta":
        # Le pasamos la última lectura real para que no se pueda resetear
        # si el gas sigue por encima del umbral (regla obligatoria).
        state_manager.resetear_alerta(_ultimas_lecturas)
    else:
        logger.warning("Acción de comando remoto desconocida: %s", action)

    publicar_estado_actuadores()


def manejar_boton_fisico(boton: str):
    """
    Callback registrado en buttons.conectar(). Se ejecuta por interrupción,
    en el instante mismo en que se presiona cualquiera de los 4 botones
    físicos del panel de control.
    """
    logger.info("Botón físico presionado: %s", boton)
    db.save_command("panel_fisico", boton)

    global _puerta_abierta_desde
    if boton == "boton_puerta":
        if actuators.estado_actuadores["puerta"] == "CERRADA":
            actuators.abrir_puerta()
            _puerta_abierta_desde = time.time()
        else:
            actuators.cerrar_puerta()
            _puerta_abierta_desde = None
    elif boton == "boton_modo_luz":
        actual = actuators.estado_actuadores["modo_iluminacion"]
        nuevo = "MANUAL" if actual == "AUTOMATICO" else "AUTOMATICO"
        actuators.set_modo_iluminacion(nuevo)
        logger.info("Modo de iluminación -> %s", nuevo)
    elif boton == "boton_silenciar":
        actuators.silenciar_alarma()
    elif boton == "boton_reset_alerta":
        state_manager.resetear_alerta(_ultimas_lecturas)

    publicar_estado_actuadores()


def publicar_estado_actuadores():
    estado = actuators.get_estado_actuadores()
    mqtt_client.publish("puerta", {"estado": estado["puerta"]})
    mqtt_client.publish("luces", {
        "encendidas": estado["luces"],
        "modo": estado["modo_iluminacion"],
    })
    mqtt_client.publish("ventilador", {"encendido": estado["ventilador"]})
    mqtt_client.publish("alarma", {"activa": estado["alarma"]})


def actualizar_lcd(lecturas: dict, estado_puerta: str, estado_global: str):
    """Muestra, de forma rotativa, cada una de las 6 pantallas obligatorias."""
    global _pantalla_actual
    pantalla = _pantalla_actual % _NUM_PANTALLAS

    if pantalla == 0:
        lcd.pantalla_temp_humedad(lecturas.get("temperatura"), lecturas.get("humedad"))
    elif pantalla == 1:
        lcd.pantalla_gas(lecturas.get("gas"))
    elif pantalla == 2:
        lcd.pantalla_distancia(lecturas.get("distancia"))
    elif pantalla == 3:
        lcd.pantalla_luz(lecturas.get("luz"))
    elif pantalla == 4:
        lcd.pantalla_puerta(estado_puerta)
    elif pantalla == 5:
        lcd.pantalla_estado_global(estado_global)

    _pantalla_actual += 1


def procesar_ciclo_sensores():
    global _puerta_abierta_desde

    lecturas = sensors.leer_todos_los_sensores()
    logger.info("Lecturas: %s", lecturas)

    _ultimas_lecturas.clear()
    _ultimas_lecturas.update(lecturas)

    # 1. Publicar y guardar cada lectura individualmente
    for sensor_key in ("temperatura", "humedad", "gas", "distancia", "luz"):
        valor = lecturas.get(sensor_key)
        if valor is None:
            continue
        mqtt_client.publish(sensor_key, {"value": valor})
        db.save_sensor_reading(sensor_key, valor)

    if lecturas.get("temperatura") is not None:
        _buffer_temperaturas.append(lecturas["temperatura"])

    # 2. Calcular estado global
    estado_anterior = state_manager.get_estado_actual()
    estado_nuevo = state_manager.calcular_estado(lecturas)

    actuators.set_leds_estado(estado_nuevo)

    if estado_nuevo != estado_anterior:
        logger.info("Cambio de estado: %s -> %s", estado_anterior, estado_nuevo)
        db.save_event("cambio_estado", f"{estado_anterior} -> {estado_nuevo}", lecturas)
        db.save_system_status(estado_nuevo, reason="cambio automático por sensores")

    mqtt_client.publish("estado_global", {"estado": estado_nuevo})

    # 3. Reglas de respuesta automática
    if estado_nuevo == "EMERGENCIA":
        actuators.activar_alarma()
        actuators.abrir_puerta()  # simula evacuación
        _puerta_abierta_desde = time.time()
        db.save_event("emergencia", "Nivel de gas/humo por encima del umbral", lecturas)
    elif estado_nuevo == "ADVERTENCIA":
        if lecturas.get("temperatura", 0) > config.THRESHOLDS["temperatura_alta"]:
            actuators.set_ventilador(True)
    else:
        actuators.silenciar_alarma()
        actuators.set_ventilador(False)

    # 4. Acceso automatizado por distancia
    distancia = lecturas.get("distancia")
    if distancia is not None and distancia < config.THRESHOLDS["distancia_apertura"]:
        if actuators.estado_actuadores["puerta"] == "CERRADA":
            actuators.abrir_puerta()
            _puerta_abierta_desde = time.time()
            db.save_event("acceso", "Puerta abierta automáticamente", {"distancia": distancia})

    # Cierre automático de la puerta tras el tiempo configurado
    if _puerta_abierta_desde is not None:
        if time.time() - _puerta_abierta_desde > config.PUERTA_TIEMPO_ABIERTA:
            if estado_nuevo != "EMERGENCIA":  # no cerrar si seguimos en emergencia
                actuators.cerrar_puerta()
                _puerta_abierta_desde = None

    # 5. Iluminación automática (con histéresis: luz_encender / luz_apagar,
    #    para que las luces no parpadeen cuando el valor anda justo en el
    #    límite). Entre esos dos umbrales, no se toca nada.
    luz = lecturas.get("luz")
    if luz is not None and actuators.estado_actuadores["modo_iluminacion"] == "AUTOMATICO":
        if luz < config.THRESHOLDS["luz_encender"]:
            actuators.set_luces(True)
        elif luz > config.THRESHOLDS["luz_apagar"]:
            actuators.set_luces(False)

    publicar_estado_actuadores()

    # 6. Actualizar el LCD rotativo del panel físico
    actualizar_lcd(lecturas, actuators.estado_actuadores["puerta"], estado_nuevo)

    # 7. Disparar módulo ARM64 cada N lecturas
    if len(_buffer_temperaturas) >= config.LECTURAS_PARA_ARM64:
        procesar_con_arm64()


def procesar_con_arm64():
    global _buffer_temperaturas
    logger.info("Disparando módulo ARM64 con %d lecturas", len(_buffer_temperaturas))
    resultado = arm64_bridge.procesar_lecturas(_buffer_temperaturas)
    if resultado:
        db.save_arm64_result(
            max_v=resultado["max"],
            min_v=resultado["min"],
            avg_v=resultado["avg"],
            count=resultado["count"],
        )
        mqtt_client.publish("arm64_resultados", resultado)
        logger.info("Resultado ARM64: %s", resultado)
    else:
        logger.error("El módulo ARM64 no devolvió resultados válidos")
    _buffer_temperaturas = []


def main():
    logger.info("Iniciando sistema (USE_SIMULATION=%s)", config.USE_SIMULATION)
    db.connect()
    mqtt_client.set_command_handler(manejar_comando_remoto)
    mqtt_client.connect()

    if not config.USE_SIMULATION:
        import arduino_bridge
        arduino_bridge.conectar()

    buttons.conectar(manejar_boton_fisico)
    lcd.conectar()

    try:
        while True:
            procesar_ciclo_sensores()
            time.sleep(config.INTERVALO_LECTURA)
    except KeyboardInterrupt:
        logger.info("Apagando sistema...")
    finally:
        mqtt_client.disconnect()
        if not config.USE_SIMULATION:
            import arduino_bridge
            arduino_bridge.desconectar()


if __name__ == "__main__":
    main()