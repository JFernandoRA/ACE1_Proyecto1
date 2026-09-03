"""
test_arm64_bridge.py

Prueba aislada del flujo Python -> datos.txt -> ARM64 -> resultado.txt,
SIN necesitar MongoDB, MQTT ni sensores reales conectados.

Uso:
    python3 test_arm64_bridge.py
"""

import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")

import arm64_bridge
import config

# Lecturas de prueba (simulan 20 lecturas reales de temperatura, como pide el proyecto)
lecturas_prueba = [
    22.4, 23.1, 24.8, 26.3, 25.0,
    27.9, 28.2, 26.5, 24.1, 23.7,
    22.9, 21.6, 23.3, 25.4, 27.1,
    29.6, 28.8, 26.2, 24.9, 23.5,
]

print("=" * 60)
print(f"Probando con {len(lecturas_prueba)} lecturas: {lecturas_prueba}")
print("=" * 60)

# Cálculo esperado en Python, solo para comparar (el cálculo real lo hace ARM64)
enteros = [round(t) for t in lecturas_prueba]
esperado = {
    "max": max(enteros),
    "min": min(enteros),
    "avg": sum(enteros) // len(enteros),  # división entera truncada, igual que sdiv
    "count": len(enteros),
}
print(f"Esperado (calculado en Python, solo referencia): {esperado}")
print()

# 1. Generar datos.txt
ruta = arm64_bridge.generar_datos_txt(lecturas_prueba)
print(f"-> datos.txt generado en: {ruta}")
with open(ruta, "r") as f:
    print("--- Contenido de datos.txt ---")
    print(f.read())

# 2. Ejecutar el binario ARM64
ok = arm64_bridge.ejecutar_binario()
print(f"-> Binario ejecutado correctamente: {ok}")

if not ok:
    print("ERROR: revisa que 'make' haya generado el binario 'procesador' en ARM64_DIR")
    print(f"       (ARM64_DIR actual = {config.ARM64_DIR})")
    exit(1)

# 3. Leer resultado.txt
resultado = arm64_bridge.leer_resultado_txt()
print(f"-> resultado.txt parseado: {resultado}")

print()
print("=" * 60)
if resultado == esperado:
    print("✅ COINCIDE con lo calculado en Python. El módulo ARM64 está funcionando bien.")
else:
    print("❌ NO coincide. Revisa procesador.s o el contenido de datos.txt/resultado.txt")
    print(f"   Esperado: {esperado}")
    print(f"   Obtenido: {resultado}")
print("=" * 60)