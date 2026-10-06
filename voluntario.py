class Voluntario:
    """
    Persona que colabora en el refugio ciudando animales.
    """

    def __init__(self, dni: str, nombre: str, telefono: str, area_asignada: str):
        self.dni = dni
        self.nombre = nombre
        self.telefono = telefono
        self.area_asignada = area_asignada

    def to_dict(self) -> dict:
        return {
            "dni": self.dni,
            "nombre": self.nombre,
            "telefono": self.telefono,
            "area_asignada": self.area_asignada,
        }

    @classmethod
    def from_dict(cls, datos: dict) -> "Voluntario":
        return cls(
            dni=datos["dni"],
            nombre=datos["nombre"],
            telefono=datos["telefono"],
            area_asignada=datos["area_asignada"],
        )

    def __repr__(self) -> str:
        return f"Voluntario(dni={self.dni}, nombre={self.nombre}, area={self.area_asignada})"

    def __eq__(self, other: object) -> bool:
        # Dos voluntarios son "el mismo" si comparten DNI
        if not isinstance(other, Voluntario):
            return NotImplemented
        return self.dni == other.dni
