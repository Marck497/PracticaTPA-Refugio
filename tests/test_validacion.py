"""Tests del patrón del chip y de validar_chip()."""

import pytest

from refugio.validacion import (
    CHIP,
    ChipAusenteError,
    ChipMalFormadoError,
    RegistroInvalido,
    validar_chip,
)


@pytest.mark.parametrize("chip", ["CHIP000", "CHIP001", "CHIP999"])
def test_chip_valido_encaja_con_el_patron(chip):
    assert CHIP.match(chip)


@pytest.mark.parametrize(
    "chip",
    [
        "chip001",    # minúsculas
        "CHIP01",     # faltan dígitos
        "CHIP0011",   # sobran dígitos
        "XCHIP001",   # texto delante
        "CHIP001 ",   # espacio detrás
        "CHIPABC",    # letras en lugar de dígitos
        "",
    ],
)
def test_chip_invalido_no_encaja_con_el_patron(chip):
    assert not CHIP.match(chip)


def test_validar_chip_devuelve_el_chip_valido():
    assert validar_chip({"id_chip": "CHIP001", "nombre": "Rex"}) == "CHIP001"


@pytest.mark.parametrize("chip", ["chip001", "CHIP01", ""])
def test_validar_chip_mal_formado_lanza_error(chip):
    with pytest.raises(ChipMalFormadoError):
        validar_chip({"id_chip": chip})


@pytest.mark.parametrize("chip", [None, 1, ["CHIP001"]])
def test_validar_chip_que_no_es_texto_lanza_error(chip):
    with pytest.raises(ChipMalFormadoError):
        validar_chip({"id_chip": chip})


def test_validar_registro_sin_chip_lanza_error():
    with pytest.raises(ChipAusenteError):
        validar_chip({"nombre": "Simba"})


def test_mensaje_de_chip_ausente_incluye_el_nombre():
    with pytest.raises(ChipAusenteError, match="Simba"):
        validar_chip({"nombre": "Simba"})


@pytest.mark.parametrize("error", [ChipMalFormadoError, ChipAusenteError])
def test_errores_de_chip_heredan_de_registro_invalido(error):
    assert issubclass(error, RegistroInvalido)
