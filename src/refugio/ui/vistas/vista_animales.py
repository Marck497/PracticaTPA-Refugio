"""Vista de animales: listado del refugio con búsqueda, filtro por estado y ficha."""

import tkinter as tk
from tkinter import ttk

from refugio.excepciones import AnimalNoEncontradoError
from refugio.modelo import Animal
from .base import Vista

COLUMNAS = ("chip", "nombre", "especie", "sexo", "peso", "edad", "estado")
ANCHOS = {"chip": 90, "nombre": 130, "especie": 90, "sexo": 80, "peso": 80, "edad": 60, "estado": 110}
TODOS = "Todos"

# Cómo se ordena el listado al pulsar la cabecera de cada columna
CLAVES_ORDEN = {
    "chip": lambda a: a.id_chip,
    "nombre": lambda a: a.nombre.lower(),
    "especie": lambda a: a.especie.lower(),
    "sexo": lambda a: a.sexo.lower(),
    "peso": lambda a: a.peso,
    "edad": lambda a: a.edad,
    "estado": lambda a: a.estado_adopcion,
}


class VistaAnimales(Vista):
    titulo = "Animales"

    def construir(self) -> None:
        self._orden: tuple[str, bool] = ("chip", False)  # (columna, descendente)
        self._visibles: list[Animal] = []  # animales mostrados, en el mismo orden que las filas

        # Barra superior: búsqueda, filtro por estado y contador
        barra = ttk.Frame(self, padding=(6, 6, 6, 3))
        barra.pack(side="top", fill="x")

        ttk.Label(barra, text="Buscar:").pack(side="left")
        self.busqueda = tk.StringVar()
        self.busqueda.trace_add("write", lambda *_: self.refrescar())
        ttk.Entry(barra, textvariable=self.busqueda, width=20).pack(side="left", padx=(4, 12))

        ttk.Label(barra, text="Estado:").pack(side="left")
        self.filtro_estado = tk.StringVar(value=TODOS)
        combo = ttk.Combobox(
            barra,
            textvariable=self.filtro_estado,
            values=(TODOS, *sorted(Animal.ESTADOS_ADOPCION_VALIDOS)),
            state="readonly",
            width=14,
        )
        combo.pack(side="left", padx=4)
        combo.bind("<<ComboboxSelected>>", lambda _: self.refrescar())

        self.contador = ttk.Label(barra)
        self.contador.pack(side="right")

        # Ficha del animal seleccionado (abajo; se empaqueta antes que la tabla)
        ficha = ttk.LabelFrame(self, text="Ficha del animal", padding=6)
        ficha.pack(side="bottom", fill="x", padx=6, pady=6)
        self.texto_ficha = tk.StringVar()
        ttk.Label(ficha, textvariable=self.texto_ficha, justify="left").pack(anchor="w")

        # Tabla (ocupa el espacio restante)
        self.tabla = self.crear_tabla(COLUMNAS)
        for columna in COLUMNAS:
            self.tabla.column(columna, width=ANCHOS[columna], anchor="w")
            self.tabla.heading(columna, command=lambda c=columna: self._ordenar_por(c))
        self.tabla.bind("<<TreeviewSelect>>", lambda _: self._mostrar_ficha())

        self._mostrar_ficha()

    def refrescar(self) -> None:
        # Recordamos la selección para no perderla al repintar
        seleccionado = self._animal_seleccionado()

        self._visibles = self._filtrar_y_ordenar()
        self.rellenar_tabla(self.tabla, (self._fila(a) for a in self._visibles))

        if seleccionado in self._visibles:  # Animal compara por chip
            item = self.tabla.get_children()[self._visibles.index(seleccionado)]
            self.tabla.selection_set(item)
        self._mostrar_ficha()

        total = len(self.refugio.animales)
        self.contador.configure(
            text=f"Mostrando {len(self._visibles)} de {total} "
                 f"(capacidad {self.refugio.capacidad_maxima})"
        )

    # Lógica de la vista

    def _filtrar_y_ordenar(self) -> list[Animal]:
        texto = self.busqueda.get().strip().lower()
        estado = self.filtro_estado.get()

        animales = [
            a for a in self.refugio.animales
            if (estado == TODOS or a.estado_adopcion == estado)
            and (not texto or texto in a.nombre.lower() or texto in a.especie.lower()
                 or texto in a.id_chip.lower())
        ]
        columna, descendente = self._orden
        return sorted(animales, key=CLAVES_ORDEN[columna], reverse=descendente)

    @staticmethod
    def _fila(a: Animal) -> tuple:
        return (a.id_chip, a.nombre, a.especie, a.sexo, f"{a.peso:.1f} kg", a.edad, a.estado_adopcion)

    def _ordenar_por(self, columna: str) -> None:
        """Pulsar la misma cabecera dos veces invierte el orden."""
        anterior, descendente = self._orden
        self._orden = (columna, not descendente if columna == anterior else False)
        self.refrescar()

    def _animal_seleccionado(self) -> Animal | None:
        seleccion = self.tabla.selection()
        if not seleccion:
            return None
        return self._visibles[self.tabla.index(seleccion[0])]

    def _mostrar_ficha(self) -> None:
        animal = self._animal_seleccionado()
        if animal is None:
            self.texto_ficha.set("Selecciona un animal de la lista para ver sus detalles.")
            return
        try:
            a = self.refugio.buscar_animal_por_chip(animal.id_chip)
        except AnimalNoEncontradoError as error:
            self.mostrar_error(error)
            return

        anio, mes, dia = a.fecha_nacimiento
        voluntarios = ", ".join(v.nombre for v in a.voluntarios_asignados) or "ninguno"
        self.texto_ficha.set(
            f"{a.nombre} ({a.especie}, {a.sexo}) - chip {a.id_chip}\n"
            f"Nacimiento: {dia:02d}/{mes:02d}/{anio} ({a.edad} años) - Peso: {a.peso:.1f} kg\n"
            f"Estado de adopción: {a.estado_adopcion}\n"
            f"Revisiones veterinarias: {len(a.historial_veterinario)}\n"
            f"Voluntarios asignados: {voluntarios}"
        )