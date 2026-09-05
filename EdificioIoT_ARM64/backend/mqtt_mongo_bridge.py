"""
mqtt_mongo_bridge.py

Servicio independiente cuya única responsabilidad es:
    escuchar TODOS los topics MQTT del edificio (edificio/#)
    y persistir cada mensaje en la colección de MongoDB que le corresponde.

Por qué existe como servicio aparte (y no adentro de main.py):

  - main.py (en la Raspberry Pi) debe enfocarse en leer sensores y
    controlar actuadores en tiempo real; no debería depender de que
    Mongo Atlas esté disponible en cada ciclo de lectura para poder
    seguir funcionando.
  - Este bridge puede correr en la misma Pi, en un servidor, o en la
    laptop de cualquier integrante del equipo: solo necesita salida a
    Internet hacia EMQX y hacia MongoDB Atlas (no necesita GPIO ni
    hardware).
  - El API/dashboard que están construyendo NO necesita hablar con la
    Raspberry Pi directamente ni tener credenciales de sensores: solo
    necesita LEER de Mongo (para mostrar datos) y PUBLICAR comandos por
    MQTT en el topic edificio/control/remoto (para controlar
    actuadores). Este bridge es el que efectivamente conecta ambos
    mundos.

IMPORTANTE - evita duplicar escrituras en Mongo:
  Si usan este bridge, quiten las llamadas directas a db.save_* que hay
  actualmente dentro de main.py (en procesar_ciclo_sensores y
  manejar_comando_remoto). De lo contrario cada lectura quedaría
  guardada DOS veces: una por main.py y otra por este bridge. La idea
  es que main.py solo PUBLIQUE por MQTT, y este bridge sea la única
  fuente de escritura hacia MongoDB.

Flujo que implementa:
    EMQX (topics edificio/#) -> este bridge -> MongoDB Atlas

Correr con: python3 mqtt_mongo_bridge.py
"""

import json
import logging
import ssl

import paho.mqtt.client as mqtt

import config
import db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("mqtt_mongo_bridge")


# ---------------------------------------------------------------------------
# Handlers: qué hacer con cada topic cuando llega un mensaje
# ---------------------------------------------------------------------------
def _handle_sensor(sensor_name):
    def handler(payload):
        valor = payload.get("value")
        if valor is not None:
            db.save_sensor_reading(sensor_name, valor)
    return handler


def _handle_actuador(nombre_actuador):
    def handler(payload):
        # Guardamos el cambio de estado del actuador como evento,
        # para poder mostrar el historial en el dashboard.
        db.save_event(
            "cambio_actuador",
            f"{nombre_actuador} actualizado",
            {"actuador": nombre_actuador, **payload},
        )
    return handler


def _handle_estado_global(payload):
    estado = payload.get("estado")
    if estado:
        db.save_system_status(estado, reason="actualizado vía MQTT")


def _handle_comando(payload):
    db.save_command(
        payload.get("source", "dashboard"),
        payload.get("action", "desconocido"),
        payload,
    )


def _handle_arm64(payload):
    try:
        db.save_arm64_result(
            max_v=payload["max"],
            min_v=payload["min"],
            avg_v=payload["avg"],
            count=payload["count"],
        )
    except KeyError:
        logger.warning("Payload de resultado ARM64 incompleto: %s", payload)


# Mapeo topic real (config.TOPICS) -> función que lo procesa
TOPIC_HANDLERS = {
    config.TOPICS["temperatura"]: _handle_sensor("temperatura"),
    config.TOPICS["humedad"]: _handle_sensor("humedad"),
    config.TOPICS["gas"]: _handle_sensor("gas"),
    config.TOPICS["distancia"]: _handle_sensor("distancia"),
    config.TOPICS["luz"]: _handle_sensor("luz"),
    config.TOPICS["puerta"]: _handle_actuador("puerta"),
    config.TOPICS["luces"]: _handle_actuador("luces"),
    config.TOPICS["ventilador"]: _handle_actuador("ventilador"),
    config.TOPICS["alarma"]: _handle_actuador("alarma"),
    config.TOPICS["estado_global"]: _handle_estado_global,
    config.TOPICS["control_remoto"]: _handle_comando,
    config.TOPICS["arm64_resultados"]: _handle_arm64,
}


def _on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        logger.info("Bridge conectado a EMQX correctamente")
        for topic in TOPIC_HANDLERS:
            client.subscribe(topic)
            logger.info("Suscrito a: %s", topic)
    else:
        logger.error("Fallo de conexión MQTT, código: %s", rc)


def _on_message(client, userdata, msg):
    handler = TOPIC_HANDLERS.get(msg.topic)
    if handler is None:
        logger.debug("Topic sin handler registrado: %s", msg.topic)
        return
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        logger.warning("Payload no es JSON válido en %s: %s", msg.topic, msg.payload)
        return
    try:
        handler(payload)
    except Exception as e:
        logger.error("Error procesando mensaje de %s: %s", msg.topic, e)


def main():
    db.connect()

    client = mqtt.Client(
        client_id=f"{config.MQTT_CLIENT_ID}_bridge", protocol=mqtt.MQTTv311
    )
    if config.MQTT_USERNAME:
        client.username_pw_set(config.MQTT_USERNAME, config.MQTT_PASSWORD)
    if config.MQTT_USE_TLS:
        client.tls_set(cert_reqs=ssl.CERT_NONE)
        client.tls_insecure_set(True)  # ajustar en producción con certificados reales

    client.on_connect = _on_connect
    client.on_message = _on_message

    client.connect(config.MQTT_HOST, config.MQTT_PORT, keepalive=60)
    logger.info("Iniciando bridge MQTT -> MongoDB (Ctrl+C para salir)")

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        logger.info("Deteniendo bridge...")
        client.disconnect()


if __name__ == "__main__":
    main()
