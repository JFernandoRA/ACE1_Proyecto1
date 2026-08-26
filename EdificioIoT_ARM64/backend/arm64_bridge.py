"""
Responsable unicamente de:
  1. Generar datos.txt con lecturas reales de temperatura (enteros).
  2. Ejecutar el binario compilado en ensamblador ARM64.
  3. Leer resultado.txt.
"""

import logging
import subprocess
import os

import config

logger = logging.getLogger("arm64_bridge")


def generar_datos_txt(lecturas_temperatura: list[float]) -> str:
    """
    lecturas_temperatura: lista de temperaturas reales tomadas del sensor
    """
    os.makedirs(config.ARM64_DIR, exist_ok=True)
    with open(config.ARM64_DATOS_TXT, "w") as f:
        for temp in lecturas_temperatura:
            f.write(f"{round(temp)}\n")
        f.write("$\n")
    logger.info(
        "datos.txt generado con %d lecturas en %s",
        len(lecturas_temperatura),
        config.ARM64_DATOS_TXT,
    )
    return config.ARM64_DATOS_TXT


def ejecutar_binario() -> bool:
    """Ejecuta el binario ARM64 ya compilado, devuelve True si corrió sin error."""
    if not os.path.exists(config.ARM64_BIN):
        logger.error(
            "No se encontró el binario ARM64 en %s. ¿Ya lo compilaste con make?",
            config.ARM64_BIN,
        )
        return False
    try:
        resultado = subprocess.run(
            [config.ARM64_BIN],
            cwd=config.ARM64_DIR,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if resultado.returncode != 0:
            logger.error("El binario ARM64 terminó con error: %s", resultado.stderr)
            return False
        return True
    except subprocess.TimeoutExpired:
        logger.error("Timeout ejecutando el binario ARM64")
        return False


def leer_resultado_txt() -> dict | None:
    if not os.path.exists(config.ARM64_RESULTADO_TXT):
        logger.error("No se encontró resultado.txt en %s", config.ARM64_RESULTADO_TXT)
        return None

    valores = {}
    with open(config.ARM64_RESULTADO_TXT, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if "=" not in linea:
                continue
            clave, valor = linea.split("=", 1)
            clave = clave.strip().upper().replace("Á", "A")  # normaliza MÁX -> MAX
            try:
                valores[clave] = int(valor.strip())
            except ValueError:
                logger.warning("Valor no numérico en resultado.txt: %s", linea)

    if not {"MAX", "MIN", "AVG", "COUNT"}.issubset(valores.keys()):
        logger.error("resultado.txt no tiene el formato esperado: %s", valores)
        return None

    return {
        "max": valores["MAX"],
        "min": valores["MIN"],
        "avg": valores["AVG"],
        "count": valores["COUNT"],
    }


def procesar_lecturas(lecturas_temperatura: list[float]) -> dict | None:
    """Orquesta el flujo completo: datos.txt -> binario -> resultado.txt."""
    generar_datos_txt(lecturas_temperatura)
    if not ejecutar_binario():
        return None
    return leer_resultado_txt()