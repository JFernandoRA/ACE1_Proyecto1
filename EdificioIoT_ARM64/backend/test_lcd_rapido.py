"""
Prueba mínima y aislada del LCD, sin tocar sensores ni el resto del sistema.
Correr en la Raspberry Pi con: python3 test_lcd_rapido.py
"""
from RPLCD.i2c import CharLCD

lcd = CharLCD(i2c_expander="PCF8574", address=0x27, port=1, cols=16, rows=2)
lcd.clear()
lcd.write_string("Hola equipo")
lcd.cursor_pos = (1, 0)
lcd.write_string("LCD funcionando")
