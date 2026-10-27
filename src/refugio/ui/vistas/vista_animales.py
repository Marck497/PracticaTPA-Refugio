"""Vista de animales."""

from .base import Vista

COLUMNAS = ("chip", "nombre", "esecie", "estado")

class VistaAnimales(Vista):
    titulo = "Animales"

    def construir(self) -> None:
        self.tabla = self.crear_tabla(COLUMNAS)
        # TODO

    def refrescar(self):
        self.rellenar_tabla(
            self.tabla,
            ((a.id_chip, a.nombre, a.especie, a.estado_adopcion) for a in self.refugio.animales)
        )