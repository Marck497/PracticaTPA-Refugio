"""Configuración del logging de la aplicación (consola + archivo)"""

import logging

FORMATO = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

def configurar_logging(nivel: str = "INFO", archivo: str = "refugio.log") -> None:
    """Se llama una sola vez al arrancar. Envía los logs a consola y a archivo"""
    logging.basicConfig(
        level=nivel,
        format=FORMATO,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(archivo, encoding="utf-8"),
        ],
    )