"""Tests de guardar y cargar el refugio en JSON (con y sin validación)."""

import json
import logging
from datetime import date

import pytest

from refugio.persistencia import cargar_refugio, cargar_refugio_validando, guardar_refugio
from refugio.validacion import ChipAusenteError, ChipMalFormadoError


@pytest.fixture
def ruta(tmp_path):
    return tmp_path / "refugio.json"


@pytest.fixture
def fichero_con_invalidos(refugio_completo, ruta):
    """JSON con 3 animales: uno con chip mal formado y otro sin chip."""
    guardar_refugio(refugio_completo, ruta)
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    datos["animales"][0]["id_chip"] = "chip001"
    del datos["animales"][2]["id_chip"]
    ruta.write_text(json.dumps(datos, ensure_ascii=False), encoding="utf-8")
    return ruta


# Guardar

def test_guardar_crea_el_fichero(refugio_completo, ruta):
    guardar_refugio(refugio_completo, ruta)
    assert ruta.exists()


def test_guardar_escribe_json_valido(refugio_completo, ruta):
    guardar_refugio(refugio_completo, ruta)
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    assert datos == refugio_completo.to_dict()


def test_guardar_conserva_las_tildes(refugio_completo, ruta):
    guardar_refugio(refugio_completo, ruta)
    assert "Revisión general" in ruta.read_text(encoding="utf-8")


# Cargar

def test_cargar_devuelve_un_refugio_igual(refugio_completo, ruta):
    guardar_refugio(refugio_completo, ruta)
    assert cargar_refugio(ruta) == refugio_completo


def test_cargar_devuelve_un_objeto_nuevo(refugio_completo, ruta):
    guardar_refugio(refugio_completo, ruta)
    assert cargar_refugio(ruta) is not refugio_completo


def test_cargar_reconstruye_la_fecha_de_nacimiento_como_tupla(refugio_completo, ruta):
    guardar_refugio(refugio_completo, ruta)
    rex = cargar_refugio(ruta).buscar_animal_por_chip("CHIP001")
    assert rex.fecha_nacimiento == (2021, 3, 12)


def test_cargar_reconstruye_las_fechas_de_las_revisiones(refugio_completo, ruta):
    guardar_refugio(refugio_completo, ruta)
    rex = cargar_refugio(ruta).buscar_animal_por_chip("CHIP001")
    assert rex.historial_veterinario[0].fecha == date(2026, 1, 10)


def test_cargar_enlaza_voluntarios_con_los_del_refugio(refugio_completo, ruta):
    guardar_refugio(refugio_completo, ruta)
    cargado = cargar_refugio(ruta)
    rex = cargado.buscar_animal_por_chip("CHIP001")
    assert rex.voluntarios_asignados[0] is cargado.voluntarios[0]


def test_cargar_enlaza_la_adopcion_con_el_animal_del_refugio(refugio_completo, ruta):
    guardar_refugio(refugio_completo, ruta)
    cargado = cargar_refugio(ruta)
    assert cargado.adopciones[0].animal is cargado.buscar_animal_por_chip("CHIP002")


def test_cargar_fichero_inexistente_lanza_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        cargar_refugio(tmp_path / "no_existe.json")


# Cargar validando

def test_cargar_validando_sin_errores_no_rechaza_nada(refugio_completo, ruta):
    guardar_refugio(refugio_completo, ruta)
    cargado, rechazados = cargar_refugio_validando(ruta)
    assert rechazados == []
    assert cargado == refugio_completo


def test_cargar_validando_conserva_solo_los_animales_validos(fichero_con_invalidos):
    cargado, _ = cargar_refugio_validando(fichero_con_invalidos)
    assert [a.id_chip for a in cargado.animales] == ["CHIP002"]


def test_cargar_validando_devuelve_los_registros_rechazados(fichero_con_invalidos):
    _, rechazados = cargar_refugio_validando(fichero_con_invalidos)
    assert [donde for donde, _ in rechazados] == ["animales[0]", "animales[2]"]


def test_cargar_validando_indica_el_tipo_de_error(fichero_con_invalidos):
    _, rechazados = cargar_refugio_validando(fichero_con_invalidos)
    assert [type(e) for _, e in rechazados] == [ChipMalFormadoError, ChipAusenteError]


def test_cargar_validando_conserva_las_adopciones_de_animales_validos(fichero_con_invalidos):
    cargado, _ = cargar_refugio_validando(fichero_con_invalidos)
    assert len(cargado.adopciones) == 1


# Logging

def test_guardar_genera_info(caplog, refugio_completo, ruta):
    caplog.set_level(logging.INFO)
    guardar_refugio(refugio_completo, ruta)
    assert [r.levelname for r in caplog.records] == ["INFO"]
    assert "guardado" in caplog.text


def test_cargar_genera_info(caplog, refugio_completo, ruta):
    guardar_refugio(refugio_completo, ruta)
    caplog.clear()
    caplog.set_level(logging.INFO)
    cargar_refugio(ruta)
    assert [r.levelname for r in caplog.records] == ["INFO"]
    assert "cargado" in caplog.text


def test_registros_descartados_generan_un_warning_cada_uno(caplog, fichero_con_invalidos):
    caplog.set_level(logging.INFO)
    cargar_refugio_validando(fichero_con_invalidos)
    avisos = [r for r in caplog.records if r.levelname == "WARNING"]
    assert len(avisos) == 2


def test_carga_validando_sin_errores_no_genera_warnings(caplog, refugio_completo, ruta):
    guardar_refugio(refugio_completo, ruta)
    caplog.set_level(logging.INFO)
    cargar_refugio_validando(ruta)
    assert [r.levelname for r in caplog.records] == ["INFO"]
