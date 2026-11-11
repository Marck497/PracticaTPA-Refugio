"""Patrón Strategy: reglas de negocio intercambiables para adopciones y asignaciones.

Cada regla es una clase con un único método `comprobar`, que no devuelve nada y 
lanza `ReglaIncumplidaError` si la operación no está permitida. `Refugio` 
recorre su lista de reglas sin saber cuáles son, así que añadir, quitar o
sustituir una regla no obliga a tocar `Refugio`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from .excepciones import ReglaIncumplidaError

if TYPE_CHECKING:
    from .gestor import Refugio
    from .modelo import Adoptante, Animal, Voluntario

class ReglaAdopcion(ABC):
    """Condición que debe cumplirse para tramitar una adopción."""

    @abstractmethod
    def comprobar(seld, refugio: Refugio, animal: Animal, adoptante: Adoptante) -> None:
        """Lanza ReglaIncumplidaError si la adopción no está permitida."""

class AnimalDisponible(ReglaAdopcion):
    """Sólo se puede adoptar un animal disponible."""

    def comprobar(seld, refugio: Refugio, animal: Animal, adoptante: Adoptante) -> None:
        if not animal.esta_disponible():
            raise ReglaIncumplidaError(
                f"El animal '{animal.nombre}' (chip {animal.id_chip}) no está disponible "
                f"para adopción (estado actual: {animal.estado_adopcion})."
            )

class LimiteAdopciones(ReglaAdopcion):
    """Un adoptante no puede superar su `max_adopciones`."""

    def comprobar(seld, refugio: Refugio, animal: Animal, adoptante: Adoptante) -> None:
        previas = sum(1 for a in refugio.adopciones if a.adoptante == adoptante)
        if previas >= adoptante.max_adopciones:
            raise ReglaIncumplidaError(
                f"{adoptante.nombre} ya tiene {previas} adopciones y su máximo es "
                f"{adoptante.max_adopciones}."
            )

class ReglaAsignacion(ABC):
    """Condición que debe cumplirse para asignar un voluntario a un animal."""

    @abstractmethod
    def comprobar(self, refugio: Refugio, animal: Animal, voluntario: Voluntario) -> None:
        """Lanza ReglaIncumplidaError si la asignación no está permitida."""

class LimiteVoluntario(ReglaAsignacion):
    """Un voluntario no puede superar su `max_animales`."""

    def comprobar(self, refugio: Refugio, animal: Animal, voluntario: Voluntario) -> None:
        if voluntario in animal.voluntarios_asignados:
            # Ya lo tiene asignado.
            return

        asignados = sum(1 for a in refugio.animales if voluntario in a.voluntarios_asignados)
        if asignados >= voluntario.max_animales:
            raise ReglaIncumplidaError(
                f"{voluntario.nombre} ya tiene {asignados} animales asignados y su máximo es "
                f"{voluntario.max_animales}."
            )
