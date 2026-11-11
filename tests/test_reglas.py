"""Tests de las reglas de negocio (patrón Strategy)."""

import pytest

from refugio import Adoptante, Animal, Refugio, Voluntario
from refugio.excepciones import ReglaInclumplidaError
from refugio.reglas import (
    AnimalDisponible,
    LimiteAdopciones,
    LimiteVoluntario,
    ReglaAdopcion,
    ReglaAsignacion,
)


def nuevo_animal(n: int) -> Animal:
    return Animal(f"CHIP{n:03d}", f"Animal{n}", "Perro", 10.0, "Macho", (2020, 1, 1))


@pytest.fixture
def refugio_con_animales():
    r = Refugio("R", capacidad_maxima=10)
    for i in range(1, 4):
        r.registrar_ingreso(nuevo_animal(i))
    return r


def test_reglas_por_defecto_del_refugio():
    r = Refugio("R", capacidad_maxima=1)
    assert [type(x) for x in r.reglas_adopcion] == [AnimalDisponible, LimiteAdopciones]
    assert [type(x) for x in r.reglas_asignacion] == [LimiteVoluntario]


@pytest.mark.parametrize("clase", [ReglaAdopcion, ReglaAsignacion])
def test_las_reglas_base_son_abstractas(clase):
    with pytest.raises(TypeError):
        clase()


# AnimalDisponible

def test_animal_disponible_deja_pasar_un_animal_disponible(refugio, animal, adoptante):
    AnimalDisponible().comprobar(refugio, animal, adoptante)


def test_animal_disponible_rechaza_un_animal_adoptado(refugio, animal, adoptante):
    animal.estado_adopcion = "adoptado"
    with pytest.raises(ReglaInclumplidaError):
        AnimalDisponible().comprobar(refugio, animal, adoptante)


# LimiteAdopciones

def test_adoptante_puede_adoptar_hasta_su_maximo(refugio_con_animales):
    adoptante = Adoptante("11111111A", "Paco", "600", "p@example.com", max_adopciones=2)
    refugio_con_animales.tramitar_adopcion("CHIP001", adoptante)
    refugio_con_animales.tramitar_adopcion("CHIP002", adoptante)
    assert len(refugio_con_animales.adopciones) == 2


def test_adoptante_no_puede_superar_su_maximo(refugio_con_animales):
    adoptante = Adoptante("11111111A", "Paco", "600", "p@example.com", max_adopciones=1)
    refugio_con_animales.tramitar_adopcion("CHIP001", adoptante)
    with pytest.raises(ReglaInclumplidaError):
        refugio_con_animales.tramitar_adopcion("CHIP002", adoptante)


def test_limite_de_adopciones_cuenta_por_dni(refugio_con_animales):
    refugio_con_animales.tramitar_adopcion(
        "CHIP001", Adoptante("11111111A", "Paco", "600", "p@example.com", max_adopciones=1)
    )
    mismo_dni = Adoptante("11111111A", "Francisco", "700", "f@example.com", max_adopciones=1)
    with pytest.raises(ReglaInclumplidaError):
        refugio_con_animales.tramitar_adopcion("CHIP002", mismo_dni)


def test_adopcion_rechazada_no_cambia_el_estado_del_animal(refugio_con_animales):
    adoptante = Adoptante("11111111A", "Paco", "600", "p@example.com", max_adopciones=1)
    refugio_con_animales.tramitar_adopcion("CHIP001", adoptante)
    with pytest.raises(ReglaInclumplidaError):
        refugio_con_animales.tramitar_adopcion("CHIP002", adoptante)
    assert refugio_con_animales.buscar_animal_por_chip("CHIP002").esta_disponible()


# LimiteVoluntario

def test_voluntario_no_puede_superar_su_maximo(refugio_con_animales):
    voluntario = Voluntario("00000009X", "Ana", "600", "Perros", max_animales=2)
    refugio_con_animales.asignar_voluntario(voluntario, "CHIP001")
    refugio_con_animales.asignar_voluntario(voluntario, "CHIP002")
    with pytest.raises(ReglaInclumplidaError):
        refugio_con_animales.asignar_voluntario(voluntario, "CHIP003")


def test_reasignar_al_mismo_animal_no_cuenta_para_el_limite(refugio_con_animales):
    voluntario = Voluntario("00000009X", "Ana", "600", "Perros", max_animales=1)
    refugio_con_animales.asignar_voluntario(voluntario, "CHIP001")
    refugio_con_animales.asignar_voluntario(voluntario, "CHIP001")
    assert refugio_con_animales.buscar_animal_por_chip("CHIP001").voluntarios_asignados == [
        voluntario
    ]


def test_asignacion_rechazada_no_registra_al_voluntario(refugio_con_animales):
    voluntario = Voluntario("00000009X", "Ana", "600", "Perros", max_animales=1)
    refugio_con_animales.reglas_asignacion = [ReglaQueSiempreFalla()]
    with pytest.raises(ReglaInclumplidaError):
        refugio_con_animales.asignar_voluntario(voluntario, "CHIP001")
    assert refugio_con_animales.voluntarios == []


# Sustituir reglas

class ReglaQueSiempreFalla(ReglaAdopcion, ReglaAsignacion):
    def comprobar(self, refugio, animal, persona):
        raise ReglaInclumplidaError("prohibido")


def test_se_pueden_quitar_todas_las_reglas_de_adopcion(animal, adoptante):
    r = Refugio("R", capacidad_maxima=5, reglas_adopcion=[])
    animal.estado_adopcion = "adoptado"
    r.registrar_ingreso(animal)
    r.tramitar_adopcion("CHIP001", adoptante)
    assert len(r.adopciones) == 1


def test_se_puede_anadir_una_regla_nueva_sin_tocar_refugio(animal, adoptante):
    r = Refugio("R", capacidad_maxima=5, reglas_adopcion=[ReglaQueSiempreFalla()])
    r.registrar_ingreso(animal)
    with pytest.raises(ReglaInclumplidaError, match="prohibido"):
        r.tramitar_adopcion("CHIP001", adoptante)
