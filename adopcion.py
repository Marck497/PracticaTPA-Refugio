from datetime import date
from animal import Animal
from adoptante import Adoptante

class Adopcion:
    """
    Registro de que un Adoptante concreto adoptó un Animal concreto en una
    fecha determinada
    """

    def __init__(self, animal: Animal, adoptante: Adoptante, fecha: date):
        self.animal = animal
        self.adoptante = adoptante
        self.fecha = fecha

    def to_dict(self) -> dict:
        # El animal se guarda solo por su chip: así, al cargar, se enlaza
        # con el MISMO objeto Animal que ya está en el refugio (sin duplicarlo).
        return {
            "id_chip": self.animal.id_chip,
            "adoptante": self.adoptante.to_dict(),
            "fecha": self.fecha.isoformat(),
        }

    @classmethod
    def from_dict(cls, datos: dict, animales_por_chip: dict) -> "Adopcion":
        return cls(
            animal=animales_por_chip[datos["id_chip"]],
            adoptante=Adoptante.from_dict(datos["adoptante"]),
            fecha=date.fromisoformat(datos["fecha"]),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Adopcion):
            return NotImplemented
        return (self.animal == other.animal and self.adoptante == other.adoptante
                and self.fecha == other.fecha)

    def __repr__(self) -> str:
        return (
            f"Adopcion(animal={self.animal.id_chip!r}, "
            f"adoptante={self.adoptante.dni!r}, fecha={self.fecha!r})"
        )
