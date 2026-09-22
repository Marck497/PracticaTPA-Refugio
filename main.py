"""
Script de demostración del Apartado 1 y 2.

Construye un Refugio con 8 animales de ejemplo (capacidad_maxima derivada
= 8 * 3 = 24, mismo criterio que el ejemplo del enunciado), añade
voluntarios, revisiones veterinarias y una adopción, y muestra el uso
básico de todas las clases del modelo.
"""

from datetime import date
from adopcion import Adopcion
from adoptante import Adoptante
from animal import Animal
from refugio import Refugio
from revision_veterinaria import RevisionVeterinaria
from voluntario import Voluntario

def construir_refugio_demo() -> Refugio:
    animales = [
        Animal("CHIP001", "Rex", "Perro", 22.5, "Macho", date(2021, 3, 12)),
        Animal("CHIP002", "Luna", "Gata", 4.1, "Hembra", date(2022, 7, 1)),
        Animal("CHIP003", "Toby", "Perro", 15.0, "Macho", date(2020, 11, 23)),
        Animal("CHIP004", "Nina", "Gata", 3.8, "Hembra", date(2023, 1, 15)),
        Animal("CHIP005", "Max", "Perro", 30.2, "Macho", date(2019, 5, 30)),
        Animal("CHIP006", "Coco", "Conejo", 1.6, "Hembra", date(2024, 2, 9)),
        Animal("CHIP007", "Simba", "Gato", 5.0, "Macho", date(2021, 9, 18)),
        Animal("CHIP008", "Bella", "Perro", 18.4, "Hembra", date(2022, 12, 4)),
    ]

    refugio = Refugio(nombre="Refugio Esperanza", animales=animales)

    voluntario = Voluntario(
        dni="12345678A", nombre="Ana Pérez", telefono="600111222", area_asignada="Perros"
    )
    refugio.asignar_voluntario(voluntario, "CHIP001")

    revision = RevisionVeterinaria(
        fecha=date(2026, 1, 10),
        motivo="Revisión general",
        diagnostico="Sano",
        tratamiento="Ninguno",
    )
    refugio.buscar_animal_por_chip("CHIP001").anadir_revision(revision)

    return refugio


def main() -> None:
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