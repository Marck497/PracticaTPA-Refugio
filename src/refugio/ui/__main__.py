"""Lanza la interfaz con datos de demostración: python -m refugio.ui [--demo] [--config RUTA]"""

import argparse
import logging
import shutil
import sys
from pathlib import Path

from ..configuracion import Configuracion, ConfiguracionError, cargar_configuracion
from ..demo import construir_refugio_demo
from ..gestor import Refugio
from ..persistencia import cargar_refugio_validando
from ..registro import configurar_logging
from .app import App

logger = logging.getLogger(__name__)

def crear_parser() -> argparse.ArgumentParser:
    """Crea el analizador de argumentos de la línea de comandos."""

    parser = argparse.ArgumentParser(
        prog="python -m refugio.ui", 
        description="Gestión de un refugio de animales (interfaz gráfica)."
    )
    parser.add_argument(
        "--demo", action="store_true",
        help="arranca con datos de demostración; no lee ni escribe el archivo de datos.",
    )
    parser.add_argument(
        "--config", metavar="RUTA",
        help="archivo de configuración JSON (poor defecto config.json si existe)",
    )
    return parser

def crear_o_cargar_refugio(config: Configuracion) -> Refugio:
    """Carga el archivo de datos; si todavía no existe, empieza con un refugio vacío."""

    ruta = Path(config.archivo_datos)
    if not ruta.exists():
        logger.info("No existe %s: se empieza con un refugio vacío", ruta)
        try:
            return Refugio(config.nombre_refugio, capacidad_maxima=config.capacidad_maxima)
        except ValueError as e:
            raise ConfiguracionError(f"capacidad_maxima no válida: {e}") from None
    refugio, rechazados = cargar_refugio_validando(str(ruta))
    if rechazados: # al guardar se perderían: dejamos una copia del original
        copia = f"{ruta}.bak"
        shutil.copy(ruta, copia)
        logger.warning("%d registros descartados; copia del archivo original en %s", len(rechazados), copia)
    return refugio

def main(argv: list[str] = None) -> None:
    """Punto de entrada: lee los argumentos y la configuración y abre la ventana."""

    parser = crear_parser()
    args = parser.parse_args(argv)
    try:
        config = cargar_configuracion(args.config)
    except ConfiguracionError as e:
        parser.error(str(e))
    configurar_logging(config.nivel_log, config.archivo_log)

    if args.demo:
        logger.info("Modo demo: datos de ejemplo, sin leer ni guardar el archivo de datos")
        App(construir_refugio_demo()).mainloop()
        return
    try:
        refugio = crear_o_cargar_refugio(config)
    except ConfiguracionError as e:
        parser.error(str(e))
    except (OSError, ValueError, KeyError, TypeError) as e:
        # No arrancamos. Si lo hacemos, al cerrar se sobrescribe el archivo con datos vacíos
        logger.error("No se pudo cargar %s: %s", config.archivo_datos, e)
        sys.exit(f"No se pudo cargar {config.archivo_datos}: {e}\nRevisa o mueve ese archivo para no perder datos.")
    App(refugio, config.archivo_datos).mainloop()

if __name__ == "__main__":
    main()