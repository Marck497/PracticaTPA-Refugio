"""Vista de voluntarios."""

from .base import Vista

COLUMNAS = ("dni", "nombre", "telefono", "area")


class VistaVoluntarios(Vista):
    titulo = "Voluntarios"

    def construir(self) -> None:
        self.tabla = self.crear_tabla(COLUMNAS)
        # TODO

    def refrescar(self) -> None:
        self.rellenar_tabla(
            self.tabla,
            ((v.dni, v.nombre, v.telefono, v.area_asignada) for v in self.refugio.voluntarios),
        )