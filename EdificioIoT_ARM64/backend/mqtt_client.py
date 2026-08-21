"""
Wrapper sobre paho-mqtt para conectarse al broker EMQX,
publicar lecturas/estado y suscribirse a comandos remotos.
"""

import json
import logging
import ssl
import paho.mqtt.client as mqtt

import config

logger = logging.getLogger("mqtt")

_client = None
_on_command_callback = None  # función que main.py inyecta para manejar comandos remotos


def _on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        logger.info("Conectado a EMQX correctamente")
        # Nos suscribimos a comandos que vienen del dashboard
        client.subscribe(config.TOPICS["control_remoto"])
    else:
        logger.error("Fallo de conexión MQTT, código: %s", rc)


def _on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        logger.warning("Mensaje MQTT no es JSON válido: %s", msg.payload)
        return

    if msg.topic == config.TOPICS["control_remoto"] and _on_command_callback:
        _on_command_callback(payload)


def set_command_handler(callback):
    """
    Registra la función que se ejecutará cuando llegue un comando
    """
    global _on_command_callback
    _on_command_callback = callback


def connect():
    global _client
    _client = mqtt.Client(client_id=config.MQTT_CLIENT_ID, protocol=mqtt.MQTTv311)

    if config.MQTT_USERNAME:
        _client.username_pw_set(config.MQTT_USERNAME, config.MQTT_PASSWORD)

    if config.MQTT_USE_TLS:
        _client.tls_set(cert_reqs=ssl.CERT_NONE)
        _client.tls_insecure_set(True)  # ajustar en producción con certificados reales

    _client.on_connect = _on_connect
    _client.on_message = _on_message

    _client.connect(config.MQTT_HOST, config.MQTT_PORT, keepalive=60)
    _client.loop_start()  # hilo en background para no bloquear el main loop
    return _client


def publish(topic_key: str, payload: dict):
    """
    topic_key: una de las llaves definidas en config.TOPICS
    payload: dict que se serializa a JSON
    """
    if _client is None:
        logger.warning("MQTT no conectado, no se pudo publicar en %s", topic_key)
        return
    topic = config.TOPICS.get(topic_key, topic_key)
    _client.publish(topic, json.dumps(payload))


def disconnect():
    if _client:
        _client.loop_stop()
        _client.disconnect()
