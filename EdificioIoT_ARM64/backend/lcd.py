"""
lcd.py
Control de la pantalla LCD 16x2 conectada por el backpack I2C (PCF8574).

Conexión (solo 4 cables):
    LCD backpack VCC -> 5V  (pin físico 2 o 4)
    LCD backpack GND -> GND (cualquier pin GND)
    LCD backpack SDA -> GPIO2 / pin físico 3
    LCD backpack SCL -> GPIO3 / pin físico 5

Nota: si al encender no se ve nada en la pantalla, gira el potenciómetro
azul del backpack (ajusta el contraste). Si nunca prende el backlight,
revisa la dirección I2C con: sudo i2cdetect -y 1
(normalmente es 0x27, a veces 0x3F -> ajústalo en el .env con
LCD_I2C_ADDRESS=0x3F)
"""

import logging

import config

logger = logging.getLogger("lcd")

_lcd = None


def conectar():
    global _lcd
    if config.USE_SIMULATION:
        logger.info("LCD en modo simulación (se imprime en consola)")
        return

    from RPLCD.i2c import CharLCD

    try:
        _lcd = CharLCD(
            i2c_expander="PCF8574",
            address=config.LCD_I2C_ADDRESS,
            port=1,
            cols=config.LCD_COLS,
            rows=config.LCD_ROWS,
            dotsize=8,
        )
        _lcd.clear()
        logger.info("LCD I2C conectado en dirección %s", hex(config.LCD_I2C_ADDRESS))
    except Exception as e:
        logger.error(
            "No se pudo conectar el LCD (revisa el I2C y la dirección): %s", e
        )
        _lcd = None


def mostrar(linea1: str, linea2: str = ""):
    """Muestra hasta 2 líneas de 16 caracteres cada una."""
    linea1 = linea1[: config.LCD_COLS].ljust(config.LCD_COLS)
    linea2 = linea2[: config.LCD_COLS].ljust(config.LCD_COLS)

    if config.USE_SIMULATION or _lcd is None:
        print(f"[LCD] {linea1.strip()} | {linea2.strip()}")
        return

    try:
        _lcd.cursor_pos = (0, 0)
        _lcd.write_string(linea1)
        _lcd.cursor_pos = (1, 0)
        _lcd.write_string(linea2)
    except Exception as e:
        logger.warning("Error escribiendo al LCD: %s", e)


# ---------------------------------------------------------------------------
# Pantallas rotativas requeridas por el proyecto
# ---------------------------------------------------------------------------
def pantalla_temp_humedad(temp, hum):
    t = f"{temp}C" if temp is not None else "--"
    h = f"{hum}%" if hum is not None else "--"
    mostrar("Temp/Humedad", f"{t}  Hum:{h}")


def pantalla_gas(gas):
    g = str(gas) if gas is not None else "--"
    mostrar("Nivel de gas", f"Valor: {g}")


def pantalla_distancia(dist):
    d = f"{dist}cm" if dist is not None else "--"
    mostrar("Distancia", f"Detectado: {d}")


def pantalla_luz(luz):
    l = str(luz) if luz is not None else "--"
    mostrar("Nivel de luz", f"Valor: {l}")


def pantalla_puerta(estado_puerta):
    mostrar("Estado puerta", estado_puerta)


def pantalla_estado_global(estado):
    mostrar("Estado edificio", estado)
