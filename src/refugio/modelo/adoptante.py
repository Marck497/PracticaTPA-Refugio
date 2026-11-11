"""Adoptante: persona que puede adoptar animales."""

from .persona import Persona

class Adoptante(Persona):
    """Persona que adopta animales, con un máximo de adopciones permitidas."""
    def __init__(self, dni, nombre, telefono, correo, max_adopciones: int = 3):
        super().__init__(dni, nombre, telefono)
        if max_adopciones <= 0:
            raise ValueError("ERROR: max_adopciones debe ser positivo")
        self.correo = correo
        self.max_adopciones = max_adopciones

    def descripcion(self) -> str:
        """Texto que describe al adoptante y cuántos animales puede adoptar."""
        return (f"Adoptante {self.nombre} ({self.correo}): "
                f"puede adoptar hasta {self.max_adopciones} animales")

    def to_dict(self) -> dict: 
        """Convierte el adoptante en un diccionario listo para guardarse como JSON."""
        return {
            "dni": self.dni,
            "nombre": self.nombre,
            "telefono": self.telefono,
            "correo": self.correo,
            "max_adopciones": self.max_adopciones,
        }

    @classmethod
    def from_dict(cls, datos: dict) -> "Adoptante": 
        """Reconstruye un adoptante a partir de un diccionario generado por `to_dict`."""
        return cls(
            dni=datos["dni"],
            nombre=datos["nombre"],
            telefono=datos["telefono"],
            correo=datos["correo"],
            max_adopciones=datos["max_adopciones"],
        )

    def __repr__(self) -> str:
        return f"Adoptante(dni={self.dni!r}, nombre={self.nombre!r}, correo={self.correo!r})"