"""Tests de la clase Observable (patrón Observer)."""

import pytest

from refugio.eventos import Observable


@pytest.fixture
def sujeto():
    return Observable()


def test_notificar_llama_al_suscriptor_con_los_datos(sujeto):
    recibidos = []
    sujeto.suscribir("evento", lambda **datos: recibidos.append(datos))
    sujeto._notificar("evento", x=1)
    assert recibidos == [{"x": 1}]


def test_notificar_sin_suscriptores_no_falla(sujeto):
    sujeto._notificar("nadie_escucha", x=1)


def test_solo_se_avisa_a_los_suscritos_a_ese_evento(sujeto):
    recibidos = []
    sujeto.suscribir("a", lambda **datos: recibidos.append("a"))
    sujeto.suscribir("b", lambda **datos: recibidos.append("b"))
    sujeto._notificar("a")
    assert recibidos == ["a"]


def test_suscriptores_se_avisan_en_orden_de_suscripcion(sujeto):
    orden = []
    sujeto.suscribir("e", lambda: orden.append(1))
    sujeto.suscribir("e", lambda: orden.append(2))
    sujeto._notificar("e")
    assert orden == [1, 2]


def test_desuscribir_deja_de_avisar(sujeto):
    recibidos = []

    def apuntar():
        recibidos.append(1)

    sujeto.suscribir("e", apuntar)
    sujeto.desuscribir("e", apuntar)
    sujeto._notificar("e")
    assert recibidos == []


def test_un_suscriptor_puede_desuscribirse_mientras_se_le_avisa(sujeto):
    recibidos = []

    def una_vez():
        recibidos.append(1)
        sujeto.desuscribir("e", una_vez)

    sujeto.suscribir("e", una_vez)
    sujeto.suscribir("e", lambda: recibidos.append(2))
    sujeto._notificar("e")
    sujeto._notificar("e")
    assert recibidos == [1, 2, 2]
