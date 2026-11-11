"""Tests de la parte de la interfaz que no necesita abrir ventanas.

TareaSegundoPlano solo usa `ventana.after(ms, funcion)`, así que se prueba con
una ventana falsa que guarda esas llamadas y las ejecuta cuando le decimos.
"""

import logging
import threading
import time

import pytest

from refugio.ui.panel_log import TextoHandler
from refugio.ui.segundo_plano import TareaSegundoPlano


class VentanaFalsa:
    def __init__(self):
        self.pendientes = []

    def after(self, ms, funcion):
        self.pendientes.append(funcion)

    def procesar(self, hasta, limite=2.0):
        """Ejecuta los after() pendientes hasta que hasta() sea cierto."""
        fin = time.monotonic() + limite
        while not hasta():
            assert time.monotonic() < fin, "la tarea no terminó a tiempo"
            if self.pendientes:
                self.pendientes.pop(0)()
            time.sleep(0.01)


@pytest.fixture
def ventana():
    return VentanaFalsa()


def lanzar(ventana, tarea):
    resultados, errores = [], []
    TareaSegundoPlano(ventana, tarea, resultados.append, errores.append)
    ventana.procesar(lambda: resultados or errores)
    return resultados, errores


def test_tarea_devuelve_su_resultado(ventana):
    resultados, errores = lanzar(ventana, lambda: 42)
    assert resultados == [42]
    assert errores == []


def test_tarea_que_falla_devuelve_la_excepcion(ventana):
    fallo = ValueError("fallo")

    def tarea():
        raise fallo

    resultados, errores = lanzar(ventana, tarea)
    assert resultados == []
    assert errores == [fallo]


def test_tarea_se_ejecuta_en_otro_hilo(ventana):
    resultados, _ = lanzar(ventana, threading.get_ident)
    assert resultados[0] != threading.get_ident()


def test_aviso_de_fin_se_ejecuta_en_el_hilo_principal(ventana):
    hilos = []
    TareaSegundoPlano(ventana, lambda: None, lambda _: hilos.append(threading.get_ident()), print)
    ventana.procesar(lambda: hilos)
    assert hilos == [threading.get_ident()]


def test_aviso_de_fallo_se_ejecuta_en_el_hilo_principal(ventana):
    hilos = []

    def tarea():
        raise RuntimeError

    TareaSegundoPlano(ventana, tarea, print, lambda _: hilos.append(threading.get_ident()))
    ventana.procesar(lambda: hilos)
    assert hilos == [threading.get_ident()]


def test_guardar_en_segundo_plano_escribe_el_fichero(ventana, refugio_completo, tmp_path):
    from functools import partial

    from refugio.persistencia import cargar_refugio, guardar_datos

    ruta = tmp_path / "refugio.json"
    lanzar(ventana, partial(guardar_datos, refugio_completo.to_dict(), ruta))
    assert cargar_refugio(ruta) == refugio_completo


def test_cargar_fichero_inexistente_en_segundo_plano_avisa_del_error(ventana, tmp_path):
    from functools import partial

    from refugio.persistencia import cargar_refugio_validando

    _, errores = lanzar(ventana, partial(cargar_refugio_validando, tmp_path / "no.json"))
    assert isinstance(errores[0], FileNotFoundError)


# Handler del panel de log

def test_texto_handler_guarda_los_mensajes_en_su_cola():
    handler = TextoHandler()
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger = logging.getLogger("prueba.texto_handler")
    logger.addHandler(handler)
    try:
        logger.warning("refugio lleno")
    finally:
        logger.removeHandler(handler)
    assert handler.cola.get_nowait() == "[WARNING] refugio lleno"


def test_texto_handler_recibe_los_logs_del_refugio(refugio, animal):
    handler = TextoHandler()
    raiz = logging.getLogger()
    raiz.addHandler(handler)
    nivel_anterior = raiz.level
    raiz.setLevel(logging.INFO)
    try:
        refugio.registrar_ingreso(animal)
    finally:
        raiz.removeHandler(handler)
        raiz.setLevel(nivel_anterior)
    assert "CHIP001" in handler.cola.get_nowait()
