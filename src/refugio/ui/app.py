"""Ventana principal: menú lateral a la izquierda y la vista activa a la derecha."""

import logging
import tkinter as tk
from functools import partial
from tkinter import filedialog, messagebox, ttk

from refugio.gestor import Refugio
from refugio.persistencia import cargar_refugio_validando, guardar_datos
from .panel_datos import PanelDatos
from .panel_log import PanelLog
from .segundo_plano import TareaSegundoPlano
from .vistas import Vista, VistaAdopciones, VistaAnimales, VistaVoluntarios

logger = logging.getLogger(__name__)

TIPOS_JSON = [("Archivos JSON", "*.json")]

class App(tk.Tk):
    VISTAS: tuple[type[Vista], ...] = (VistaAnimales, VistaVoluntarios, VistaAdopciones)

    def __init__(self, refugio: Refugio):
        super().__init__()
        self.title(f"Gestión de refugio - {refugio.nombre}")
        self.geometry("900x500")
        self.refugio = refugio
        PanelLog(self).pack(side="bottom", fill="x")
        self.panel_datos = PanelDatos(self, refugio)
        self.panel_datos.pack(side="top", fill="x", padx=6, pady=(6, 0))
        menu = ttk.Frame(self, padding=6)
        menu.pack(side="left", fill="y")
        self.contenido = ttk.Frame(self)
        self.contenido.pack(side="right", fill="both", expand=True)

        self.vistas: dict[str, Vista] = {}
        for clase in self.VISTAS:
            vista = clase(self.contenido, refugio)
            vista.place(relwidth=1, relheight=1)
            self.vistas[clase.titulo] = vista
            ttk.Button(
                menu, text=clase.titulo, command = lambda t=clase.titulo: self.mostrar(t)
            ).pack(fill="x", pady=2)

        # Guardar / cargar datos
        ttk.Separator(menu).pack(fill="x", pady=8)
        self.botones_archivo = [
            ttk.Button(menu, text="Guardar datos", command=self._guardar),
            ttk.Button(menu, text="Cargar datos", command=self._cargar)
        ]
        for boton in self.botones_archivo:
            boton.pack(fill="x", pady=2)

        self._actual = self.VISTAS[0].titulo
        self.mostrar(self._actual)

    def mostrar(self, titulo: str) -> None:
        """Pone una vista al frente, después de actualizar sus datos"""
        self._actual = titulo
        vista = self.vistas[titulo]
        vista.refrescar()
        vista.tkraise()

    def _guardar(self) -> None:
        ruta = filedialog.asksaveasfilename(
            title="Guardar datos", defaultextension=".json",
            filetypes=TIPOS_JSON, initialfile="refugio.json",
        )
        if not ruta: # el usuario cancela
            return
        datos = self.refugio.to_dict()
        self._ocupado(True)
        TareaSegundoPlano(
            self, partial(guardar_datos, datos, ruta),
            partial(self._tras_guardar, ruta), self._tras_fallo,
        )

    def _tras_guardar(self, ruta: str, _resultado: None) -> None:
        self._ocupado(False)
        messagebox.showinfo("Guardado", f"Datos guardados en: \n{ruta}")

    def _cargar(self) -> None:
        ruta = filedialog.askopenfilename(title="Cargar datos", filetypes=TIPOS_JSON)
        if not ruta:
            return
        if not messagebox.askyesno("Cargar datos", "Se sustituirán los datos actuales, ¿Continuar?"):
            return
        self._ocupado(True)
        TareaSegundoPlano(self, partial(cargar_refugio_validando, ruta), self._tras_cargar, self._tras_fallo)

    def _tras_cargar(self, resultado: tuple[Refugio, list]) -> None:
        refugio, rechazados = resultado
        self._ocupado(False)
        self.refugio = refugio
        self.panel_datos.cambiar_refugio(refugio)
        for vista in self.vistas.values():
            vista.refugio = refugio
        self.title(f"Gestión de refugio - {refugio.nombre}")
        self.mostrar(self._actual)
        aviso = f"Datos cargados: {len(refugio.animales)} animales."
        if rechazados:
            aviso += f"\nSe descartaron {len(rechazados)} registros inválidos (ver el log)."
        messagebox.showinfo("Cargado", aviso)

    def _tras_fallo(self, error: Exception) -> None:
        self._ocupado(False)
        logger.error("Operación con archivo fallida: %s", error)
        messagebox.showerror("Error", f"No se pudo completar la operación:\n{error}")

    def _ocupado(self, ocupado: bool) -> None:
        """Mientras se guarda o carga: botones desactivados y cursor de espera."""
        for boton in self.botones_archivo:
            boton.configure(state="disabled" if ocupado else "normal")
        self.configure(cursor="watch" if ocupado else "")