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
import actuators

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


def resetear_alerta(lecturas: dict = None):
    """
    Se llama cuando el usuario presiona el botón físico de 'restablecer alerta'
    o el control equivalente del dashboard, una vez la condición peligrosa
    ya no está presente.

    Importante: revisamos el valor de gas MÁS RECIENTE (lecturas), no la
    etiqueta _estado_actual guardada. La etiqueta solo se actualiza cada
    INTERVALO_LECTURA segundos dentro del loop de sensores, así que si el
    gas ya bajó pero la etiqueta todavía dice "EMERGENCIA" porque no le ha
    tocado su ciclo de actualización, el reset quedaría bloqueado sin razón.
    """
    global _estado_actual

    if lecturas is not None:
        gas = lecturas.get("gas")
        if gas is not None and gas > config.THRESHOLDS["gas_max"]:
            logger.warning(
                "No se puede resetear: el gas sigue por encima del umbral (%s > %s)",
                gas,
                config.THRESHOLDS["gas_max"],
            )
            return

    _estado_actual = "NORMAL"
    logger.info("Alerta reseteada manualmente -> NORMAL")

    # Retroalimentación visual/física inmediata: prende el LED verde y apaga
    # el ventilador al instante, en vez de esperar hasta el siguiente ciclo
    # del loop principal (que puede tardar varios segundos y, si la
    # condición real sigue presente, nunca llega a mostrarlo porque el
    # estado ya volvió a cambiar antes).
    # OJO: si el sensor sigue detectando la condición peligrosa, el próximo
    # ciclo de lectura va a recalcular el estado real y puede volver a
    # encender el ventilador y cambiar los LEDs -- esto es solo para
    # confirmar que el botón sí actúa sobre el hardware, no reemplaza que
    # la condición real deba resolverse.
    actuators.set_leds_estado("NORMAL")
    actuators.set_ventilador(False)