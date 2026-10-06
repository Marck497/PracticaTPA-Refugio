class Adoptante:
    """Persona que adopta (o ha adoptado) animales del refugio."""

    def __init__(self, dni: str, nombre: str, telefono: str, correo: str):
        self.dni = dni
        self.nombre = nombre
        self.telefono = telefono
        self.correo = correo

    def to_dict(self) -> dict:
        return {
            "dni": self.dni,
            "nombre": self.nombre,
            "telefono": self.telefono,
            "correo": self.correo,
        }

    @classmethod
    def from_dict(cls, datos: dict) -> "Adoptante":
        return cls(
            dni=datos["dni"],
            nombre=datos["nombre"],
            telefono=datos["telefono"],
            correo=datos["correo"],
        )

    def __repr__(self) -> str:
        return f"Adoptante(dni={self.dni!r}, nombre={self.nombre!r}, correo={self.correo!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Adoptante):
            return NotImplemented
        return self.dni == other.dni
