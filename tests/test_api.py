"""Tests de la API pública del paquete (refugio/__init__.py)."""

import pytest

import refugio


@pytest.mark.parametrize("nombre", refugio.__all__)
def test_todo_lo_de_all_existe_en_el_paquete(nombre):
    assert hasattr(refugio, nombre)
