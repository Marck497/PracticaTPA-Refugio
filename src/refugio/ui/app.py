"""Ventana principal: menú lateral a la izquierda y la vista activa a la derecha."""

import tkinter as tk
from tkinter import ttk

from refugio.gestor import Refugio
from .panel_log import PanelLog
from .vistas import Vista, VistaAdopciones, VistaAnimales, VistaVoluntarios

class App(tk.Tk):
    VISTAS: tuple[type[Vista], ...] = (VistaAnimales, VistaVoluntarios, VistaAdopciones)

    def __init__(self, refugio: Refugio):
        super().__init__()
        self.title(f"Gestión de refugio - {refugio.nombre}")
        self.geometry("900x500")
        self.refugio = refugio
        PanelLog(self).pack(side="bottom", fill="x")
        menu = ttk.Frame(self, padding=6)
        menu.pack(side="left", fill="y")
        self.contenido = ttk.Frame(self)
        self.contenido.pack(side="right", fill="both", expand=True)
        # Más adelante aquí panel de datos arriba y panel de log abajo

        self.vistas: dict[str, Vista] = {}
        for clase in self.VISTAS:
            vista = clase(self.contenido, refugio)
            vista.place(relwidth=1, relheight=1)
            self.vistas[clase.titulo] = vista
            ttk.Button(
                menu, text=clase.titulo, command = lambda t=clase.titulo: self.mostrar(t)
            ).pack(fill="x", pady=2)

        self.mostrar(self.VISTAS[0].titulo)

    def mostrar(self, titulo: str) -> None:
        """Pone una vista al frente, después de actualizar sus datos"""
        vista = self.vistas[titulo]
        vista.refrescar()
        vista.tkraise()