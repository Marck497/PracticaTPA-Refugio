"""Panel inferior que muestra los mensajes de log dentro de la ventana."""

import logging
import tkinter as tk
from tkinter import scrolledtext

from refugio.registro import FORMATO

class TextoHandler(logging.Handler):
    """Handler de logging que escribe cada mensaje en una interfaz gráfica"""

    def __init__(self, texto: tk.Text):
        super().__init__()
        self.texto = texto

    def emit(self, record: logging.LogRecord) -> None:
        self.texto.after(0, self._escribir, self.format(record))

    def _escribir(self, mensaje: str) -> None:
        self.texto.configure(state="normal")
        self.texto.insert("end", mensaje + "\n")
        self.texto.configure(state="disabled")  # Solo para leer
        self.texto.see("end")                   # Baja al último mensaje

class PanelLog(scrolledtext.ScrolledText):
    """Cuadro de texto de solo lectura conectado al sistema de logging"""

    def __init__(self, padre: tk.Misc):
        super().__init__(padre, height=8, state="disabled")
        self.handler = TextoHandler(self)
        self.handler.setFormatter(logging.Formatter(FORMATO.replace("%(name)s: ", ""), "%H:%M:%S"))
        logging.getLogger().addHandler(self.handler)
        self.bind("<Destroy>", self._al_destruir)

    def _al_destruir(self, evento: tk.Event) -> None:
        if evento.widget is self:
            logging.getLogger().removeHandler(self.handler)