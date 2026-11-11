"""Tests de Refugio: capacidad, búsquedas, voluntarios, adopciones, eventos y logging."""

import logging
from datetime import date

import pytest

from refugio import (
    Adopcion,
    Animal,
    AnimalNoEncontradoError,
    CapacidadSuperadaError,
    Refugio,
    RefugioError,
    Voluntario,
)
from refugio.excepciones import ReglaInclumplidaError


def nuevo_animal(n: int) -> Animal:
    return Animal(f"CHIP{n:03d}", f"Animal{n}", "Perro", 10.0, "Macho", (2020, 1, 1))


# Capacidad

def test_capacidad_explicita(refugio):
    assert refugio.capacidad_maxima == 3


def test_capacidad_por_defecto_es_triple_de_los_animales_iniciales():
    r = Refugio("R", animales=[nuevo_animal(i) for i in range(1, 5)])
    assert r.capacidad_maxima == 12


def test_capacidad_por_defecto_sin_animales_es_uno():
    assert Refugio("R").capacidad_maxima == 1


@pytest.mark.parametrize("valor", [0, 24])
def test_capacidad_en_los_limites_es_valida(refugio, valor):
    refugio.capacidad_maxima = valor
    assert refugio.capacidad_maxima == valor


@pytest.mark.parametrize("valor", [-1, 25])
def test_capacidad_fuera_de_rango_lanza_value_error(refugio, valor):
    with pytest.raises(ValueError):
        refugio.capacidad_maxima = valor


def test_registrar_ingreso_anade_el_animal(refugio, animal):
    refugio.registrar_ingreso(animal)
    assert refugio.animales == [animal]


def test_registrar_ingreso_ignora_un_animal_repetido(refugio, animal):
    refugio.registrar_ingreso(animal)
    refugio.registrar_ingreso(animal)
    assert len(refugio.animales) == 1


def test_refugio_lleno_lanza_capacidad_superada(refugio):
    for i in range(1, 4):
        refugio.registrar_ingreso(nuevo_animal(i))
    with pytest.raises(CapacidadSuperadaError):
        refugio.registrar_ingreso(nuevo_animal(4))


def test_capacidad_superada_es_un_refugio_error():
    assert issubclass(CapacidadSuperadaError, RefugioError)


def test_refugios_distintos_no_comparten_listas():
    a = Refugio("A", capacidad_maxima=5)
    b = Refugio("B", capacidad_maxima=5)
    a.registrar_ingreso(nuevo_animal(1))
    assert b.animales == []


# Búsquedas

def test_buscar_animal_por_nombre_sin_distinguir_mayusculas(refugio, animal):
    refugio.registrar_ingreso(animal)
    assert refugio.buscar_animal("rEx") is animal


def test_buscar_animal_inexistente_lanza_error(refugio):
    with pytest.raises(AnimalNoEncontradoError):
        refugio.buscar_animal("Nadie")


def test_buscar_animal_por_chip(refugio, animal):
    refugio.registrar_ingreso(animal)
    assert refugio.buscar_animal_por_chip("CHIP001") is animal


def test_buscar_chip_inexistente_lanza_error(refugio):
    with pytest.raises(AnimalNoEncontradoError):
        refugio.buscar_animal_por_chip("CHIP999")


def test_animal_no_encontrado_es_un_refugio_error():
    assert issubclass(AnimalNoEncontradoError, RefugioError)


def test_regla_incumplida_es_un_refugio_error():
    # la interfaz solo captura RefugioError
    assert issubclass(ReglaInclumplidaError, RefugioError)


def test_regla_incumplida_sigue_siendo_un_value_error():
    assert issubclass(ReglaInclumplidaError, ValueError)


def test_mostrar_animal_incluye_sus_datos(refugio_completo):
    ficha = refugio_completo.mostrar_animal("Rex")
    assert "Chip: CHIP001" in ficha
    assert "Revisiones veterinarias: 1" in ficha
    assert "Voluntarios asignados: ['Marcos']" in ficha


# Voluntarios

def test_asignar_voluntario_lo_enlaza_con_el_animal(refugio, animal, voluntario):
    refugio.registrar_ingreso(animal)
    refugio.asignar_voluntario(voluntario, "CHIP001")
    assert animal.voluntarios_asignados == [voluntario]


def test_asignar_voluntario_nuevo_lo_registra_en_el_refugio(refugio, animal, voluntario):
    refugio.registrar_ingreso(animal)
    refugio.asignar_voluntario(voluntario, "CHIP001")
    assert refugio.voluntarios == [voluntario]


def test_asignar_voluntario_dos_veces_no_lo_duplica(refugio, animal, voluntario):
    refugio.registrar_ingreso(animal)
    refugio.asignar_voluntario(voluntario, "CHIP001")
    refugio.asignar_voluntario(voluntario, "CHIP001")
    assert refugio.voluntarios == [voluntario]
    assert animal.voluntarios_asignados == [voluntario]


def test_asignar_voluntario_a_chip_inexistente_lanza_error(refugio, voluntario):
    with pytest.raises(AnimalNoEncontradoError):
        refugio.asignar_voluntario(voluntario, "CHIP999")


# Adopciones

def test_tramitar_adopcion_devuelve_la_adopcion(refugio, animal, adoptante):
    refugio.registrar_ingreso(animal)
    adopcion = refugio.tramitar_adopcion("CHIP001", adoptante, date(2026, 9, 20))
    assert isinstance(adopcion, Adopcion)
    assert adopcion.animal is animal
    assert adopcion.adoptante is adoptante


def test_tramitar_adopcion_la_guarda_en_el_historico(refugio, animal, adoptante):
    refugio.registrar_ingreso(animal)
    adopcion = refugio.tramitar_adopcion("CHIP001", adoptante)
    assert refugio.adopciones == [adopcion]


def test_tramitar_adopcion_marca_el_animal_como_adoptado(refugio, animal, adoptante):
    refugio.registrar_ingreso(animal)
    refugio.tramitar_adopcion("CHIP001", adoptante)
    assert animal.estado_adopcion == "adoptado"


def test_tramitar_adopcion_sin_fecha_usa_la_de_hoy(refugio, animal, adoptante):
    refugio.registrar_ingreso(animal)
    adopcion = refugio.tramitar_adopcion("CHIP001", adoptante)
    assert adopcion.fecha == date.today()


def test_adoptar_animal_ya_adoptado_lanza_regla_incumplida(refugio, animal, adoptante):
    refugio.registrar_ingreso(animal)
    refugio.tramitar_adopcion("CHIP001", adoptante)
    with pytest.raises(ReglaInclumplidaError):
        refugio.tramitar_adopcion("CHIP001", adoptante)


def test_adoptar_animal_no_disponible_no_crea_adopcion(refugio, animal, adoptante):
    animal.estado_adopcion = "en_proceso"
    refugio.registrar_ingreso(animal)
    with pytest.raises(ReglaInclumplidaError):
        refugio.tramitar_adopcion("CHIP001", adoptante)
    assert refugio.adopciones == []


def test_adoptar_chip_inexistente_lanza_error(refugio, adoptante):
    with pytest.raises(AnimalNoEncontradoError):
        refugio.tramitar_adopcion("CHIP999", adoptante)


# Informe e igualdad

def test_informe_actividad(refugio_completo):
    informe = refugio_completo.informe_actividad()
    assert "Ocupación: 3/10" in informe
    assert "Animales disponibles: 2" in informe
    assert "Animales adoptados: 1" in informe
    assert "Adopciones tramitadas (histórico): 1" in informe
    assert "Voluntarios activos: 1" in informe


def test_to_dict_incluye_voluntarios_asignados_solo_a_animales(refugio, animal, voluntario):
    refugio.registrar_ingreso(animal)
    animal.asignar_voluntario(voluntario)  # sin pasar por el refugio
    dnis = [v["dni"] for v in refugio.to_dict()["voluntarios"]]
    assert dnis == ["00000001X"]


def test_refugio_from_dict_reconstruye_el_mismo_refugio(refugio_completo):
    assert Refugio.from_dict(refugio_completo.to_dict()) == refugio_completo


def test_refugio_comparado_con_otro_tipo_no_es_igual(refugio):
    assert refugio != "Refugio Esperanza"


# Bajas, cancelaciones y voluntarios

def test_eliminar_animal_lo_quita_del_refugio(refugio, animal):
    refugio.registrar_ingreso(animal)
    refugio.eliminar_animal(animal)
    assert refugio.animales == []


def test_eliminar_animal_que_no_esta_lanza_error(refugio, animal):
    with pytest.raises(AnimalNoEncontradoError):
        refugio.eliminar_animal(animal)


def test_eliminar_animal_con_adopcion_lanza_regla_incumplida(refugio_completo):
    luna = refugio_completo.buscar_animal_por_chip("CHIP002")
    with pytest.raises(ReglaInclumplidaError):
        refugio_completo.eliminar_animal(luna)


def test_cancelar_adopcion_la_quita_del_historico(refugio_completo):
    refugio_completo.cancelar_adopcion(refugio_completo.adopciones[0])
    assert refugio_completo.adopciones == []


def test_cancelar_adopcion_deja_el_animal_disponible(refugio_completo):
    refugio_completo.cancelar_adopcion(refugio_completo.adopciones[0])
    assert refugio_completo.buscar_animal_por_chip("CHIP002").esta_disponible()


def test_cancelar_adopcion_inexistente_lanza_error(refugio, animal, adoptante):
    adopcion = Adopcion(animal, adoptante, date(2026, 9, 20))
    with pytest.raises(ValueError):
        refugio.cancelar_adopcion(adopcion)


def test_desvincular_voluntario_lo_quita_del_animal(refugio_completo, voluntario, animal):
    refugio_completo.desvincular_voluntario(voluntario, "CHIP001")
    assert animal.voluntarios_asignados == []


def test_desvincular_voluntario_no_asignado_lanza_error(refugio_completo, voluntario):
    with pytest.raises(ValueError):
        refugio_completo.desvincular_voluntario(voluntario, "CHIP003")


def test_eliminar_voluntario_lo_quita_de_todos_sus_animales(refugio_completo, voluntario, animal):
    refugio_completo.eliminar_voluntario(voluntario)
    assert refugio_completo.voluntarios == []
    assert animal.voluntarios_asignados == []


def test_eliminar_voluntario_no_registrado_lanza_error(refugio, voluntario):
    with pytest.raises(ValueError):
        refugio.eliminar_voluntario(voluntario)


def test_datos_generales(refugio_completo):
    assert refugio_completo.datos_generales() == {
        "animales": 3,
        "capacidad": 10,
        "disponibles": 2,
        "adoptados": 1,
        "voluntarios": 1,
        "adopciones": 1,
        "adoptantes": 1,
    }


# Eventos (Observer)

@pytest.fixture
def eventos(refugio_completo):
    """Lista donde se apunta cada evento que emite el refugio: (nombre, datos)."""
    recibidos = []
    for nombre in ("ingreso", "baja", "voluntario", "adopcion"):
        refugio_completo.suscribir(
            nombre, lambda nombre=nombre, **datos: recibidos.append((nombre, datos))
        )
    return recibidos


def test_registrar_ingreso_emite_evento_ingreso(refugio_completo, eventos):
    nuevo = nuevo_animal(9)
    refugio_completo.registrar_ingreso(nuevo)
    assert eventos == [("ingreso", {"animal": nuevo})]


def test_ingreso_repetido_no_emite_evento(refugio_completo, eventos, animal):
    refugio_completo.registrar_ingreso(animal)
    assert eventos == []


def test_asignar_voluntario_emite_evento_voluntario(refugio_completo, eventos, voluntario):
    refugio_completo.asignar_voluntario(voluntario, "CHIP003")
    toby = refugio_completo.buscar_animal_por_chip("CHIP003")
    assert eventos == [("voluntario", {"voluntario": voluntario, "animal": toby})]


def test_tramitar_adopcion_emite_evento_adopcion(refugio_completo, eventos, adoptante):
    adopcion = refugio_completo.tramitar_adopcion("CHIP003", adoptante)
    assert eventos == [("adopcion", {"adopcion": adopcion})]


def test_eliminar_animal_emite_evento_baja(refugio_completo, eventos):
    toby = refugio_completo.buscar_animal_por_chip("CHIP003")
    refugio_completo.eliminar_animal(toby)
    assert eventos == [("baja", {"animal": toby})]


def test_cancelar_adopcion_emite_evento_adopcion(refugio_completo, eventos):
    adopcion = refugio_completo.adopciones[0]
    refugio_completo.cancelar_adopcion(adopcion)
    assert eventos == [("adopcion", {"adopcion": adopcion})]


def test_operacion_rechazada_no_emite_evento(refugio_completo, eventos, adoptante):
    with pytest.raises(ReglaInclumplidaError):
        refugio_completo.tramitar_adopcion("CHIP002", adoptante)
    assert eventos == []


def test_tras_desuscribir_ya_no_se_recibe_el_evento(refugio):
    recibidos = []

    def apuntar(**datos):
        recibidos.append(datos)

    refugio.suscribir("ingreso", apuntar)
    refugio.desuscribir("ingreso", apuntar)
    refugio.registrar_ingreso(nuevo_animal(1))
    assert recibidos == []


def test_varios_suscriptores_reciben_el_mismo_evento(refugio):
    a, b = [], []
    refugio.suscribir("ingreso", lambda **datos: a.append(datos))
    refugio.suscribir("ingreso", lambda **datos: b.append(datos))
    refugio.registrar_ingreso(nuevo_animal(1))
    assert len(a) == len(b) == 1


# Logging

def niveles(caplog, logger="refugio.gestor"):
    return [r.levelname for r in caplog.records if r.name == logger]


def test_ingreso_correcto_genera_info(caplog, refugio, animal):
    caplog.set_level(logging.INFO)
    refugio.registrar_ingreso(animal)
    assert niveles(caplog) == ["INFO"]
    assert "CHIP001" in caplog.text


def test_ingreso_con_refugio_lleno_genera_warning(caplog):
    r = Refugio("R", capacidad_maxima=0)
    caplog.set_level(logging.INFO)
    with pytest.raises(CapacidadSuperadaError):
        r.registrar_ingreso(nuevo_animal(1))
    assert niveles(caplog) == ["WARNING"]


def test_asignacion_correcta_genera_info(caplog, refugio, animal, voluntario):
    refugio.registrar_ingreso(animal)
    caplog.set_level(logging.INFO)
    refugio.asignar_voluntario(voluntario, "CHIP001")
    assert niveles(caplog) == ["INFO"]


def test_asignacion_rechazada_genera_warning(caplog, refugio):
    voluntario = Voluntario("00000009X", "Ana", "600000009", "Perros", max_animales=1)
    refugio.registrar_ingreso(nuevo_animal(1))
    refugio.registrar_ingreso(nuevo_animal(2))
    refugio.asignar_voluntario(voluntario, "CHIP001")
    caplog.set_level(logging.INFO)
    with pytest.raises(ReglaInclumplidaError):
        refugio.asignar_voluntario(voluntario, "CHIP002")
    assert niveles(caplog) == ["WARNING"]


def test_adopcion_correcta_genera_info(caplog, refugio, animal, adoptante):
    refugio.registrar_ingreso(animal)
    caplog.set_level(logging.INFO)
    refugio.tramitar_adopcion("CHIP001", adoptante)
    assert niveles(caplog) == ["INFO"]


def test_adopcion_de_animal_no_disponible_genera_warning(caplog, refugio_completo, adoptante):
    caplog.set_level(logging.INFO)
    with pytest.raises(ReglaInclumplidaError):
        refugio_completo.tramitar_adopcion("CHIP002", adoptante)
    assert niveles(caplog) == ["WARNING"]
    assert "no está disponible" in caplog.text


def test_baja_rechazada_genera_warning(caplog, refugio_completo):
    luna = refugio_completo.buscar_animal_por_chip("CHIP002")
    caplog.set_level(logging.INFO)
    with pytest.raises(ReglaInclumplidaError):
        refugio_completo.eliminar_animal(luna)
    assert niveles(caplog) == ["WARNING"]
