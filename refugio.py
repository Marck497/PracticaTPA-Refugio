from datetime import date
from animal import Animal
from adoptante import Adoptante
from adopcion import Adopcion
from voluntario import Voluntario

class CapacidadSuperadaError(Exception):
    """Se lanza si se intenta ingresar un animal superando la capacidad máxima."""

class AnimalNoEncontradoError(Exception):
    """Se lanza cuando no se encientra un animal por nombre o por chip"""

class Refugio:
    """Agregado raíz del dominio: coordina animales, voluntarios y adopciones"""

    def __init__(
            self,
            nombre: str,
            capacidad_maxima: int = None,
            animales: list[Animal] = None,
            voluntarios: list[Voluntario] = None,
    ):
        self.nombre = nombre

        # Evita el bug del argumento mutable (Apartado 3)
        self.animales: list[Animal] = animales if animales is not None else []
        self.voluntarios: list[Voluntario] = voluntarios if voluntarios is not None else []
        self.adopciones: list[Adopcion] = []

        # Si no se indica capacidad explícita, se deriva de la ocupación 
        # inicial. (Como lo que pide el ejemplo del enunciad de los 8 casos
        # de prueba y tal)
        if capacidad_maxima is not None:
            self.capacidad_maxima = capacidad_maxima
        else:
            self.capacidad_maxima = max(len(self.animales) * 3, 1)

    @property
    def capacidad_maxima(self) -> int:
        return self.__capacidad_maxima

    @capacidad_maxima.setter
    def capacidad_maxima(self, valor: int) -> None:
        if valor < 0:
            raise ValueError("ERROR: La capacidad maxima no puede ser negativa")
        if valor > 24:
            raise ValueError("ERROR: La capacidad maxima no puede ser mas de 24")
        self.__capacidad_maxima = valor


    def registrar_ingreso(self, animal: Animal) -> None:
        """Da de alta un animal en el refugio, respetando la capacidad máxima"""
        if len(self.animales) >= self.capacidad_maxima:
            raise CapacidadSuperadaError(
                f"El refugio {self.nombre} ya está al límite de su capacidad "
                f"({self.capacidad_maxima} animales)."
            )

        if animal in self.animales:
            # Ya registrado
            return

        self.animales.append(animal)

    def mostrar_animal(self, nombre: str) -> str:
        """Devuelve una ficha legible del primer animal que coincide con ese nombre"""
        animal = self.buscar_animal(nombre)
        return (
            f"Chip: {animal.id_chip}\n"
            f"Nombre: {animal.nombre}\n"
            f"Especie: {animal.especie}\n"
            f"Sexo: {animal.sexo}\n"
            f"Peso: {animal.peso} kg\n"
            f"Edad: {animal.edad} años\n"
            f"Estado de adopción: {animal.estado_adopcion}\n"
            f"Revisiones veterinarias: {len(animal.historial_veterinario)}\n"
            f"Voluntarios asignados: {[v.nombre for v in animal.voluntarios_asignados]}"
        )

    def buscar_animal(self, nombre: str) -> Animal:
        """Busca un animal por su nombre"""
        for animal in self.animales:
            if animal.nombre.lower() == nombre.lower():
                return animal

        raise AnimalNoEncontradoError(f"No hay ningún animal con el nombre: {nombre}")

    def buscar_animal_por_chip(self, id_chip: str) -> Animal:
        """Busca un animal por su identificador de chip"""
        for animal in self.animales:
            if animal.id_chip == id_chip:
                return animal

        raise AnimalNoEncontradoError(f"No hay ningún animal con id_chip: {id_chip}")

    def asignar_voluntario(self, voluntario: Voluntario, id_chip: str) -> None:
        """Asigna un voluntario a un animal concreto, identificado por su chip"""
        animal = self.buscar_animal_por_chip(id_chip)
        if voluntario not in self.voluntarios:
            # Si el voluntario no está registrado lo añadimos
            self.voluntarios.append(voluntario)
        animal.asignar_voluntario(voluntario)

    def tramitar_adopcion(
            self, id_chip: str, adoptante: Adoptante, fecha: date = None
    ) -> Adopcion:
        """
        Registra la adopción de un animal disponible por parte de un
        adoptante, y actualiza el estado del animal
        """
        animal = self.buscar_animal_por_chip(id_chip)
        if not animal.esta_disponible():
            raise ValueError(
                f"El animal '{animal.nombre}' (chip {id_chip}) no está disponible "
                f"para adopción (estado actual: {animal.estado_adopcion})."
            )

        adopcion = Adopcion(animal=animal, adoptante=adoptante, fecha=fecha or date.today())
        self.adopciones.append(adopcion)
        animal.estado_adopcion = "adoptado"
        return adopcion

    def informe_actividad(self) -> str:
        """Resumen de la actividad del refugio: ocupación, adopciones y equipo."""
        disponibles = sum(1 for a in self.animales if a.esta_disponible())
        adoptados = sum(1 for a in self.animales if a.estado_adopcion == "adoptado")
        return (
            f"Informe de actividad — Refugio '{self.nombre}'\n"
            f"Ocupación: {len(self.animales)}/{self.capacidad_maxima}\n"
            f"Animales disponibles: {disponibles}\n"
            f"Animales adoptados: {adoptados}\n"
            f"Adopciones tramitadas (histórico): {len(self.adopciones)}\n"
            f"Voluntarios activos: {len(self.voluntarios)}"
        )

    def __repr__(self) -> str:
        return (
            f"Refugio(nombre={self.nombre!r}, animales={len(self.animales)}, "
            f"capacidad_maxima={self.capacidad_maxima})"
        )

    