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
    # Histéresis para la iluminación: dos umbrales en vez de uno solo, para
    # que las luces no parpadeen cuando el valor de luz anda justo en el
    # límite. Se enciende por debajo de "luz_encender" y se apaga por
    # encima de "luz_apagar" -- entre esos dos valores, se queda como
    # estaba (no hace nada).
    "luz_encender": 150,           # unidades ADC -> por debajo de esto, enciende
    "luz_apagar": 250,             # unidades ADC -> por encima de esto, apaga
}

# Tiempo (segundos) que la puerta permanece abierta antes de cerrar sola
PUERTA_TIEMPO_ABIERTA = 5

# Intervalo entre lecturas de sensores (segundos)
INTERVALO_LECTURA = 3

# Cada cuántas lecturas se dispara el módulo ARM64
LECTURAS_PARA_ARM64 = 20

#Rutas del modulo ARM64
ARM64_DIR = os.getenv("ARM64_DIR", "../ARM")
ARM64_BIN = os.path.join(ARM64_DIR, "procesador")
ARM64_DATOS_TXT = os.path.join(ARM64_DIR, "datos.txt")
ARM64_RESULTADO_TXT = os.path.join(ARM64_DIR, "resultado.txt")

# ---------------------------------------------------------------------------
# Pines GPIO (numeración BCM) - Raspberry Pi 3
#
# NOTA IMPORTANTE: la Raspberry Pi no tiene entradas analógicas, por lo que
# el MQ-2 (gas/humo) y el LDR (luz) NO se conectan a la Pi. Se conectan a un
# Arduino Uno, que lee sus valores analógicos y se los envía a la Pi por
# cable USB (puerto serie). Ver arduino_bridge.py y arduino/mq2_ldr_reader.ino
# ---------------------------------------------------------------------------
PINS = {
    "dht": 4,                 # DHT11/DHT22 - dato (pin físico 7)
    "hcsr04_trigger": 23,      # HC-SR04 - trigger (pin físico 16)
    "hcsr04_echo": 24,         # HC-SR04 - echo, vía divisor de voltaje (pin físico 18)
    "servo_puerta": 18,        # Servo SG90 - señal PWM (pin físico 12)
    "buzzer": 27,              # Buzzer activo (pin físico 13)
    "led_rojo": 22,            # LED rojo de emergencia por gas (pin físico 15)
    "led_puerta": 5,           # LED indicador de puerta (pin físico 29)
    "led_estado_verde": 6,     # LED estado NORMAL (pin físico 31)
    "led_estado_amarillo": 13, # LED estado ADVERTENCIA (pin físico 33)
    "led_estado_rojo": 19,     # LED estado EMERGENCIA (pin físico 35)
    "leds_iluminacion": [12, 16, 20],  # 3 zonas (pines físicos 32, 36, 38)
    "ventilador": 25,          # Control de ventilador vía relé/transistor (pin físico 22)
    "boton_puerta": 21,        # Botón físico: abrir/cerrar puerta (pin físico 40)
    "boton_modo_luz": 26,      # Botón físico: alternar modo AUTOMATICO/MANUAL (pin físico 37)
    "boton_silenciar": 7,      # Botón físico: silenciar buzzer (pin físico 26)
    "boton_reset_alerta": 8,   # Botón físico: resetear alerta (pin físico 24)
    # LCD 16x2 con backpack I2C: no usa pines PINS, usa el bus I2C
    # (SDA = GPIO2 / pin físico 3, SCL = GPIO3 / pin físico 5)
}

# Dirección I2C del backpack del LCD (la más común es 0x27, algunos son 0x3F)
LCD_I2C_ADDRESS = int(os.getenv("LCD_I2C_ADDRESS", "0x27"), 16)
LCD_COLS = 16
LCD_ROWS = 2

# El módulo de relé de 1 canal más común (placa azul, relé "Songle") es
# activo-bajo: se energiza con IN en LOW, igual que tu buzzer. Si al correr
# test_rele_rapido.py el relé hace "clic" en la fase de HIGH en vez de LOW,
# cambia esto a False.
RELE_VENTILADOR_ACTIVE_LOW = os.getenv("RELE_VENTILADOR_ACTIVE_LOW", "True").lower() == "true"

# ---------------------------------------------------------------------------
# Puente serie con el Arduino Uno (lee MQ-2 y LDR)
# ---------------------------------------------------------------------------
ARDUINO_SERIAL_PORT = os.getenv("ARDUINO_SERIAL_PORT", "/dev/ttyACM0")
ARDUINO_BAUDRATE = int(os.getenv("ARDUINO_BAUDRATE", "9600"))