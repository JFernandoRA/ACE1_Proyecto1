"""
api.py

API REST del Edificio Inteligente IoT.

Responsabilidad de esta API: SOLO LECTURA de historial desde MongoDB Atlas.

  - Los datos EN VIVO (lecturas nuevas, cambios de actuador, estado global)
    los recibe el dashboard directo por MQTT (ver services/mqttClient.js
    del frontend) — esta API no interviene ahí.
  - Los COMANDOS (abrir puerta, encender luces, etc.) el dashboard los
    publica directo a MQTT (edificio/control/remoto) — tampoco pasan
    por esta API en el flujo normal.
  - Lo que SÍ necesita esta API es dar el "historial" que MQTT no puede
    dar: cuando alguien abre el dashboard por primera vez (o lo
    refresca), no hay forma de que MQTT le entregue mensajes que ya
    pasaron. Por eso el dashboard hace UNA llamada a /api/snapshot al
    cargar, y de ahí en adelante todo lo demás llega por MQTT.

Requiere: fastapi, uvicorn (agregar a requirements.txt)
Correr con: uvicorn api:app --host 0.0.0.0 --port 5000 --reload
"""

import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import config
import db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("api")

app = FastAPI(title="Edificio Inteligente IoT - API", version="1.0.0")

# ---------------------------------------------------------------------------
# CORS: el navegador (Vite corre en localhost:5173 por defecto) necesita
# permiso explícito para llamar a esta API desde otro puerto.
# En producción, cambia ALLOWED_ORIGINS en tu .env por el dominio real.
# ---------------------------------------------------------------------------
_origins_env = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")
ALLOWED_ORIGINS = [o.strip() for o in _origins_env.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

SENSORES_VALIDOS = ("temperatura", "humedad", "gas", "distancia", "luz")
ACTUADORES_VALIDOS = ("puerta", "luces", "ventilador", "alarma")


@app.on_event("startup")
def _startup():
    db.connect()
    logger.info("API conectada a MongoDB Atlas")


# ---------------------------------------------------------------------------
# Helpers de serialización: Mongo devuelve ObjectId y datetime, que no son
# JSON de forma nativa. Los convertimos a texto antes de responder.
# ---------------------------------------------------------------------------
def _serialize(doc: dict | None) -> dict | None:
    if doc is None:
        return None
    doc = dict(doc)
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    ts = doc.get("timestamp")
    if ts is not None and hasattr(ts, "isoformat"):
        doc["timestamp"] = ts.isoformat() + "Z"
    return doc


def _serialize_many(docs) -> list:
    return [_serialize(d) for d in docs]


# ---------------------------------------------------------------------------
# Endpoints individuales
# ---------------------------------------------------------------------------
@app.get("/api/health")
def health():
    """Chequeo simple de que la API y la conexión a Mongo están vivas."""
    try:
        db.get_db().command("ping")
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Mongo no disponible: {e}")


@app.get("/api/readings/{sensor}")
def readings(sensor: str, limit: int = 50):
    """
    Historial de un sensor para alimentar las gráficas (TrendChart.jsx).
    sensor: 'temperatura' | 'humedad' | 'gas' | 'distancia' | 'luz'
    Devuelve en orden CRONOLÓGICO (más antiguo primero), como lo
    necesita un gráfico de líneas.
    """
    if sensor not in SENSORES_VALIDOS:
        raise HTTPException(
            status_code=404,
            detail=f"Sensor '{sensor}' no reconocido. Usa uno de: {SENSORES_VALIDOS}",
        )
    docs = db.get_latest_readings(sensor, limit=limit)
    docs = list(reversed(docs))  # get_latest_readings devuelve más reciente primero
    return _serialize_many(docs)


@app.get("/api/events")
def events(limit: int = 20):
    """Últimos eventos (alertas, cambios de estado, accesos) para ActivityTables.jsx."""
    return _serialize_many(db.get_latest_events(limit=limit))


@app.get("/api/commands")
def commands(limit: int = 20):
    """Últimos comandos remotos ejecutados, para ActivityTables.jsx."""
    return _serialize_many(db.get_latest_commands(limit=limit))


@app.get("/api/arm64/results")
def arm64_results(limit: int = 20):
    """Historial de resultados del módulo ARM64 (para la gráfica de promedios)."""
    return _serialize_many(db.get_latest_arm64_results(limit=limit))


@app.get("/api/arm64/latest")
def arm64_latest():
    """Último resultado ARM64 únicamente, para Arm64Panel.jsx."""
    results = db.get_latest_arm64_results(limit=1)
    if not results:
        return {"max": None, "min": None, "avg": None, "count": None}
    doc = _serialize(results[0])
    return {"max": doc["max"], "min": doc["min"], "avg": doc["avg"], "count": doc["count"]}


@app.get("/api/status")
def status():
    """Estado global actual del edificio (NORMAL/ADVERTENCIA/EMERGENCIA)."""
    doc = db.get_current_status()
    if doc is None:
        return {"status": "NORMAL", "reason": "sin datos aún"}
    return _serialize(doc)


@app.get("/api/actuators")
def actuators():
    """
    Estado actual de puerta/luces/ventilador/alarma, reconstruido a
    partir del último evento 'cambio_actuador' de cada uno.
    """
    resultado = {
        "puerta": "CERRADA",
        "luces": False,
        "modo_iluminacion": "AUTOMATICO",
        "ventilador": False,
        "alarma": False,
    }
    for nombre in ACTUADORES_VALIDOS:
        doc = db.get_latest_actuator_state(nombre)
        if doc is None:
            continue
        data = doc.get("data", {})
        if nombre == "puerta":
            resultado["puerta"] = data.get("estado", resultado["puerta"])
        elif nombre == "luces":
            resultado["luces"] = data.get("encendidas", resultado["luces"])
            resultado["modo_iluminacion"] = data.get("modo", resultado["modo_iluminacion"])
        elif nombre == "ventilador":
            resultado["ventilador"] = data.get("encendido", resultado["ventilador"])
        elif nombre == "alarma":
            resultado["alarma"] = data.get("activa", resultado["alarma"])
    return resultado


# ---------------------------------------------------------------------------
# Endpoint agregador: UNA sola llamada para arrancar el dashboard completo
# ---------------------------------------------------------------------------
@app.get("/api/snapshot")
def snapshot(readings_limit: int = 50, events_limit: int = 20, commands_limit: int = 20):
    """
    Devuelve todo lo que el dashboard necesita para pintar su primera
    pantalla, en una sola llamada: historial de cada sensor, estado
    global, actuadores, último ARM64, eventos y comandos recientes.
    Pensado para llamarse UNA VEZ al montar la app; de ahí en adelante
    MQTT se encarga de las actualizaciones en vivo.
    """
    return {
        "history": {
            sensor: _serialize_many(list(reversed(db.get_latest_readings(sensor, limit=readings_limit))))
            for sensor in SENSORES_VALIDOS
        },
        "status": status(),
        "actuators": actuators(),
        "arm64": arm64_latest(),
        "events": _serialize_many(db.get_latest_events(limit=events_limit)),
        "commands": _serialize_many(db.get_latest_commands(limit=commands_limit)),
    }
