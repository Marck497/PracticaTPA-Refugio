"""Entidades del dominio: animales, personas, adopciones y revisiones."""

from .adopcion import Adopcion
from .adoptante import Adoptante
from .animal import Animal
from .revision_veterinaria import RevisionVeterinaria
from .voluntario import Voluntario
from .persona import Persona

__all__ = ["Adopcion", "Adoptante", "Animal", "Persona", "RevisionVeterinaria", "Voluntario"]