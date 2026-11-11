"""Patrón observer: permite que otros objetos se suscriban a eventos del refugio"""

from collections.abc import Callable
from typing import Any

class Observable:
    """Mantiene una lista de suscriptores por evento y los avisa cuando ocurre"""

    def __init__(self) -> None:
        self._suscriptores: dict[str, list[Callable[..., None]]] = {}

    def suscribir(self, evento: str, function: Callable[..., None]) -> None:
        """Registra una función que se llamará cada vez que ocurra el evento."""
        self._suscriptores.setdefault(evento, []).append(function)

    def desuscribir(self, evento: str, function: Callable[..., None]) -> None:
        """Deja de avisar a esa función (necesario al cerrar una ventana)"""
        self._suscriptores.get(evento, []).remove(function)

    def _notificar(self, evento: str, **datos: Any) -> None:
        for function in list(self._suscriptores.get(evento, [])):
            function(**datos)