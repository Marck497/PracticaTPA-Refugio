from datetime import date

from revision_veterinaria import RevisionVeterinaria
from voluntario import Voluntario

class Animal:
    ESTADOS_ADOPCION_VALIDOS = {"disponible", "en_proceso", "adoptado", "no_disponible"}

    def __init__(
            self,
            id_chip: str,
            nombre: str,
            especie: str,
            peso: float,
            sexo: str,
            fecha_nacimiento: date,
            estado_adopcion: str = "disponible",
            historial_veterinario: list[RevisionVeterinaria] = None,
            voluntarios_asignados: list[Voluntario] = None
    ):
        self.id_chip = id_chip
        self.nombre = nombre
        self.especie = especie
        self.peso = peso
        self.sexo = sexo
        self.fecha_nacimiento = fecha_nacimiento
        self.estado_adopcion = estado_adopcion
        self.historial_veterinario = historial_veterinario if historial_veterinario is not None else []
        self.voluntarios_asignados = voluntarios_asignados if voluntarios_asignados is not None else []

    @property
    def id_chip(self) -> str:
        return self.__id_chip

    @id_chip.setter
    def id_chip(self, valor: str) -> None:
        if not valor.strip():
            raise ValueError("ERROR, el ID del chip no puede estar vacio")
        self.__id_chip = valor

    @property
    def edad(self) -> int:
        """Edad en años completos, se calcula con la fecha_nacimiento"""
        hoy = date.today()
        anios = hoy.year - self.fecha_nacimiento.year
        # SI no ha llegado al cumple, se quita un año
        if (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day):
            anios -= 1

        return anios

    def esta_disponible(self) -> bool:
        return self.estado_adopcion == "disponible"

    def anadir_revision(self, revision: RevisionVeterinaria) -> None:
        self.historial_veterinario.append(revision)

    def asignar_voluntario(self, voluntario: Voluntario) -> None:
        if voluntario not in self.voluntarios_asignados:
            self.voluntarios_asignados.append(voluntario)

    def __repr__(self) -> str:
        return (
            f"Animal(id_chip={self.id_chip!r}, nombre={self.nombre!r}, "
            f"especie={self.especie!r}, edad={self.edad}, "
            f"estado_adopcion={self.estado_adopcion!r})"
        )

    def __eq__(self, other: object) -> bool:
        # Identidad de dominio: el chip es único por animal.
        if not isinstance(other, Animal):
            return NotImplemented
        return self.id_chip == other.id_chip
