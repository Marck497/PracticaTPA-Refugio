"""Ejecuta tareas lentas en un hilo para que la ventana no se congele."""

import queue
import threading
import tkinter as tk
from collections.abc import Callable
from typing import Any

class TareaSegundoPlano:
    """Lanza `tarea` en un hilo y avisa, en el hilo de tkinter, al terminar o fallar.

    - `tarea()` se ejecuta em el hilo secundario: NO debe tocar ningún widget.
    - `al_terminar(resultado)` y `al_fallar(error)` se ejecutan en el hilo principal,
    así que ahí sí se puede actualizar la interfaz.
    """
    def __init__(
            self,
            ventana: tk.Misc,
            tarea: Callable[[], Any],
            al_terminar: Callable[[Any], None],
            al_fallar: Callable[[Exception], None],
    ):
        self.ventana = ventana
        self.al_terminar = al_terminar
        self.al_fallar = al_fallar
        self.cola: queue.Queue[tuple[str, Any]] = queue.Queue()
        threading.Thread(target=self._trabajo, args=(tarea,), daemon=True).start()
        self.ventana.after(50, self._revisar)

    def _trabajo(self, tarea: Callable[[], Any]) -> None:
        """Se ejecuta en el hilo secundario"""
        try:
            self.cola.put(("ok", tarea()))
        except Exception as e:
            self.cola.put(("error", e))

    def _revisar(self) -> None:
        """Se ejecuta en el hilo principal"""
        try:
            estado, valor = self.cola.get_nowait()
        except queue.Empty:
            self.ventana.after(50, self._revisar)
            return
        (self.al_terminar if estado == "ok" else self.al_fallar)(valor)