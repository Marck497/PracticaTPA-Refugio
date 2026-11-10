import logging
from datetime import date
from .excepciones import AnimalNoEncontradoError, CapacidadSuperadaError, ReglaInclumplidaError
from .modelo import Adopcion, Adoptante, Animal, Voluntario
from .reglas import (
    AnimalDisponible,
    LimiteAdopciones,
    LimiteVoluntario,
    ReglaAdopcion,
    ReglaAsignacion
)

logger = logging.getLogger(__name__)

class Refugio:
    """Agregado raíz del dominio: coordina animales, voluntarios y adopciones"""

    def __init__(
            self,
            nombre: str,
            capacidad_maxima: int = None,
            animales: list[Animal] = None,
            voluntarios: list[Voluntario] = None,
            reglas_adopcion: list[ReglaAdopcion] = None,
            reglas_asignacion: list[ReglaAsignacion] = None,
    ):
        self.nombre = nombre

        # Evita el bug del argumento mutable (Apartado 3)
        self.animales: list[Animal] = animales if animales is not None else []
        self.voluntarios: list[Voluntario] = voluntarios if voluntarios is not None else []
        self.adopciones: list[Adopcion] = []

        # Reglas de negocio (Patrón Strategy): se pueden sustituir al crear el refugio
        self.reglas_adopcion: list[ReglaAdopcion] = (
            reglas_adopcion if reglas_adopcion is not None else [AnimalDisponible(), LimiteAdopciones()]
        )
        self.reglas_asignacion: list[ReglaAsignacion] = (
            reglas_asignacion if reglas_asignacion is not None else [LimiteVoluntario()]
        ) 

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
            logger.warning("Ingreso rechazado de %s: refugio lleno (%d)", animal.id_chip, self.capacidad_maxima)
            raise CapacidadSuperadaError(
                f"El refugio {self.nombre} ya está al límite de su capacidad "
                f"({self.capacidad_maxima} animales)."
            )

        if animal in self.animales:
            # Ya registrado
            return

        self.animales.append(animal)
        logger.info("Ingreso registrado: %s (%s)", animal.nombre, animal.id_chip)

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
        self._aplicar_reglas("Asignación", self.reglas_asignacion, animal, voluntario)
        if voluntario not in self.voluntarios:
            # Si el voluntario no está registrado lo añadimos
            self.voluntarios.append(voluntario)
        animal.asignar_voluntario(voluntario)
        logger.info("Voluntario %s asignado a %s", voluntario.nombre, id_chip)

    def tramitar_adopcion(
            self, id_chip: str, adoptante: Adoptante, fecha: date = None
    ) -> Adopcion:
        """
        Registra la adopción de un animal disponible por parte de un
        adoptante, y actualiza el estado del animal
        """
        animal = self.buscar_animal_por_chip(id_chip)
        self._aplicar_reglas("Adopción", self.reglas_adopcion, animal, adoptante)

        adopcion = Adopcion(animal=animal, adoptante=adoptante, fecha=fecha or date.today())
        self.adopciones.append(adopcion)
        animal.estado_adopcion = "adoptado"
        logger.info("Adopción registrada: %s por %s", id_chip, adoptante.nombre)
        return adopcion

    def eliminar_animal(self, animal: Animal) -> None:
        """Da de baja a un animal. No se puede si tiene adopciones registradas."""
        if animal not in self.animales:
            raise AnimalNoEncontradoError(f"El animal {animal.id_chip} no está en el refugio.")
        if any(a.animal == animal for a in self.adopciones):
            logger.warning("Baja rechazada: %s tiene adopciones registradas", animal.id_chip)
            raise ReglaInclumplidaError(
                f"No se puede eliminar a {animal.nombre} porque tiene una dopción registrada. "
                "Elimina primero la adopción"
            )
        self.animales.remove(animal)
        logger.info("Animal eliminado: %s (%s)", animal.nombre, animal.id_chip)

    def cancelar_adopcion(self, adopcion: Adopcion) -> None:
        """Elimina una adopción; si el animal no tiene otra, vuelve a estar disponible."""
        if adopcion not in self.adopciones:
            raise ValueError("Esa adopción no está registrada en el refugio.")
        self.adopciones.remove(adopcion)
        animal = adopcion.animal
        if not any(a.animal == animal for a in self.adopciones):
            animal.estado_adopcion = "disponible"
        logger.info("Adopción cancelada: %s (adoptante %s)", animal.id_chip, adopcion.adoptante.nombre)

    def desvincular_voluntario(self, voluntario: Voluntario, id_chip: str) -> None:
        """Quita un voluntario de un animal concreto, identificado por su chip."""
        animal = self.buscar_animal_por_chip(id_chip)
        if voluntario not in animal.voluntarios_asignados:
            raise ValueError(f"{voluntario.nombre} no está asignado al animal {id_chip}.")
        animal.deasignar_voluntario(voluntario)
        logger.info("Voluntario %s desvinculado de %s", voluntario.nombre, id_chip)

    def eliminar_voluntario(self, voluntario: Voluntario) -> None:
        """Da de baja a un voluntario y lo quita de todos los animales a los que estaba asignado"""
        if voluntario not in self.voluntarios:
            raise ValueError(f"{voluntario.nombre} no está registrado en el refugio.")
        for animal in self.animales:
            animal.deasignar_voluntario(voluntario)
        self.voluntarios.remove(voluntario)
        logger.info("Voluntario eliminado: %s", voluntario.nombre)

    def _aplicar_reglas(self, operacion: str, reglas: list, animal: Animal, persona) -> None:
        """Pasa todas las reglas. Si alguna falla, lo registra en el log y relanza el error"""
        for regla in reglas:
            try:
                regla.comprobar(self, animal, persona)
            except ReglaInclumplidaError as e:
                logger.warning("%s rechazada: %s", operacion, e)
                # raise para dejarlo seguir hacia arriba y conservar el traceback original
                raise

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

    def to_dict(self) -> dict: 
        # Voluntarios registrados + los asignados directamente a algún animal
        todos = {v.dni: v for v in self.voluntarios}
        for animal in self.animales:
            for v in animal.voluntarios_asignados:
                todos.setdefault(v.dni, v)
        return {
            "nombre": self.nombre,
            "capacidad_maxima": self.capacidad_maxima,
            "voluntarios": [v.to_dict() for v in todos.values()],
            "animales": [a.to_dict() for a in self.animales],
            "adopciones": [a.to_dict() for a in self.adopciones],
        }

    @classmethod
    def from_dict(cls, datos: dict) -> "Refugio":
        voluntarios = [Voluntario.from_dict(v) for v in datos["voluntarios"]]
        por_dni = {v.dni: v for v in voluntarios}
        animales = [Animal.from_dict(a, por_dni) for a in datos["animales"]]
        por_chip = {a.id_chip: a for a in animales}

        refugio = cls(
            nombre=datos["nombre"],
            capacidad_maxima=datos["capacidad_maxima"],
            animales=animales,
            voluntarios=voluntarios,
        )
        refugio.adopciones = [Adopcion.from_dict(a, por_chip) for a in datos["adopciones"]]
        return refugio

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Refugio):
            return NotImplemented
        return (
            self.nombre == other.nombre
            and self.capacidad_maxima == other.capacidad_maxima
            and self.animales == other.animales
            and self.voluntarios == other.voluntarios
            and self.adopciones == other.adopciones
        )

    def __repr__(self) -> str:
        return (
            f"Refugio(nombre={self.nombre!r}, animales={len(self.animales)}, "
            f"capacidad_maxima={self.capacidad_maxima})"
        )

    