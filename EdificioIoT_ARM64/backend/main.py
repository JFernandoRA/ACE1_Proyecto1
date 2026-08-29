"""
Loop principal del sistema de Edificio Inteligente IoT.

Flujo por cada ciclo de lectura:
  1. Leer sensores (real o simulado).
  2. Publicar lecturas por MQTT.
  3. Guardar lecturas en MongoDB. (ahora lo hace mqtt_mongo_bridge.py,
     escuchando estos mismos topics -- ver líneas comentadas con db.save_*)
  4. Calcular estado global y actuar en consecuencia (LEDs, buzzer, puerta, etc.).
  5. Cada N lecturas, disparar el flujo con el módulo ARM64.
  6. Escuchar y ejecutar comandos remotos que lleguen del dashboard.
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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("main")

# Buffer de temperaturas reales para alimentar al módulo ARM64
_buffer_temperaturas: list[float] = []
_puerta_abierta_desde: float | None = None
# Última lectura de sensores completa, para que resetear_alerta() pueda
# validar el gas actual (igual que hace hardware_test.py con gpiozero).
_ultimas_lecturas: dict = {}


def manejar_comando_remoto(payload: dict):
    action = payload.get("action")
    logger.info("Comando remoto recibido: %s", payload)
    # Guardado en Mongo movido a mqtt_mongo_bridge.py, que escucha
    # edificio/control/remoto y guarda el comando desde ahí.
    # db.save_command("dashboard", action, payload)

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
        # Se le pasan las lecturas más recientes para que la función pueda
        # negarse a resetear si el gas sigue por encima del umbral (ver
        # state_manager.resetear_alerta).
        state_manager.resetear_alerta(_ultimas_lecturas)
    else:
        logger.warning("Acción de comando remoto desconocida: %s", action)

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


def procesar_ciclo_sensores():
    global _puerta_abierta_desde

    lecturas = sensors.leer_todos_los_sensores()
    logger.info("Lecturas: %s", lecturas)

    # Guardamos la última lectura completa para que manejar_comando_remoto
    # (que llega por interrupción MQTT, fuera de este loop) pueda usarla
    # al procesar un resetear_alerta.
    _ultimas_lecturas.clear()
    _ultimas_lecturas.update(lecturas)

    # 1. Publicar y guardar cada lectura individualmente
    for sensor_key in ("temperatura", "humedad", "gas", "distancia", "luz"):
        valor = lecturas.get(sensor_key)
        if valor is None:
            continue
        mqtt_client.publish(sensor_key, {"value": valor})
        # Guardado en Mongo movido a mqtt_mongo_bridge.py (escucha este
        # mismo topic).
        # db.save_sensor_reading(sensor_key, valor)

    if lecturas.get("temperatura") is not None:
        _buffer_temperaturas.append(lecturas["temperatura"])

    # 2. Calcular estado global
    estado_anterior = state_manager.get_estado_actual()
    estado_nuevo = state_manager.calcular_estado(lecturas)

    actuators.set_leds_estado(estado_nuevo)

    if estado_nuevo != estado_anterior:
        logger.info("Cambio de estado: %s -> %s", estado_anterior, estado_nuevo)
        db.save_event("cambio_estado", f"{estado_anterior} -> {estado_nuevo}", lecturas)
        # Guardado en Mongo movido a mqtt_mongo_bridge.py (escucha
        # edificio/estado/global, que se publica en cada ciclo).
        # db.save_system_status(estado_nuevo, reason="cambio automático por sensores")

    mqtt_client.publish("estado_global", {"estado": estado_nuevo})

    # 3. Reglas de respuesta automática
    if estado_nuevo == "EMERGENCIA":
        actuators.activar_alarma()
        actuators.abrir_puerta()  # simula evacuación
        _puerta_abierta_desde = time.time()
        # Este también se queda: guarda el motivo exacto de la emergencia
        # con las lecturas completas, que no viaja por MQTT.
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

    # 5. Iluminación automática (con histéresis, igual que hardware_test.py:
    # se enciende por debajo de "luz_encender" y se apaga por encima de
    # "luz_apagar"; entre esos dos valores no se toca nada, para evitar
    # parpadeos). Antes esta línea usaba config.THRESHOLDS["luz_baja"], que
    # ya no existe -- causaba un KeyError y tumbaba todo el programa.
    luz = lecturas.get("luz")
    if luz is not None and actuators.estado_actuadores["modo_iluminacion"] == "AUTOMATICO":
        if luz < config.THRESHOLDS["luz_encender"]:
            actuators.set_luces(True)
        elif luz > config.THRESHOLDS["luz_apagar"]:
            actuators.set_luces(False)
        # si luz está entre los dos umbrales, no se cambia nada

    publicar_estado_actuadores()

    # 6. Disparar módulo ARM64 cada N lecturas
    if len(_buffer_temperaturas) >= config.LECTURAS_PARA_ARM64:
        procesar_con_arm64()


def procesar_con_arm64():
    global _buffer_temperaturas
    logger.info("Disparando módulo ARM64 con %d lecturas", len(_buffer_temperaturas))
    resultado = arm64_bridge.procesar_lecturas(_buffer_temperaturas)
    if resultado:
        # Guardado en Mongo movido a mqtt_mongo_bridge.py (escucha
        # edificio/arm64/resultados). 
        # db.save_arm64_result(**resultado)
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

    try:
        while True:
            procesar_ciclo_sensores()
            time.sleep(config.INTERVALO_LECTURA)
    except KeyboardInterrupt:
        logger.info("Apagando sistema...")
    finally:
        mqtt_client.disconnect()


if __name__ == "__main__":
    main()
