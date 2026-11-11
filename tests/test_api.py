"""Tests de la API pública del paquete (refugio/__init__.py)."""

import pytest

import refugio


@pytest.mark.parametrize("nombre", refugio.__all__)
def test_todo_lo_de_all_existe_en_el_paquete(nombre):
    assert hasattr(refugio, nombre)


def test_nombre_antiguo_de_regla_incumplida_sigue_funcionando():
    from refugio.excepciones import ReglaInclumplidaError, ReglaIncumplidaError

    assert ReglaInclumplidaError is ReglaIncumplidaError
