"""Clase base de todas las vistas de la interfaz."""

import tkinter as tk
from abc import ABC, abstractmethod
from collections.abc import Iterable
from tkinter import messagebox, ttk

from refugio.gestor import Refugio

class Vista(ttk.Frame, ABC):
    """Una pantalla de la aplicación.

    Para crear una vista nueva: heredar de esta clase, poner un `titulo`
    (es el texto del botón del menú lateral) e implementar `construir` y `refrescar`.
    La vista solo habla con `self.refugio`; nunca toca las listas internas.
    """

    titulo: str = ""

    def __init__(self, padre : tk.Misc, refugio: Refugio):
        super().__init__(padre)
        self.refugio = refugio
        self.construir()

    @abstractmethod
    def construir(self) -> None:
        """Crea los widgets. Se llama UNA sola vez al crear la vista."""

    @abstractmethod
    def refrescar(self) -> None:
        """Vuelve a leer los datos del refugio y los pinta.

        Se llama cada vez que se entra en la vista y tras cada acción.
        """

    # Utilidades comunes para las vistas

    def crear_tabla(self, columnas: tuple[str, ...]) -> ttk.Treeview:
        """Crea una tabla con esas columnas y la coloca ocupando toda la vista."""
        tabla = ttk.Treeview(self, columns=columnas, show="headings")
        for columna in columnas:
            tabla.heading(columna, text=columna.capitalize())
        tabla.pack(fill="both", expand=True)
        return tabla

    @staticmethod
    def rellenar_tabla(tabla: ttk.Treeview, filas: Iterable[tuple]) -> None:
        """Borra el contenido de la tabla y lo sustituye por estas filas"""
        tabla.delete(*tabla.get_children())
        for fila in filas:
            tabla.insert("", "end", values=fila)

    @staticmethod
    def mostrar_error(error: Exception) -> None:
        """Muestra un error del dominio al usuario en un cuadro de diálogo."""
        messagebox.showerror("No se pudo completar la operación", str(error))