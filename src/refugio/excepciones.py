"""Excepciones propias del dominio del refugio."""


class RefugioError(Exception):
    """Base común de los errores del dominio (permite un único `except` en la UI)."""


class CapacidadSuperadaError(RefugioError):
    """Se lanza si se intenta ingresar un animal superando la capacidad máxima."""


class AnimalNoEncontradoError(RefugioError):
    """Se lanza cuando no se encuentra un animal por nombre o por chip."""

class ReglaInclumplidaError(RefugioError, ValueError):
    """Una regla de negocio impide la operación (límite alcanzado, animal no disponible...).
    
    Hereda también de ValueError para no romper el código que ya capturaba el ValueError.
    """