from .persona import Persona

class Voluntario(Persona):
    def __init__(self, dni, nombre, telefono, area_asignada, max_animales: int = 5):
        super().__init__(dni, nombre, telefono)
        if max_animales <= 0:
            raise ValueError("ERROR: max_animales debe ser positivo")
        self.area_asignada = area_asignada
        self.max_animales = max_animales

    def descripcion(self) -> str:
        return (f"Voluntario {self.nombre}: area {self.area_asignada}, "
                f"hasta {self.max_animales} animales")

    def to_dict(self) -> dict:
        return {
            "dni": self.dni,
            "nombre": self.nombre,
            "telefono": self.telefono,
            "area_asignada": self.area_asignada,
            "max_animales": self.max_animales,
        }

    @classmethod
    def from_dict(cls, datos: dict) -> "Voluntario": 
        return cls(
            dni=datos["dni"],
            nombre=datos["nombre"],
            telefono=datos["telefono"],
            area_asignada=datos["area_asignada"],
            max_animales=datos["max_animales"],
        )

    def __repr__(self) -> str:
        return f"Voluntario(dni={self.dni}, nombre={self.nombre}, area={self.area_asignada})"