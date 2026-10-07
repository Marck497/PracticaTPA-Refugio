"""
Apartado 6 - Validación de los datos que se cargan.

Campo de formato fijo del dominio: el código de chip de un animal (id_chip),
con la forma  CHIP + tres dígitos  (p. ej. "CHIP001").
"""

import re

# Patrón compilado UNA sola vez, en cadena raw:
#   ^        principio de la cadena
#   CHIP     literal "CHIP" (mayúsculas)
#   \d{3}    exactamente tres dígitos
#   $        final de la cadena (sin nada detrás)
CHIP = re.compile(r"^CHIP\d{3}$")


class RegistroInvalido(Exception):
    """Un registro leído del fichero no cumple lo que el modelo espera."""

class ChipMalFormadoError(RegistroInvalido):
    """El campo id_chip existe pero no encaja con el patrón CHIP + 3 dígitos."""

class ChipAusenteError(RegistroInvalido):
    """El registro no trae el campo id_chip."""

def validar_chip(fila: dict) -> str:
    """Devuelve el chip si es válido; si no, lanza una excepción que dice qué falla."""
    if "id_chip" not in fila:
        raise ChipAusenteError(f"registro sin campo 'id_chip': {fila.get('nombre', '?')!r}")
    chip = fila["id_chip"]
    if not isinstance(chip, str) or not CHIP.match(chip):
        raise ChipMalFormadoError(f"id_chip mal formado: {chip!r}")
    return chip