"""
Apartado 4.2 - Persistencia del modelo en JSON.

Se guarda y recupera el Refugio completo (animales, voluntarios, revisiones
y adopciones) con el gestor de contexto `with open(...)`.
"""

import json

from .gestor import Refugio


def guardar_refugio(refugio: Refugio, ruta: str) -> None:
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(refugio.to_dict(), f, ensure_ascii=False, indent=2)


def cargar_refugio(ruta: str) -> Refugio:
    with open(ruta, "r", encoding="utf-8") as f:
        datos = json.load(f)
    return Refugio.from_dict(datos)