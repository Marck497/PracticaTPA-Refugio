from .persona import Persona

class Adoptante(Persona):
    def __init__(self, dni, nombre, telefono, correo, max_adopciones: int = 3):
        super().__init__(dni, nombre, telefono)
        if max_adopciones <= 0:
            raise ValueError("ERROR: max_adopciones debe ser positivo")
        self.correo = correo
        self.max_adopciones = max_adopciones

    def descripcion(self) -> str:
        return (f"Adoptante {self.nombre} ({self.correo}): "
                f"puede adoptar hasta {self.max_adopciones} animales")

    def __repr__(self) -> str:  
        return f"Adoptante(dni={self.dni!r}, nombre={self.nombre!r}, correo={self.correo!r})"