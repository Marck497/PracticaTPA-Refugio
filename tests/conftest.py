"""Fixtures compartidas por todos los tests."""

from datetime import date

import pytest

from refugio import Adoptante, Animal, Refugio, RevisionVeterinaria, Voluntario


@pytest.fixture
def animal():
    return Animal("CHIP001", "Rex", "Perro", 22.5, "Macho", (2021, 3, 12))


@pytest.fixture
def adoptante():
    return Adoptante("90000005H", "Hugo", "611000005", "hugo@example.com")


@pytest.fixture
def voluntario():
    return Voluntario("00000001X", "Marcos", "600000001", "Perros")


@pytest.fixture
def revision():
    return RevisionVeterinaria(date(2026, 1, 10), "Revisión general", "Sano", "Ninguno")


@pytest.fixture
def refugio():
    """Refugio vacío con capacidad para 3 animales."""
    return Refugio("Refugio Esperanza", capacidad_maxima=3)


@pytest.fixture
def refugio_completo(animal, adoptante, voluntario, revision):
    """Refugio con animales, un voluntario, una revisión y una adopción."""
    r = Refugio("Refugio Esperanza", capacidad_maxima=10)
    r.registrar_ingreso(animal)
    r.registrar_ingreso(Animal("CHIP002", "Luna", "Gata", 4.1, "Hembra", (2022, 7, 1)))
    r.registrar_ingreso(Animal("CHIP003", "Toby", "Perro", 15.0, "Macho", (2020, 11, 23)))
    r.asignar_voluntario(voluntario, "CHIP001")
    animal.anadir_revision(revision)
    r.tramitar_adopcion("CHIP002", adoptante, date(2026, 9, 20))
    return r
