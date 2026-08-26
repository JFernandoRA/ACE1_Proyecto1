"""
arduino_bridge.py
Puente de comunicación serie (USB) entre la Raspberry Pi y un Arduino Uno.

¿Por qué un Arduino? La Raspberry Pi no tiene entradas analógicas, y tanto
el sensor de gas MQ-2 como el LDR entregan una señal analógica (0-5V).
El Arduino Uno sí tiene entradas analógicas (A0-A5), así que:

    MQ-2 (AO) -> Arduino A0 ---\
                                 >-- Arduino lee y envía por USB -> Pi
    LDR        -> Arduino A1 --/

El Arduino corre el sketch en arduino/mq2_ldr_reader.ino, que cada ~300ms
envía por el puerto serie una línea de texto con este formato exacto:

    GAS:<valor_0_1023>,LUZ:<valor_0_1023>

Este módulo abre el puerto serie, lee en un hilo de fondo (para no bloquear
el loop principal) y guarda siempre la última lectura válida.
"""

import logging
import re
import threading
import time

import config

logger = logging.getLogger("arduino_bridge")

_serial_conn = None
_lock = threading.Lock()
_ultima_lectura = {"gas": None, "luz": None, "ultima_actualizacion": 0}
_hilo = None
_detener = False

_PATRON = re.compile(r"GAS:(\d+),LUZ:(\d+)")


def conectar():
    """Abre el puerto serie hacia el Arduino y arranca el hilo de lectura."""
    global _serial_conn, _hilo, _detener

    import serial  # pyserial; se importa aquí para no romper el modo simulación

    try:
        _serial_conn = serial.Serial(
            config.ARDUINO_SERIAL_PORT, config.ARDUINO_BAUDRATE, timeout=2
        )
        # El Arduino se resetea al abrir el puerto serie; le damos un momento.
        time.sleep(2)
        logger.info(
            "Conectado al Arduino en %s @ %d baudios",
            config.ARDUINO_SERIAL_PORT,
            config.ARDUINO_BAUDRATE,
        )
    except Exception as e:
        logger.error(
            "No se pudo abrir el puerto serie %s: %s. "
            "Revisa el cable USB y el puerto (prueba 'ls /dev/tty*').",
            config.ARDUINO_SERIAL_PORT,
            e,
        )
        _serial_conn = None
        return False

    _detener = False
    _hilo = threading.Thread(target=_loop_lectura, daemon=True)
    _hilo.start()
    return True


def _loop_lectura():
    global _detener
    while not _detener and _serial_conn is not None:
        try:
            linea = _serial_conn.readline().decode("utf-8", errors="ignore").strip()
            if not linea:
                continue
            match = _PATRON.match(linea)
            if match:
                gas_raw, luz_raw = int(match.group(1)), int(match.group(2))
                with _lock:
                    _ultima_lectura["gas"] = gas_raw
                    _ultima_lectura["luz"] = luz_raw
                    _ultima_lectura["ultima_actualizacion"] = time.time()
            else:
                logger.debug("Línea del Arduino no reconocida: %s", linea)
        except Exception as e:
            logger.warning("Error leyendo del Arduino: %s", e)
            time.sleep(1)


def get_gas():
    """Devuelve el último valor de gas recibido del Arduino (0-1023) o None."""
    with _lock:
        return _ultima_lectura["gas"]


def get_luz():
    """Devuelve el último valor de luz recibido del Arduino (0-1023) o None."""
    with _lock:
        return _ultima_lectura["luz"]


def datos_frescos(max_antiguedad_seg: float = 5.0) -> bool:
    """True si hemos recibido datos del Arduino recientemente."""
    with _lock:
        ultima = _ultima_lectura["ultima_actualizacion"]
    return ultima != 0 and (time.time() - ultima) < max_antiguedad_seg


def desconectar():
    global _detener, _serial_conn
    _detener = True
    if _hilo is not None:
        _hilo.join(timeout=2)
    if _serial_conn is not None:
        _serial_conn.close()
        _serial_conn = None
