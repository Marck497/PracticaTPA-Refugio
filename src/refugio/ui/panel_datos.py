"""Panel de datos generales: se actualiza solo gracias al patrón Observer"""

from tkinter import ttk
import tkinter as tk
from typing import Any

from refugio.gestor import Refugio

EVENTOS = ("ingreso", "baja", "voluntario", "adopcion")

class PanelDatos(ttk.LabelFrame):
    """Muestra cifras del refugio y se redibuja cuando el refugio cambia"""

    def __init__(self, padre: tk.Misc, refugio: Refugio) -> None:
        super().__init__(padre, text="Datos generales")
        self.refugio = refugio
        self.etiqueta = ttk.Label(self, justify="left")
        self.etiqueta.pack(anchor="w", padx=8, pady=4)

        self._suscribir()
        self.bind("<Destroy>", self._al_destruir)
        self.actualizar()

    def cambiar_refugio(self, refugio: Refugio) -> None:
        """Pasa al observer otro refugio (por ejemplo, tras cargar un archivo)"""
        self._desuscribir()
        self.refugio = refugio
        self._suscribir()
        self.actualizar()

    def _suscribir(self) -> None:
        for evento in EVENTOS:
            self.refugio.suscribir(evento, self._al_cambiar)

    def _desuscribir(self) -> None:
        for evento in EVENTOS:
            self.refugio.desuscribir(evento, self._al_cambiar)

    def _al_cambiar(self, **datos: Any) -> None:
        self.actualizar()

    def actualizar(self) -> None:
        datos = self.refugio.datos_generales()
        self.etiqueta.configure(text=(
            f"Animales: {datos['animales']}/{datos['capacidad']}   "
            f"Disponibles: {datos['disponibles']}   "
            f"Adoptados: {datos['adoptados']}\n"
            f"Voluntarios: {datos['voluntarios']}   "
            f"Adopciones: {datos['adopciones']}   "
            f"Adoptantes: {datos['adoptantes']}"
        ))

    def _al_destruir(self, evento: tk.Event) -> None:
        if evento.widget is self:
            self._desuscribir()