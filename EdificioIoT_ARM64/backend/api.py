"""
api.py
Pequeño servidor REST (Flask) que expone el historial guardado en MongoDB
Atlas al dashboard web. El tiempo real (lecturas/estado/actuadores que
cambian segundo a segundo) sigue viajando por MQTT directo desde el
navegador; esta API solo cubre lo que MQTT no puede dar por sí solo:
datos que ya existían ANTES de que el dashboard se abriera
(gráficas históricas, últimos eventos, últimos comandos, último resultado
ARM64).

Se corre como un proceso aparte de main.py (main.py sigue siendo el que
lee sensores y controla actuadores). Ambos comparten la misma conexión a
MongoDB (misma base de datos, mismas colecciones).

Ejecutar:
    python3 api.py
"""

import logging

from flask import Flask, jsonify, request
from flask_cors import CORS

import config
import db

logging.basicConfig(level=logging.INFO, format="%(asctime)s [api] %(levelname)s: %(message)s")
logger = logging.getLogger("api")

app = Flask(__name__)
CORS(app, origins=config.ALLOWED_ORIGINS)

VALID_SENSORS = {"temperatura", "humedad", "gas", "distancia", "luz"}


def _serialize(doc: dict) -> dict:
    doc = dict(doc)
    doc["id"] = str(doc.pop("_id"))
    if "timestamp" in doc and doc["timestamp"] is not None:
        doc["timestamp"] = doc["timestamp"].isoformat() + "Z"
    return doc


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api/readings/<sensor>")
def readings(sensor):
    if sensor not in VALID_SENSORS:
        return jsonify({"error": f"sensor inválido: {sensor}"}), 400
    limit = request.args.get("limit", default=50, type=int)
    docs = db.get_latest_readings(sensor, limit=limit)
    docs.reverse()  # más antiguo primero, para graficar de izquierda a derecha
    return jsonify([_serialize(d) for d in docs])


@app.get("/api/events")
def events():
    limit = request.args.get("limit", default=20, type=int)
    docs = db.get_latest_events(limit=limit)
    return jsonify([_serialize(d) for d in docs])


@app.get("/api/commands")
def commands():
    limit = request.args.get("limit", default=20, type=int)
    docs = db.get_latest_commands(limit=limit)
    out = []
    for d in docs:
        d = _serialize(d)
        d["label"] = d.get("action", "?")  # el dashboard espera "label"
        out.append(d)
    return jsonify(out)


@app.get("/api/arm64/latest")
def arm64_latest():
    docs = db.get_latest_arm64_results(limit=1)
    if not docs:
        return jsonify(None)
    return jsonify(_serialize(docs[0]))


@app.get("/api/arm64/history")
def arm64_history():
    limit = request.args.get("limit", default=20, type=int)
    docs = db.get_latest_arm64_results(limit=limit)
    docs.reverse()
    return jsonify([_serialize(d) for d in docs])


@app.get("/api/status")
def status():
    doc = db.get_current_status()
    if not doc:
        return jsonify(None)
    return jsonify(_serialize(doc))


if __name__ == "__main__":
    db.connect()
    logger.info("API REST escuchando en 0.0.0.0:%s (orígenes permitidos: %s)",
                config.API_PORT, config.ALLOWED_ORIGINS)
    app.run(host="0.0.0.0", port=config.API_PORT)
