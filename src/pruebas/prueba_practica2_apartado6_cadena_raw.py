"""
Apartado 6.2 - Predicción + ejecución: cadena raw frente a cadena normal.
Ejecutar (desde src/):  python -m pruebas.prueba_practica2_apartado6_cadena_raw

Predicción (antes de ejecutar):
- "^CHIP\d{3}$" sin la r funciona igual que con ella: \d no es un escape de
  Python, la barra se conserva (solo avisa con un SyntaxWarning).
- "\bCHIP\d{3}\b" sin la r NO funciona: \b es un escape de Python (retroceso,
  un solo carácter), el motor ya no ve "límite de palabra" y findall devuelve [].
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