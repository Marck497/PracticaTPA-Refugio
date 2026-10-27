"""Vista de adopciones."""

from .base import Vista

COLUMNAS = ("chip", "animal", "adoptante", "fecha")


class VistaAdopciones(Vista):
    titulo = "Adopciones"

    def construir(self) -> None:
        self.tabla = self.crear_tabla(COLUMNAS)
        # TODO

    def refrescar(self) -> None:
        self.rellenar_tabla(
            self.tabla,
            (
                (a.animal.id_chip, a.animal.nombre, a.adoptante.nombre, a.fecha)
                for a in self.refugio.adopciones
            ),
        )