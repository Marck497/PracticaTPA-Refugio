"""
Apartado 6.2 - Predicción + ejecución: cadena raw frente a cadena normal.
Ejecutar:  python3 demo_cadena_raw.py
"""
import re

print("len('\\b') =", len("\b"), "| len(r'\\b') =", len(r"\b"))

# 1) Nuestro patrón real, SIN la r inicial. \d no es un escape de Python,
#    así que Python deja la barra tal cual (y avisa con un SyntaxWarning).
sin_raw = re.compile("^CHIP\d{3}$")
print("CHIP001 con patrón sin r:", bool(sin_raw.match("CHIP001")))
print("chip1   con patrón sin r:", bool(sin_raw.match("chip1")))

# 2) Un patrón con \b (límite de palabra) para buscar chips dentro de un texto.
texto = "el animal CHIP001 ya fue revisado"
print("con r  :", re.findall(r"\bCHIP\d{3}\b", texto))
print("sin r  :", re.findall("\bCHIP\d{3}\b", texto))
