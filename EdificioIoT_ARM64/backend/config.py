"""
Configuración centralizada del sistema.
Lee variables de entorno desde un archivo .env
"""
import os
from dotenv import load_dotenv

load_dotenv()

#Modo de operación
USE_SIMULATION = os.getenv("USE_SIMULATION", "True").lower() == "true"

#MQTT (EMQX)
MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "8883"))  # 8883 = TLS, 1883 = sin TLS
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")
MQTT_USE_TLS = os.getenv("MQTT_USE_TLS", "True").lower() == "true"
MQTT_CLIENT_ID = os.getenv("MQTT_CLIENT_ID", "edificio_backend")

TOPICS = {
    "temperatura": "edificio/sensores/temperatura",
    "humedad": "edificio/sensores/humedad",
    "gas": "edificio/sensores/gas",
    "distancia": "edificio/sensores/distancia",
    "luz": "edificio/sensores/luz",
    "puerta": "edificio/actuadores/puerta",
    "luces": "edificio/actuadores/luces",
    "ventilador": "edificio/actuadores/ventilador",
    "alarma": "edificio/actuadores/alarma",
    "estado_global": "edificio/estado/global",
    "control_remoto": "edificio/control/remoto",
    "arm64_resultados": "edificio/arm64/resultados",
}

#MongoDB Atlas
MONGO_URI = os.getenv("MONGO_URI", "")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "edificio_inteligente")

COLLECTIONS = {
    "sensor_readings": "sensor_readings",
    "events": "events",
    "commands": "commands",
    "arm64_results": "arm64_results",
    "system_status": "system_status",
}

# Umbrales del sistema 
THRESHOLDS = {
    "temperatura_alta": 30.0,      # °C
    "humedad_min": 30.0,           # %
    "humedad_max": 70.0,           # %
    "gas_max": 400,                # unidades ADC (depende del sensor MQ)
    "distancia_apertura": 30.0,    # cm -> abre la puerta si es menor
    "luz_baja": 200,               # unidades ADC -> enciende luces si es menor
}

# Tiempo (segundos) que la puerta permanece abierta antes de cerrar sola
PUERTA_TIEMPO_ABIERTA = 5

# Intervalo entre lecturas de sensores (segundos)
INTERVALO_LECTURA = 3

# Cada cuántas lecturas se dispara el módulo ARM64
LECTURAS_PARA_ARM64 = 20

#Rutas del modulo ARM64
ARM64_DIR = os.getenv("ARM64_DIR", "../arm64")
ARM64_BIN = os.path.join(ARM64_DIR, "procesador")
ARM64_DATOS_TXT = os.path.join(ARM64_DIR, "datos.txt")
ARM64_RESULTADO_TXT = os.path.join(ARM64_DIR, "resultado.txt")

#Pines GPIO
PINS = {
    "dht": 4,
    "mq_gas_do": 17,        # salida digital del sensor de gas 
    "hcsr04_trigger": 23,
    "hcsr04_echo": 24,
    "ldr_channel": 0,        # canal en ADC externo, si aplica
    "servo_puerta": 18,
    "buzzer": 27,
    "led_rojo": 22,
    "led_puerta": 5,
    "led_estado_verde": 6,
    "led_estado_amarillo": 13,
    "led_estado_rojo": 19,
    "leds_iluminacion": [12, 16, 20],  # mínimo 3 zonas
    "ventilador": 25,
    "boton_puerta": 21,
    "boton_modo_luz": 26,
    "boton_silenciar": 20,
    "boton_reset_alerta": 7,
}