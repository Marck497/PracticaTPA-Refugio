"""Protocolo Resumible: objetos que saben describirse con un método `resumen()`."""

from __future__ import annotations
from typing import Protocol, runtime_checkable

@runtime_checkable
class Resumible(Protocol):
    """
    Cualquier objeto que tenga un método resumen() -> str cumple este 
    protocolo, sin necesidad de heredar de ninguna clase común.
    """
    def resumen(self) -> str:
        """Devuelve un texto breve que describe el objeto."""
        ...

def mostrar_resumen(obj: Resumible) -> None:
    """Función polimórfica: opera sobre cualquier objeto que cumpla 
       resumible
    """
    print(obj.resumen())