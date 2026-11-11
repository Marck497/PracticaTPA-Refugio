"""Persona: clase base abstracta de voluntarios y adoptantes."""

from abc import ABC, abstractmethod

class Persona(ABC):
    """Persona del refugio, identificada por su DNI. Clase base abstracta de `Voluntario` y `Adoptante`."""
    def __init__(self, dni: str, nombre: str, telefono: str):
        self.dni = dni
        self.nombre = nombre
        self.telefono = telefono

    @abstractmethod
    def descripcion(self) -> str:
        """Cada tipo de persona se describe a su manera."""

    def __eq__(self, other: object) -> bool:
        if type(self) is not type(other):
            return NotImplemented
        return self.dni == other.dni