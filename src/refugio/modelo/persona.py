from abc import ABC, abstractmethod

class Persona(ABC):
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