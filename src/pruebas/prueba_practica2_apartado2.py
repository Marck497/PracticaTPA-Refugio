from datetime import date

from refugio import Adopcion, Adoptante, Animal, RevisionVeterinaria
from refugio.protocolos import Resumible, mostrar_resumen

def main() -> None:
    animal = Animal("CHIP010", "Nieve", "Gata", 3.2, "Hembra", (2022, 4, 5))
    adoptante = Adoptante("11111111A", "Paco", "767859487", "paco@example.com")
    adopcion = Adopcion(animal=animal, adoptante=adoptante, fecha=date.today())

    revision = RevisionVeterinaria(
        fecha=date(2026, 2, 3),
        motivo="Revision Anual",
        diagnostico="Sano",
        tratamiento="Vacuna de refuerzo",
    )

    print("RevisionVeterinaria y Adopcion no comparten ninguna clase base propia:")
    print("RevisionVeterinaria.__bases__:", RevisionVeterinaria.__bases__)
    print("Adopcion.__bases__:", Adopcion.__bases__)
    print()

    print("¿RevisionVeterinaria cumple Resumible?", isinstance(revision, Resumible))
    print("¿Adopcion cumple Resumible?", isinstance(adopcion, Resumible))
    print()

    print("Llamada polimórfica a través de mostrar_resumen():")
    mostrar_resumen(revision)
    mostrar_resumen(adopcion)
    print()

if __name__ == "__main__":
    main()