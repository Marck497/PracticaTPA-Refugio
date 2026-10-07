"""
Apartado 4 - Genericidad + persistencia.

Ejecutar:  python3 test_modelo.py

Los datos de prueba usan como voluntarios y adoptante a los integrantes
del grupo: Marcos, Maria, Gonzalo, Miguel y Hugo (DNI y teléfonos ficticios).
"""

from datetime import date

from adoptante import Adoptante
from animal import Animal
from persistencia import cargar_refugio, guardar_refugio
from refugio import Refugio
from repositorio import ElementoDuplicadoError, ElementoNoEncontradoError, Repositorio
from revision_veterinaria import RevisionVeterinaria
from voluntario import Voluntario

RUTA_JSON = "refugio.json"
INTEGRANTES = ["Marcos", "Maria", "Gonzalo", "Miguel", "Hugo"]


def construir_refugio() -> Refugio:
    animales = [
        Animal("CHIP001", "Rex", "Perro", 22.5, "Macho", (2021, 3, 12)),
        Animal("CHIP002", "Luna", "Gata", 4.1, "Hembra", (2022, 7, 1)),
        Animal("CHIP003", "Toby", "Perro", 15.0, "Macho", (2020, 11, 23)),
        Animal("CHIP004", "Nina", "Gata", 3.8, "Hembra", (2023, 1, 15)),
        Animal("CHIP005", "Max", "Perro", 30.2, "Macho", (2019, 5, 30)),
    ]
    refugio = Refugio("Refugio Esperanza", capacidad_maxima=24, animales=animales)

    # Un voluntario por cada integrante del grupo
    areas = ["Perros", "Gatos", "Perros", "Administración", "Gatos"]
    for i, (nombre, area) in enumerate(zip(INTEGRANTES, areas), start=1):
        v = Voluntario(f"0000000{i}X", nombre, f"60000000{i}", area)
        refugio.voluntarios.append(v)

    refugio.asignar_voluntario(refugio.voluntarios[0], "CHIP001")  # Marcos -> Rex
    refugio.asignar_voluntario(refugio.voluntarios[2], "CHIP001")  # Gonzalo -> Rex
    refugio.asignar_voluntario(refugio.voluntarios[1], "CHIP002")  # Maria -> Luna

    refugio.buscar_animal_por_chip("CHIP001").anadir_revision(
        RevisionVeterinaria(date(2026, 1, 10), "Revisión general", "Sano", "Ninguno")
    )

    hugo = Adoptante("90000005H", "Hugo", "611000005", "hugo@example.com")
    refugio.tramitar_adopcion("CHIP002", hugo, date(2026, 9, 20))
    return refugio


def test_repositorio_generico(refugio: Refugio) -> None:
    print("Repositorio genérico")
    # Misma clase, distintos tipos T
    repo_animales: Repositorio[Animal] = Repositorio(lambda a: a.id_chip)
    repo_voluntarios: Repositorio[Voluntario] = Repositorio(lambda v: v.dni)

    for a in refugio.animales:
        repo_animales.anadir(a)
    for v in refugio.voluntarios:
        repo_voluntarios.anadir(v)

    print(repo_animales, "|", repo_voluntarios)
    assert len(repo_animales) == 5 and len(repo_voluntarios) == 5
    assert repo_animales.obtener("CHIP001").nombre == "Rex"
    assert [v.nombre for v in repo_voluntarios] == INTEGRANTES

    try:
        repo_animales.anadir(refugio.animales[0])
    except ElementoDuplicadoError as e:
        print("Duplicado rechazado:", e)
    else:
        raise AssertionError("debía lanzar ElementoDuplicadoError")

    try:
        repo_voluntarios.obtener("NO-EXISTE")
    except ElementoNoEncontradoError as e:
        print("No encontrado:", e)
    else:
        raise AssertionError("debía lanzar ElementoNoEncontradoError")
    print()


def test_persistencia(original: Refugio) -> None:
    print("== 4.2 Persistencia JSON ==")
    guardar_refugio(original, RUTA_JSON)
    recargado = cargar_refugio(RUTA_JSON)
    print("Guardado en", RUTA_JSON, "y recargado:", recargado)

    # Reconstrucción fiel de los datos (tuplas, fechas, referencias)
    assert recargado.to_dict() == original.to_dict()
    rex = recargado.buscar_animal_por_chip("CHIP001")
    assert isinstance(rex.fecha_nacimiento, tuple)
    assert rex.historial_veterinario[0].fecha == date(2026, 1, 10)
    assert [v.nombre for v in rex.voluntarios_asignados] == ["Marcos", "Gonzalo"]
    # La adopción apunta al MISMO Animal que está en el refugio recargado
    assert recargado.adopciones[0].animal is recargado.buscar_animal_por_chip("CHIP002")
    print("Datos reconstruidos correctamente.")
    print()


def test_igualdad_vs_identidad(original: Refugio) -> None:
    print("== 4.3 Predicción + ejecución: == vs is ==")
    recargado = cargar_refugio(RUTA_JSON)

    print("PREDICCIÓN: original == recargado -> True  (mismos datos / __eq__)")
    print("PREDICCIÓN: original is recargado -> False (objeto nuevo en memoria)")
    print()
    print("original == recargado:", original == recargado)
    print("original is recargado:", original is recargado)

    a_orig = original.animales[0]
    a_rec = recargado.animales[0]
    print("animal original == recargado:", a_orig == a_rec)
    print("animal original is recargado:", a_orig is a_rec)
    print("id(original) =", id(a_orig), "| id(recargado) =", id(a_rec))

    assert original == recargado and original is not recargado
    assert a_orig == a_rec and a_orig is not a_rec

    # Matiz: Animal.__eq__ solo compara el chip. Si cambiamos otro campo,
    # sigue siendo "igual" aunque ya no tenga los mismos datos.
    a_rec.peso = 99.9
    print("\nTras cambiar el peso del recargado:")
    print("animal == :", a_orig == a_rec, "(solo compara el chip)")
    print("to_dict ==:", a_orig.to_dict() == a_rec.to_dict())
    assert a_orig == a_rec and a_orig.to_dict() != a_rec.to_dict()
    print()


def main() -> None:
    original = construir_refugio()
    test_repositorio_generico(original)
    test_persistencia(original)
    test_igualdad_vs_identidad(original)
    print("Todas las pruebas del Apartado 4 han pasado.")


if __name__ == "__main__":
    main()

