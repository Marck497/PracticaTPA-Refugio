"""
Apartado 4.2 - Persistencia del modelo en JSON.

Se guarda y recupera el Refugio completo (animales, voluntarios, revisiones
y adopciones) con el gestor de contexto `with open(...)`.
"""

import json

from .gestor import Refugio
from .validacion import ChipAusenteError, ChipMalFormadoError, validar_chip


def guardar_refugio(refugio: Refugio, ruta: str) -> None:
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(refugio.to_dict(), f, ensure_ascii=False, indent=2)


def cargar_refugio(ruta: str) -> Refugio:
    with open(ruta, "r", encoding="utf-8") as f:
        datos = json.load(f)
    return Refugio.from_dict(datos)


def cargar_refugio_validando(ruta: str) -> tuple[Refugio, list[tuple[str, Exception]]]:
    """
    Carga el refugio validando cada animal. Los registros inválidos se
    descartan y se devuelven aparte (descripción, excepción); los válidos
    se cargan igualmente.
    """
    with open(ruta, "r", encoding="utf-8") as f:
        datos = json.load(f)

    validos: list[dict] = []
    rechazados: list[tuple[str, Exception]] = []

    for i, fila in enumerate(datos["animales"]):
        try:
            validar_chip(fila)
        # Primero los específicos, luego (si hiciera falta) los generales (Apartado 3)
        except ChipAusenteError as e:
            rechazados.append((f"animales[{i}]", e))
        except ChipMalFormadoError as e:
            rechazados.append((f"animales[{i}]", e))
        else:
            validos.append(fila)

    datos["animales"] = validos
    return Refugio.from_dict(datos), rechazados