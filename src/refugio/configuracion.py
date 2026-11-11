"""Configuración de la aplicación: valores por defecto y archivo JSON opcional"""

import json
import logging
from dataclasses import dataclass, fields
from pathlib import Path

ARCHIVO_POR_DEFECTO = "config.json"

class ConfiguracionError(Exception):
    """El archivo de configuración no existe, no es JSON o tiene valores no válidos."""

@dataclass
class Configuracion:
    """Opciones de la aplicación. Cualquier clave que falte en el archivo usa su valor por defecto."""

    nivel_log: str = "INFO"
    archivo_log: str = "refugio.log"
    archivo_datos: str = "refugio.json"
    nombre_refugio: str = "Mi refugio"
    capacidad_maxima: int = 24

    def __post_init__(self) -> None:
        self.nivel_log = str(self.nivel_log).upper()
        if self.nivel_log not in logging.getLevelNamesMapping():
            raise ConfiguracionError(f"nivel_log no válido: {self.nivel_log!r}")
        for nombre in ("archivo_log", "archivo_datos", "nombre_refugio"):
            valor = getattr(self, nombre)
            if not isinstance(valor, str) or not valor.strip():
                raise ConfiguracionError(f"{nombre} debe ser un texto no vacío")
        if isinstance(self.capacidad_maxima, bool) or not isinstance(self.capacidad_maxima, int):
            raise ConfiguracionError("capacidad_maxima debe ser un número entero.")

def cargar_configuracion(ruta: str = None) -> Configuracion:
    """Lee la configuración.
    
    Con `ruta` el archivo debe existir. Sin ella, se usa `config.json` si está
    en la carpeta actual, sino, los valores por defecto.
    """
    if ruta is None:
        if not Path(ARCHIVO_POR_DEFECTO).exists():
            return Configuracion()
        ruta = ARCHIVO_POR_DEFECTO
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            datos = json.load(f)
    except FileNotFoundError:
        raise ConfiguracionError(f"No existe el archivo de configuración: {ruta}") from None
    except json.JSONDecodeError as e:
        raise ConfiguracionError(f"{ruta} no es un JSON válido: {e}") from None
    if not isinstance(datos, dict):
        raise ConfiguracionError(f"{ruta} debe contener un objeto JSON con las opciones")
    desconocidas = set(datos) - {campo.name for campo in fields(Configuracion)}
    if desconocidas:
        raise ConfiguracionError(f"Opciones desconocidas en {ruta}: {", ".join(sorted(desconocidas))}")
    return Configuracion(**datos)