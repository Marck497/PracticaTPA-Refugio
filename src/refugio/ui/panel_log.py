"""Panel inferior que muestra los mensajes de log dentro de la ventana."""

import logging
import queue
import tkinter as tk
from tkinter import scrolledtext

from refugio.registro import FORMATO

INTERVALO_MS = 100 # cada cuánto vuelca el panel los mensajes pendientes

class TextoHandler(logging.Handler):
    """Handler de logging que escribe cada mensaje en una interfaz gráfica"""

    def __init__(self):
        super().__init__()
        self.cola: queue.Queue[str] = queue.Queue()

    def emit(self, record: logging.LogRecord) -> None:
        """Guarda el mensaje formateado en la cola; el panel lo escribe desde el hilo principal."""
        self.cola.put(self.format(record))


class PanelLog(scrolledtext.ScrolledText):
    """Cuadro de texto de solo lectura conectado al sistema de logging"""

    def __init__(self, padre: tk.Misc):
        super().__init__(padre, height=8, state="disabled")
        self.handler = TextoHandler()
        self.handler.setFormatter(logging.Formatter(FORMATO.replace("%(name)s: ", ""), "%H:%M:%S"))
        logging.getLogger().addHandler(self.handler)
        self._tarea = self.after(INTERVALO_MS, self._vaciar_cola)
        self.bind("<Destroy>", self._al_destruir)

    def _vaciar_cola(self) -> None:
        """Escribe los mensajes pendientes (se ejecuta en el hilo principal)"""
        while True:
            try:
                mensaje = self.handler.cola.get_nowait()
            except queue.Empty:
                break
            self._escribir(mensaje)
        self._tarea = self.after(INTERVALO_MS, self._vaciar_cola)

    def _escribir(self, mensaje: str) -> None:
        self.configure(state="normal")
        self.insert("end", mensaje + "\n")
        self.configure(state="disabled")
        self.see("end")

    def _al_destruir(self, evento: tk.Event) -> None:
        if evento.widget is self:
            logging.getLogger().removeHandler(self.handler)
            self.after_cancel(self._tarea)