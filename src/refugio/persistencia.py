"""
Apartado 4.2 - Persistencia del modelo en JSON.

Se guarda y recupera el Refugio completo (animales, voluntarios, revisiones
y adopciones) con el gestor de contexto `with open(...)`.
"""

import json
import logging
import os

from .gestor import Refugio
from .validacion import ChipAusenteError, ChipMalFormadoError, validar_chip

logger = logging.getLogger(__name__)

def guardar_datos(datos: dict, ruta: str) -> None:
    """Escribe en disco un diccionario ya generado con `Refugio.to_dict()`.

    Se separa de `guradar_refugio` para poder hacer la "foto" de los datos en 
    el hilo de la interfaz y escribirla después en un hilo secundario.
    """
    temporal = f"{ruta}.tmp"
    with open(temporal, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    os.replace(temporal, ruta)
    logger.info("Refugio guardado en %s (%d animales)", ruta, len(datos["animales"]))

def guardar_refugio(refugio: Refugio, ruta: str) -> None:
    guardar_datos(refugio.to_dict(), ruta)


def cargar_refugio(ruta: str) -> Refugio:
    with open(ruta, "r", encoding="utf-8") as f:
        datos = json.load(f)
    refugio = Refugio.from_dict(datos)
    logger.info("Refugio cargado desde %s (%d animales)", ruta, len(refugio.animales))
    return refugio


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

    for donde, error in rechazados:
        logger.warning("Registro descartado en %s: %s", donde, error)

    datos["animales"] = validos
    refugio = Refugio.from_dict(datos)
    logger.info(
        "Refugio cargado desde %s (%d animales, %d descartados)",
        ruta, len(refugio.animales), len(rechazados)
    )
    return refugio, rechazados