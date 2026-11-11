"""Tests de las entidades: Animal, Persona, Voluntario, Adoptante, revisiones y adopciones."""

from datetime import date

import pytest

from refugio import (
    Adopcion,
    Adoptante,
    Animal,
    Persona,
    Resumible,
    RevisionVeterinaria,
    Voluntario,
)
from refugio.modelo import animal as modulo_animal


# Animal

def test_animal_nuevo_esta_disponible(animal):
    assert animal.esta_disponible()


def test_animal_adoptado_no_esta_disponible(animal):
    animal.estado_adopcion = "adoptado"
    assert not animal.esta_disponible()


def test_animal_empieza_sin_historial_ni_voluntarios(animal):
    assert animal.historial_veterinario == []
    assert animal.voluntarios_asignados == []


def test_animales_distintos_no_comparten_listas():
    a = Animal("CHIP001", "Rex", "Perro", 22.5, "Macho", (2021, 3, 12))
    b = Animal("CHIP002", "Luna", "Gata", 4.1, "Hembra", (2022, 7, 1))
    a.historial_veterinario.append("x")
    assert b.historial_veterinario == []


@pytest.mark.parametrize("chip", ["", "   "])
def test_chip_vacio_lanza_value_error(chip):
    with pytest.raises(ValueError):
        Animal(chip, "Rex", "Perro", 22.5, "Macho", (2021, 3, 12))


def test_cambiar_chip_a_vacio_lanza_value_error(animal):
    with pytest.raises(ValueError):
        animal.id_chip = ""


def test_cambiar_chip_valido(animal):
    animal.id_chip = "CHIP999"
    assert animal.id_chip == "CHIP999"


@pytest.mark.parametrize(
    "hoy, edad_esperada",
    [
        (date(2026, 3, 12), 5),  # el día del cumpleaños
        (date(2026, 3, 11), 4),  # el día anterior
        (date(2026, 12, 31), 5),
    ],
)
def test_edad_se_calcula_segun_la_fecha_de_hoy(monkeypatch, animal, hoy, edad_esperada):
    class FechaFija(date):
        @classmethod
        def today(cls):
            return hoy

    monkeypatch.setattr(modulo_animal, "date", FechaFija)
    assert animal.edad == edad_esperada


def test_anadir_revision_la_guarda_en_el_historial(animal, revision):
    animal.anadir_revision(revision)
    assert animal.historial_veterinario == [revision]


def test_asignar_voluntario_no_lo_duplica(animal, voluntario):
    animal.asignar_voluntario(voluntario)
    animal.asignar_voluntario(voluntario)
    assert animal.voluntarios_asignados == [voluntario]


def test_animales_con_mismo_chip_son_iguales(animal):
    otro = Animal("CHIP001", "Otro", "Gato", 1.0, "Hembra", (2020, 1, 1))
    assert animal == otro


def test_animales_con_distinto_chip_no_son_iguales(animal):
    otro = Animal("CHIP002", "Rex", "Perro", 22.5, "Macho", (2021, 3, 12))
    assert animal != otro


def test_animal_to_dict_y_from_dict_conservan_los_datos(animal, voluntario, revision):
    animal.asignar_voluntario(voluntario)
    animal.anadir_revision(revision)
    copia = Animal.from_dict(animal.to_dict(), {voluntario.dni: voluntario})
    assert copia.to_dict() == animal.to_dict()


def test_animal_from_dict_devuelve_la_fecha_como_tupla(animal):
    copia = Animal.from_dict(animal.to_dict(), {})
    assert copia.fecha_nacimiento == (2021, 3, 12)


def test_animal_to_dict_guarda_voluntarios_por_dni(animal, voluntario):
    animal.asignar_voluntario(voluntario)
    assert animal.to_dict()["voluntarios_asignados"] == ["00000001X"]


# Persona, Voluntario y Adoptante

def test_persona_es_abstracta():
    with pytest.raises(TypeError):
        Persona("00000000X", "Nadie", "600000000")


def test_voluntario_es_una_persona(voluntario):
    assert isinstance(voluntario, Persona)


def test_adoptante_es_una_persona(adoptante):
    assert isinstance(adoptante, Persona)


def test_descripcion_del_voluntario(voluntario):
    assert voluntario.descripcion() == "Voluntario Marcos: area Perros, hasta 5 animales"


def test_descripcion_del_adoptante(adoptante):
    assert adoptante.descripcion() == (
        "Adoptante Hugo (hugo@example.com): puede adoptar hasta 3 animales"
    )


def test_voluntarios_con_mismo_dni_son_iguales(voluntario):
    assert voluntario == Voluntario("00000001X", "Otro nombre", "0", "Gatos")


def test_voluntarios_con_distinto_dni_no_son_iguales(voluntario):
    assert voluntario != Voluntario("00000002X", "Marcos", "600000001", "Perros")


def test_voluntario_y_adoptante_con_mismo_dni_no_son_iguales(voluntario):
    adoptante = Adoptante(voluntario.dni, "Marcos", "600000001", "m@example.com")
    assert voluntario != adoptante


@pytest.mark.parametrize("maximo", [0, -1])
def test_voluntario_max_animales_no_positivo_lanza_value_error(maximo):
    with pytest.raises(ValueError):
        Voluntario("00000001X", "Marcos", "600000001", "Perros", max_animales=maximo)


@pytest.mark.parametrize("maximo", [0, -1])
def test_adoptante_max_adopciones_no_positivo_lanza_value_error(maximo):
    with pytest.raises(ValueError):
        Adoptante("90000005H", "Hugo", "611000005", "h@example.com", max_adopciones=maximo)


def test_voluntario_to_dict_y_from_dict(voluntario):
    copia = Voluntario.from_dict(voluntario.to_dict())
    assert copia.to_dict() == voluntario.to_dict()


def test_adoptante_to_dict_y_from_dict(adoptante):
    copia = Adoptante.from_dict(adoptante.to_dict())
    assert copia.to_dict() == adoptante.to_dict()


# Revisiones y adopciones

def test_revision_to_dict_guarda_la_fecha_en_iso(revision):
    assert revision.to_dict()["fecha"] == "2026-01-10"


def test_revision_to_dict_y_from_dict(revision):
    assert RevisionVeterinaria.from_dict(revision.to_dict()) == revision


def test_revision_resumen(revision):
    assert revision.resumen() == (
        "Revisión veterinaria del 2026-01-10: Revisión general - "
        "diagnóstico: Sano, tratamiento: Ninguno"
    )


def test_adopcion_resumen(animal, adoptante):
    adopcion = Adopcion(animal, adoptante, date(2026, 9, 20))
    assert adopcion.resumen() == "Adopción: Rex adoptado/a por Hugo el 2026-09-20"


def test_adopcion_from_dict_enlaza_el_mismo_animal(animal, adoptante):
    adopcion = Adopcion(animal, adoptante, date(2026, 9, 20))
    copia = Adopcion.from_dict(adopcion.to_dict(), {animal.id_chip: animal})
    assert copia.animal is animal
    assert copia == adopcion


def test_revision_cumple_el_protocolo_resumible(revision):
    assert isinstance(revision, Resumible)


def test_adopcion_cumple_el_protocolo_resumible(animal, adoptante):
    assert isinstance(Adopcion(animal, adoptante, date(2026, 9, 20)), Resumible)


def test_animal_no_cumple_el_protocolo_resumible(animal):
    assert not isinstance(animal, Resumible)


@pytest.mark.parametrize("estado", sorted(Animal.ESTADOS_ADOPCION_VALIDOS))
def test_estado_de_adopcion_valido(animal, estado):
    animal.estado_adopcion = estado
    assert animal.estado_adopcion == estado


@pytest.mark.parametrize("estado", ["", "Disponible", "vendido"])
def test_estado_de_adopcion_invalido_lanza_value_error(animal, estado):
    with pytest.raises(ValueError):
        animal.estado_adopcion = estado


def test_crear_animal_con_estado_invalido_lanza_value_error():
    with pytest.raises(ValueError):
        Animal("CHIP001", "Rex", "Perro", 22.5, "Macho", (2021, 3, 12), estado_adopcion="x")


def test_deasignar_voluntario_lo_quita(animal, voluntario):
    animal.asignar_voluntario(voluntario)
    animal.deasignar_voluntario(voluntario)
    assert animal.voluntarios_asignados == []


def test_deasignar_voluntario_no_asignado_no_falla(animal, voluntario):
    animal.deasignar_voluntario(voluntario)
    assert animal.voluntarios_asignados == []
