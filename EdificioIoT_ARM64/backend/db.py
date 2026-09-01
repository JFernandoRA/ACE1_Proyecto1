"""
db.py
Capa de acceso a MongoDB Atlas.
Expone funciones simples para guardar lecturas, eventos, comandos,
resultados de ARM64 y el estado del sistema.
"""

import datetime
import logging
from pymongo import MongoClient
from pymongo.errors import PyMongoError

import config

logger = logging.getLogger("db")

_client = None
_db = None


def connect():
    """Inicializa la conexión a MongoDB Atlas. Debe llamarse una sola vez."""
    global _client, _db
    if not config.MONGO_URI:
        raise RuntimeError(
            "MONGO_URI no está configurado. Revisa tu archivo .env"
        )
    _client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=5000)
    _db = _client[config.MONGO_DB_NAME]
    #Fuerza una verificación de conexión temprana
    _client.admin.command("ping")
    logger.info("Conectado a MongoDB Atlas (%s)", config.MONGO_DB_NAME)
    return _db


def get_db():
    if _db is None:
        return connect()
    return _db


def _now():
    return datetime.datetime.utcnow()


def _insert(collection_name: str, document: dict):
    document.setdefault("timestamp", _now())
    try:
        col = get_db()[collection_name]
        result = col.insert_one(document)
        return result.inserted_id
    except PyMongoError as e:
        logger.error("Error insertando en %s: %s", collection_name, e)
        return None


# Funciones específicas por colección
def save_sensor_reading(sensor: str, value, extra: dict = None):
    """
    sensor: 'temperatura' | 'humedad' | 'gas' | 'distancia' | 'luz'
    """
    doc = {"sensor": sensor, "value": value}
    if extra:
        doc.update(extra)
    return _insert(config.COLLECTIONS["sensor_readings"], doc)


def save_event(event_type: str, description: str, data: dict = None):
    """
    event_type: 'alerta' | 'emergencia' | 'cambio_estado' | 'acceso' | etc.
    """
    doc = {"type": event_type, "description": description}
    if data:
        doc["data"] = data
    return _insert(config.COLLECTIONS["events"], doc)


def save_command(source: str, action: str, params: dict = None):
    """
    source: 'dashboard' | 'panel_fisico'
    action: 'abrir_puerta' | 'toggle_luces' | 'silenciar_buzzer' | etc.
    """
    doc = {"source": source, "action": action}
    if params:
        doc["params"] = params
    return _insert(config.COLLECTIONS["commands"], doc)


def save_arm64_result(max_v: int, min_v: int, avg_v: int, count: int):
    doc = {"max": max_v, "min": min_v, "avg": avg_v, "count": count}
    return _insert(config.COLLECTIONS["arm64_results"], doc)


def save_system_status(status: str, reason: str = ""):
    doc = {"status": status, "reason": reason}
    return _insert(config.COLLECTIONS["system_status"], doc)

# Funciones de consulta (útiles para el dashboard/API)
def get_latest_readings(sensor: str, limit: int = 50):
    col = get_db()[config.COLLECTIONS["sensor_readings"]]
    cursor = col.find({"sensor": sensor}).sort("timestamp", -1).limit(limit)
    return list(cursor)


def get_latest_events(limit: int = 20):
    col = get_db()[config.COLLECTIONS["events"]]
    return list(col.find().sort("timestamp", -1).limit(limit))


def get_latest_commands(limit: int = 20):
    col = get_db()[config.COLLECTIONS["commands"]]
    return list(col.find().sort("timestamp", -1).limit(limit))


def get_latest_arm64_results(limit: int = 20):
    col = get_db()[config.COLLECTIONS["arm64_results"]]
    return list(col.find().sort("timestamp", -1).limit(limit))


def get_current_status():
    col = get_db()[config.COLLECTIONS["system_status"]]
    return col.find_one(sort=[("timestamp", -1)])

def get_latest_actuator_state(actuator_name: str):
    """
    Busca el evento más reciente de tipo 'cambio_actuador' para un actuador
    específico ('puerta', 'luces', 'ventilador', 'alarma'). Este evento lo
    genera mqtt_mongo_bridge.py cada vez que llega un mensaje MQTT de
    edificio/actuadores/<algo>.
    """
    col = get_db()[config.COLLECTIONS["events"]]
    return col.find_one(
        {"type": "cambio_actuador", "data.actuador": actuator_name},
        sort=[("timestamp", -1)],
    )


