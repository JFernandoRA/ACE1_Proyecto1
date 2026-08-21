"""
state_manager.py
Calcula el estado global del edificio a partir de las lecturas de sensores,
siguiendo las reglas obligatorias del proyecto:

  NORMAL      -> todos los sensores dentro de rangos seguros
  ADVERTENCIA -> temperatura alta, humedad fuera de rango, u otra condición no crítica
  EMERGENCIA  -> gas/humo por encima del umbral (no puede bajar de EMERGENCIA
                 mientras la condición siga presente)
"""

import logging
import config

logger = logging.getLogger("state_manager")

# Estado actual en memoria
_estado_actual = "NORMAL"


def calcular_estado(lecturas: dict) -> str:
    """
    lecturas: dict con keys 'temperatura', 'humedad', 'gas', 'distancia', 'luz'
    Devuelve el nuevo estado global y actualiza el estado interno.
    """
    global _estado_actual

    gas = lecturas.get("gas")
    temperatura = lecturas.get("temperatura")
    humedad = lecturas.get("humedad")

    # EMERGENCIA tiene prioridad absoluta y es "pegajosa":
    # no se puede volver a NORMAL mientras la condición siga presente.
    if gas is not None and gas > config.THRESHOLDS["gas_max"]:
        _estado_actual = "EMERGENCIA"
        return _estado_actual

    if _estado_actual == "EMERGENCIA":
        # Si ya estábamos en emergencia y el gas ya bajó, pasamos a advertencia
        # (no directo a NORMAL) para forzar una revisión / reset manual.
        _estado_actual = "ADVERTENCIA"
        return _estado_actual

    advertencia = False
    if temperatura is not None and temperatura > config.THRESHOLDS["temperatura_alta"]:
        advertencia = True
    if humedad is not None and not (
        config.THRESHOLDS["humedad_min"] <= humedad <= config.THRESHOLDS["humedad_max"]
    ):
        advertencia = True

    _estado_actual = "ADVERTENCIA" if advertencia else "NORMAL"
    return _estado_actual


def get_estado_actual() -> str:
    return _estado_actual


def resetear_alerta():
    """
    Se llama cuando el usuario presiona el botón físico de 'restablecer alerta'
    o el control equivalente del dashboard, una vez la condición peligrosa
    ya no está presente.
    """
    global _estado_actual
    if _estado_actual != "EMERGENCIA":
        _estado_actual = "NORMAL"
        logger.info("Alerta reseteada manualmente -> NORMAL")
    else:
        logger.warning("No se puede resetear: la condición de EMERGENCIA sigue activa")
