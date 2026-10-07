"""
Gestor de refugio de animales.

API pública del paquete: cualquier interfaz (CLI, GUI, web) debería importar
solo desde aquí, p. ej.::

    from refugio import Refugio, Animal, Adoptante
"""

from .excepciones import AnimalNoEncontradoError, CapacidadSuperadaError, RefugioError
from .gestor import Refugio
from .modelo import Adopcion, Adoptante, Animal, RevisionVeterinaria, Voluntario
from .protocolos import Resumible, mostrar_resumen

__version__ = "0.2.0"

__all__ = [
    "Refugio",
    "Animal",
    "Adoptante",
    "Voluntario",
    "Adopcion",
    "RevisionVeterinaria",
    "Resumible",
    "mostrar_resumen",
    "RefugioError",
    "CapacidadSuperadaError",
    "AnimalNoEncontradoError",
    "__version__",
]