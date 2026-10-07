"""
Apartado 4.1 - Estructura genérica: repositorio tipado.

Repositorio[T] guarda objetos de CUALQUIER tipo T del modelo (Animal,
Voluntario, Adoptante...) indexados por una clave. La misma implementación
sirve para todos, pero el verificador de tipos (mypy/pyright) distingue
Repositorio[Animal] de Repositorio[Voluntario].
"""

from typing import Callable, Generic, Iterator, TypeVar

T = TypeVar("T")


class ElementoDuplicadoError(Exception):
    """Se lanza al añadir un elemento cuya clave ya existe en el repositorio."""


class ElementoNoEncontradoError(Exception):
    """Se lanza al pedir un elemento cuya clave no existe en el repositorio."""


class Repositorio(Generic[T]):
    """Colección tipada de elementos T, identificados por una clave única."""

    def __init__(self, clave: Callable[[T], str]) -> None:
        # 'clave' extrae el identificador de cada elemento (p. ej. el chip o el DNI)
        self._clave = clave
        self._items: dict[str, T] = {}

    def anadir(self, item: T) -> None:
        k = self._clave(item)
        if k in self._items:
            raise ElementoDuplicadoError(f"Ya existe un elemento con clave {k!r}")
        self._items[k] = item

    def obtener(self, clave: str) -> T:
        try:
            return self._items[clave]
        except KeyError:
            raise ElementoNoEncontradoError(f"No hay ningún elemento con clave {clave!r}") from None

    def eliminar(self, clave: str) -> T:
        item = self.obtener(clave)
        del self._items[clave]
        return item

    def todos(self) -> list[T]:
        return list(self._items.values())

    def __contains__(self, clave: str) -> bool:
        return clave in self._items

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[T]:
        return iter(self._items.values())

    def __repr__(self) -> str:
        return f"Repositorio({len(self)} elementos)"