"""Animal: entidad principal del refugio, con su historial veterinario y sus voluntarios."""

from datetime import date
from .revision_veterinaria import RevisionVeterinaria
from .voluntario import Voluntario

class Animal:
    """Animal del refugio, identificado por su chip: dos animales con el mismo chip son iguales."""
    ESTADOS_ADOPCION_VALIDOS = {"disponible", "en_proceso", "adoptado", "no_disponible"}

    def __init__(
            self,
            id_chip: str,
            nombre: str,
            especie: str,
            peso: float,
            sexo: str,
            fecha_nacimiento: tuple[int, int, int],
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
        """Identificador único del animal (no puede estar vacío)."""
        return self.__id_chip

    @id_chip.setter
    def id_chip(self, valor: str) -> None:
        if not valor.strip():
            raise ValueError("ERROR, el ID del chip no puede estar vacio")
        self.__id_chip = valor

    @property
    def estado_adopcion(self) -> str:
        """Estado de adopción del animal: uno de `ESTADOS_ADOPCION_VALIDOS`."""
        return self.__estado_adopcion

    @estado_adopcion.setter
    def estado_adopcion(self, valor: str) -> None:
        if valor not in self.ESTADOS_ADOPCION_VALIDOS:
            validos = ", ".join(sorted(self.ESTADOS_ADOPCION_VALIDOS))
            raise ValueError(f"Estado de adopción no válido: '{valor}'. Estados posibles: {validos}.")
        self.__estado_adopcion = valor

    @property
    def edad(self) -> int:
        """Edad en años completos, calculada dinámicamente desde la tupla (año, mes, día)"""
        hoy = date.today()
        anios = hoy.year - self.fecha_nacimiento[0]
        
        if (hoy.month, hoy.day) < (self.fecha_nacimiento[1], self.fecha_nacimiento[2]):
            anios -= 1

        return anios

    def esta_disponible(self) -> bool:
        """Indica si el animal se puede adoptar (estado `disponible`)."""
        return self.estado_adopcion == "disponible"

    def anadir_revision(self, revision: RevisionVeterinaria) -> None:
        """Añade una revisión veterinaria al historial del animal."""
        self.historial_veterinario.append(revision)

    def asignar_voluntario(self, voluntario: Voluntario) -> None:
        """Asigna un voluntario al animal si no lo estaba ya."""
        if voluntario not in self.voluntarios_asignados:
            self.voluntarios_asignados.append(voluntario)

    def deasignar_voluntario(self, voluntario: Voluntario) -> None:
        """Quita un voluntario del animal; no hace nada si no estaba asignado."""
        if voluntario in self.voluntarios_asignados:
            self.voluntarios_asignados.remove(voluntario)

    def to_dict(self) -> dict:  
        """Convierte el animal en un diccionario. Los voluntarios se guardan solo por DNI."""
        # Los voluntarios se guardan solo por DNI (referencia), no copiados.
        return {
            "id_chip": self.id_chip,
            "nombre": self.nombre,
            "especie": self.especie,
            "peso": self.peso,
            "sexo": self.sexo,
            "fecha_nacimiento": list(self.fecha_nacimiento),
            "estado_adopcion": self.estado_adopcion,
            "historial_veterinario": [r.to_dict() for r in self.historial_veterinario],
            "voluntarios_asignados": [v.dni for v in self.voluntarios_asignados],
        }

    @classmethod
    def from_dict(cls, datos: dict, voluntarios_por_dni: dict) -> "Animal": 
        """Reconstruye un animal enlazando con los voluntarios ya creados (`voluntarios_por_dni`)."""
        return cls(
            id_chip=datos["id_chip"],
            nombre=datos["nombre"],
            especie=datos["especie"],
            peso=datos["peso"],
            sexo=datos["sexo"],
            # JSON no tiene tuplas: llega como lista y hay que volver a tupla
            fecha_nacimiento=tuple(datos["fecha_nacimiento"]),
            estado_adopcion=datos["estado_adopcion"],
            historial_veterinario=[
                RevisionVeterinaria.from_dict(r) for r in datos["historial_veterinario"]
            ],
            voluntarios_asignados=[
                voluntarios_por_dni[dni] for dni in datos["voluntarios_asignados"]
            ],
        )

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