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

    def __repr__(self) -> str:  
        return f"Voluntario(dni={self.dni}, nombre={self.nombre}, area={self.area_asignada})"