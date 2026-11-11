"""
Datos y script de demostración.

`construir_refugio_demo` crea un refugio poblado (18 animales, 6 voluntarios, 5 adopciones
y varias revisiones veterinarias) que se usa en `python -m refugio.ui --demo` y en
`python -m refugio`. La capacidad es 24, así que quedan plazas libres para probar los
ingresos y el límite de capacidad.
"""

from datetime import date
from .gestor import Refugio
from .modelo import Adoptante, Animal, RevisionVeterinaria, Voluntario

# (chip, nombre, especie, peso, sexo, nacimiento, estado)
ANIMALES = [
    ("CHIP001", "Rex", "Perro", 22.5, "Macho", (2021, 3, 12), "disponible"),
    ("CHIP002", "Luna", "Gata", 4.1, "Hembra", (2022, 7, 1), "disponible"),
    ("CHIP003", "Toby", "Perro", 15.0, "Macho", (2020, 11, 23), "disponible"),
    ("CHIP004", "Nina", "Gata", 3.8, "Hembra", (2023, 1, 15), "disponible"),
    ("CHIP005", "Max", "Perro", 30.2, "Macho", (2019, 5, 30), "disponible"),
    ("CHIP006", "Coco", "Conejo", 1.6, "Hembra", (2024, 2, 9), "disponible"),
    ("CHIP007", "Simba", "Gato", 5.0, "Macho", (2021, 9, 18), "disponible"),
    ("CHIP008", "Bella", "Perro", 18.4, "Hembra", (2022, 12, 4), "disponible"),
    ("CHIP009", "Kira", "Perro", 12.3, "Hembra", (2023, 6, 2), "disponible"),
    ("CHIP010", "Milo", "Gato", 4.6, "Macho", (2024, 4, 20), "disponible"),
    ("CHIP011", "Lola", "Gata", 3.9, "Hembra", (2020, 8, 14), "disponible"),
    ("CHIP012", "Thor", "Perro", 34.0, "Macho", (2018, 2, 27), "no_disponible"),
    ("CHIP013", "Pelusa", "Conejo", 2.1, "Hembra", (2023, 10, 5), "disponible"),
    ("CHIP014", "Rocky", "Perro", 19.8, "Macho", (2022, 1, 30), "disponible"),
    ("CHIP015", "Nube", "Gata", 3.5, "Hembra", (2025, 3, 11), "disponible"),
    ("CHIP016", "Oliver", "Gato", 5.4, "Macho", (2019, 12, 9), "en_proceso"),
    ("CHIP017", "Canela", "Perro", 11.2, "Hembra", (2024, 9, 1), "disponible"),
    ("CHIP018", "Bimba", "Gata", 4.2, "Hembra", (2021, 5, 25), "disponible"),
]

# (dni, nombre, teléfono, área, chips de los animales que cuida)
VOLUNTARIOS = [
    ("12345678A", "Ana Pérez", "600111222", "Perros", ("CHIP001", "CHIP008", "CHIP009", "CHIP012")),
    ("23456789B", "Luis Gómez", "600222333", "Perros", ("CHIP001", "CHIP012", "CHIP017")),
    ("34567890C", "Elena Ruiz", "600333444", "Gatos", ("CHIP002", "CHIP004", "CHIP011", "CHIP015")),
    ("45678901D", "Sara Molina", "600444555", "Gatos", ("CHIP004", "CHIP016", "CHIP018")),
    ("56789012E", "Iván Torres", "600555666", "Exóticos", ("CHIP006", "CHIP013")),
    ("67890123F", "Noelia Vega", "600666777", "Adopciones", ()),
]

# (chip, motivo, diagnóstico, tratamiento, fecha)
REVISIONES = [
    ("CHIP001", "Revisión general", "Sano", "Ninguno", date(2026, 1, 10)),
    ("CHIP001", "Vacunación anual", "Sano", "Vacuna polivalente", date(2026, 6, 15)),
    ("CHIP004", "Esterilización", "Recuperación correcta", "Antibiótico 7 días", date(2026, 3, 2)),
    ("CHIP012", "Cojera pata trasera", "Esguince leve", "Reposo y antiinflamatorio", date(2026, 9, 28)),
    ("CHIP016", "Revisión general", "Sano", "Ninguno", date(2026, 10, 5)),
    ("CHIP009", "Desparasitación", "Sano", "Pipeta antiparasitaria", date(2026, 8, 19)),
]

# (chip, dni, nombre, teléfono, correo, máximo de adopciones, fecha)
ADOPCIONES = [
    ("CHIP005", "78901234G", "Marta Gil", "611000111", "marta.gil@example.com", 3, date(2026, 2, 14)),
    ("CHIP007", "78901234G", "Marta Gil", "611000111", "marta.gil@example.com", 3, date(2026, 5, 3)),
    ("CHIP010", "89012345H", "Javier Soto", "611000222", "javier.soto@example.com", 2, date(2026, 7, 21)),
    ("CHIP014", "90123456J", "Lucía Marín", "611000333", "lucia.marin@example.com", 1, date(2026, 9, 9)),
    ("CHIP003", "01234567K", "Pablo Díaz", "611000444", "pablo.diaz@example.com", 2, date(2026, 10, 12)),
]


def construir_refugio_demo() -> Refugio:
    """Refugio de ejemplo ya poblado: animales, voluntarios, revisiones y adopciones."""
    animales = [
        Animal(chip, nombre, especie, peso, sexo, nacimiento, estado_adopcion=estado)
        for chip, nombre, especie, peso, sexo, nacimiento, estado in ANIMALES
    ]
    refugio = Refugio(nombre="Refugio Esperanza", capacidad_maxima=24, animales=animales)

    for dni, nombre, telefono, area, chips in VOLUNTARIOS:
        voluntario = Voluntario(dni=dni, nombre=nombre, telefono=telefono, area_asignada=area)
        refugio.voluntarios.append(voluntario)
        for chip in chips:
            refugio.asignar_voluntario(voluntario, chip)

    for chip, motivo, diagnostico, tratamiento, fecha in REVISIONES:
        revision = RevisionVeterinaria(fecha, motivo, diagnostico, tratamiento)
        refugio.buscar_animal_por_chip(chip).anadir_revision(revision)

    for chip, dni, nombre, telefono, correo, maximo, fecha in ADOPCIONES:
        adoptante = Adoptante(dni, nombre, telefono, correo, maximo)
        refugio.tramitar_adopcion(chip, adoptante, fecha)

    return refugio


def main() -> None:
    """Ejecuta la demostración por consola (`python -m refugio`)."""
    refugio = construir_refugio_demo()

    print(refugio.mostrar_animal("Rex"))
    print()

    adoptante = Adoptante(
        dni="87654321B", nombre="Carlos Ruiz", telefono="611222333", correo="carlos@example.com"
    )
    adopcion = refugio.tramitar_adopcion("CHIP002", adoptante)
    print(f"Adopción registrada: {adopcion}")
    print()

    print(refugio.informe_actividad())
    print()
    print("ID actual", refugio.animales[0].id_chip)

    refugio.animales[0].id_chip = "CHIP999"
    print("ID nuevo:", refugio.animales[0].id_chip)

    refugio.capacidad_maxima = 20
    print("Capacidad nueva:", refugio.capacidad_maxima)

    try:
        refugio.animales[0].id_chip = ""
    except ValueError as e:
        print("Error", e)

    try:
        refugio.capacidad_maxima = 30
    except ValueError as e:
        print("Error", e)

if __name__ == "__main__":
    main()