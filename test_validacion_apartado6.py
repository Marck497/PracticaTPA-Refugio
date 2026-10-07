"""
Apartado 6 - Validación al cargar.

Ejecutar:  python3 test_validacion.py
(Para la comparación con la biblioteca de terceros: python3 -m pip install regex)
"""

import json

from animal import Animal
from persistencia import cargar_refugio_validando, guardar_refugio
from test_modelo import construir_refugio
from validacion import CHIP, ChipAusenteError, ChipMalFormadoError

RUTA_INVALIDOS = "datos_invalidos.json"


def preparar_fichero_prueba() -> None:
    """8 registros de animales: 6 válidos y 2 inválidos (mal formado y sin campo)."""
    refugio = construir_refugio()  # CHIP001..CHIP005
    refugio.registrar_ingreso(Animal("CHIP006", "Coco", "Conejo", 1.6, "Hembra", (2024, 2, 9)))
    refugio.registrar_ingreso(Animal("CHIP007", "Simba", "Gato", 5.0, "Macho", (2021, 9, 18)))
    refugio.registrar_ingreso(Animal("CHIP008", "Bella", "Perro", 18.4, "Hembra", (2022, 12, 4)))
    guardar_refugio(refugio, RUTA_INVALIDOS)

    with open(RUTA_INVALIDOS, "r", encoding="utf-8") as f:
        datos = json.load(f)
    datos["animales"][3]["id_chip"] = "chip004"   # inválido: minúsculas y sin ceros
    del datos["animales"][6]["id_chip"]           # inválido: falta el campo
    with open(RUTA_INVALIDOS, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)


def test_patron_re_vs_regex() -> None:
    print("== 6.2 Patrón: re frente a regex ==")
    print("Patrón:", CHIP.pattern)
    casos = ["CHIP001", "CHIP999", "chip001", "CHIP01", "CHIP0011", "XCHIP001", ""]
    try:
        import regex
    except ModuleNotFoundError:
        print("(regex no instalada: ejecuta  python3 -m pip install regex  y repite)")
        regex = None

    for c in casos:
        r = bool(CHIP.match(c))
        linea = f"{c!r:12} re={r}"
        if regex is not None:
            g = bool(regex.compile(CHIP.pattern).match(c))
            assert r == g
            linea += f"  regex={g}"
        print(linea)
    assert [bool(CHIP.match(c)) for c in casos] == [True, True, False, False, False, False, False]
    print()


def test_carga_con_rechazos() -> None:
    print("== 6.3 Carga con registros inválidos ==")
    preparar_fichero_prueba()
    with open(RUTA_INVALIDOS, encoding="utf-8") as f:
        total = len(json.load(f)["animales"])
    refugio, rechazados = cargar_refugio_validando(RUTA_INVALIDOS)

    print(f"Registros en fichero: {total} | cargados: {len(refugio.animales)} | rechazados: {len(rechazados)}")
    for donde, error in rechazados:
        print(f"  RECHAZADO {donde}: {type(error).__name__}: {error}")
    print("Animales válidos cargados:", [a.id_chip for a in refugio.animales])

    assert total == 8 and len(refugio.animales) == 6 and len(rechazados) == 2
    tipos = {type(e) for _, e in rechazados}
    assert tipos == {ChipMalFormadoError, ChipAusenteError}
    # Los válidos no se pierden, ni sus adopciones ni sus datos
    assert [a.id_chip for a in refugio.animales] == [
        "CHIP001", "CHIP002", "CHIP003", "CHIP005", "CHIP006", "CHIP008"]
    assert len(refugio.adopciones) == 1
    print()

def main() -> None:
    test_patron_re_vs_regex()
    test_carga_con_rechazos()
    print("Todas las pruebas del Apartado 6 han pasado.")


if __name__ == "__main__":
    main()
