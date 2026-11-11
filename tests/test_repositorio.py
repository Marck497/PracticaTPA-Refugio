"""Tests de Repositorio[T]."""

import pytest

from refugio import Animal, Voluntario
from refugio.repositorio import ElementoDuplicadoError, ElementoNoEncontradoError, Repositorio


@pytest.fixture
def repo_animales(animal):
    repo: Repositorio[Animal] = Repositorio(lambda a: a.id_chip)
    repo.anadir(animal)
    return repo


def test_repositorio_nuevo_esta_vacio():
    repo: Repositorio[Animal] = Repositorio(lambda a: a.id_chip)
    assert len(repo) == 0
    assert repo.todos() == []


def test_anadir_aumenta_el_tamano(repo_animales):
    assert len(repo_animales) == 1


def test_obtener_por_clave(repo_animales, animal):
    assert repo_animales.obtener("CHIP001") is animal


def test_obtener_clave_inexistente_lanza_error(repo_animales):
    with pytest.raises(ElementoNoEncontradoError):
        repo_animales.obtener("CHIP999")


def test_anadir_duplicado_lanza_error(repo_animales, animal):
    with pytest.raises(ElementoDuplicadoError):
        repo_animales.anadir(animal)


def test_contains_por_clave(repo_animales):
    assert "CHIP001" in repo_animales
    assert "CHIP999" not in repo_animales


def test_eliminar_devuelve_el_elemento(repo_animales, animal):
    assert repo_animales.eliminar("CHIP001") is animal


def test_eliminar_lo_quita_del_repositorio(repo_animales):
    repo_animales.eliminar("CHIP001")
    assert "CHIP001" not in repo_animales


def test_eliminar_clave_inexistente_lanza_error(repo_animales):
    with pytest.raises(ElementoNoEncontradoError):
        repo_animales.eliminar("CHIP999")


def test_iterar_respeta_el_orden_de_insercion():
    repo: Repositorio[Voluntario] = Repositorio(lambda v: v.dni)
    nombres = ["Marcos", "Maria", "Gonzalo", "Miguel", "Hugo"]
    for i, nombre in enumerate(nombres, start=1):
        repo.anadir(Voluntario(f"0000000{i}X", nombre, f"60000000{i}", "Perros"))
    assert [v.nombre for v in repo] == nombres


def test_mismo_repositorio_sirve_para_voluntarios(voluntario):
    repo: Repositorio[Voluntario] = Repositorio(lambda v: v.dni)
    repo.anadir(voluntario)
    assert repo.obtener("00000001X") is voluntario


def test_repr_muestra_el_numero_de_elementos(repo_animales):
    assert repr(repo_animales) == "Repositorio(1 elementos)"
