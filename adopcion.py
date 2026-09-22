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

    def __repr__(self) -> str:
        return (
            f"Adopcion(animal={self.animal.id_chip!r}, "
            f"adoptante={self.adoptante.dni!r}, fecha={self.fecha!r})"
        ) 