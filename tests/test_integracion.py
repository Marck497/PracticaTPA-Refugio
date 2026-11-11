"""Flujo completo: ingreso, adopción, guardado y carga."""

from datetime import date

from refugio import Adoptante, Animal, Refugio, Voluntario
from refugio.persistencia import cargar_refugio, guardar_refugio


def test_flujo_completo_guardar_y_cargar_da_el_mismo_refugio(tmp_path):
    refugio = Refugio("Refugio Esperanza", capacidad_maxima=5)
    refugio.registrar_ingreso(Animal("CHIP001", "Rex", "Perro", 22.5, "Macho", (2021, 3, 12)))
    refugio.registrar_ingreso(Animal("CHIP002", "Luna", "Gata", 4.1, "Hembra", (2022, 7, 1)))
    refugio.asignar_voluntario(Voluntario("00000001X", "Marcos", "600000001", "Perros"), "CHIP001")
    hugo = Adoptante("90000005H", "Hugo", "611000005", "hugo@example.com")
    refugio.tramitar_adopcion("CHIP002", hugo, date(2026, 9, 20))

    ruta = tmp_path / "refugio.json"
    guardar_refugio(refugio, ruta)
    cargado = cargar_refugio(ruta)

    assert cargado == refugio
    assert cargado.to_dict() == refugio.to_dict()
    assert cargado.buscar_animal_por_chip("CHIP002").estado_adopcion == "adoptado"
    assert cargado.informe_actividad() == refugio.informe_actividad()


def test_refugio_cargado_sigue_funcionando(refugio_completo, tmp_path):
    ruta = tmp_path / "refugio.json"
    guardar_refugio(refugio_completo, ruta)
    cargado = cargar_refugio(ruta)

    cargado.registrar_ingreso(Animal("CHIP004", "Nina", "Gata", 3.8, "Hembra", (2023, 1, 15)))
    adoptante = Adoptante("11111111A", "Paco", "767859487", "paco@example.com")
    cargado.tramitar_adopcion("CHIP004", adoptante, date(2026, 10, 1))

    guardar_refugio(cargado, ruta)
    assert cargar_refugio(ruta) == cargado
    assert len(cargado.adopciones) == 2
