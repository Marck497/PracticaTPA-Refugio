"""Vista de animales: listado del refugio con búsqueda, filtro por estado y ficha."""

from datetime import date
from functools import partial
import tkinter as tk
from tkinter import messagebox, ttk

from refugio.excepciones import AnimalNoEncontradoError, RefugioError
from refugio.modelo import Animal
from refugio.validacion import RegistroInvalido, validar_chip
from .base import Vista

COLUMNAS = ("chip", "nombre", "especie", "sexo", "peso", "edad", "estado")
ANCHOS = {"chip": 90, "nombre": 130, "especie": 90, "sexo": 80, "peso": 80, "edad": 60, "estado": 110}
TODOS = "Todos"
SEXOS = ("Macho", "Hembra")

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
    """Listado de animales: buscar, filtrar por estado, ordenar, ver ficha, registrar ingreso y eliminar."""

    titulo = "Animales"

    def construir(self) -> None:
        """Crea la barra de búsqueda y filtro, la tabla y la ficha del animal."""

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

        ttk.Button(barra, text="Eliminar animal", command= self._on_eliminar_click).pack(side="left", padx=(0, 12))
        ttk.Button(barra, text="Registrar ingreso", command=self._on_ingreso_click).pack(side="left", padx=(0, 12))

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
        """Vuelve a rellenar la tabla respetando búsqueda, filtro, orden y selección."""

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

    def _on_eliminar_click(self) -> None:
        animal = self._animal_seleccionado()
        if animal is None:
            messagebox.showinfo("Aviso", "Selecciona un animal de la lista.")
            return
        if not messagebox.askyesno("Eliminar", f"¿Eliminar a {animal.nombre} (chip {animal.id_chip}) del refugio?"):
            return
        try:
            self.refugio.eliminar_animal(animal)
        except (ValueError, RefugioError) as e:
            self.mostrar_error(e)
            return
        self.refrescar()
        

    def _on_ingreso_click(self) -> None:
        ventana = tk.Toplevel(self)
        ventana.title("Registrar ingreso")
        ventana.resizable(False, False)
        ventana.grab_set()

        marco = ttk.Frame(ventana, padding=15)
        marco.pack()
        etiquetas = (
            ("chip", "Chip (CHIP001):"),
            ("nombre", "Nombre:"),
            ("especie", "Especie:"),
            ("sexo", "Sexo:"),
            ("peso", "Peso (kg):"),
            ("nacimiento", "Nacimiento (AAAA-MM-DD):"),
        )
        campos: dict[str, ttk.Entry] = {}
        for fila, (clave, texto) in enumerate(etiquetas):
            ttk.Label(marco, text=texto).grid(row=fila, column=0, sticky="e", padx=5, pady=4)
            if clave == "sexo":
                campo = ttk.Combobox(marco, values=SEXOS, state="readonly", width=26)
            else:
                campo = ttk.Entry(marco, width=28)
            campo.grid(row=fila, column=1, sticky="w", pady=4)
            campos[clave] = campo

        ttk.Button(
            marco, text="Guardar", command=partial(self._guardar_ingreso, ventana, campos)
        ).grid(row=len(etiquetas), column=0, columnspan=2, pady=(12, 0))

    def _guardar_ingreso(self, ventana: tk.Toplevel, campos: dict[str, ttk.Entry]) -> None:
        try:
            animal = self._leer_animal(campos)
            if animal in self.refugio.animales:
                raise ValueError(f"Ya existe un animnal con el chip {animal.id_chip}.")
            self.refugio.registrar_ingreso(animal)
        except (ValueError, RefugioError, RegistroInvalido) as e:
            self.mostrar_error(e)
            return
        ventana.destroy()
        self.refrescar()
        messagebox.showinfo("Éxito", f"{animal.nombre} ha ingresado en el refugio.")

    @staticmethod
    def _leer_animal(campos: dict[str, ttk.Entry]) -> Animal:
        """Valida lo escrito en el formulario y constuye el Animal."""
        datos = {clave: campo.get().strip() for clave, campo in campos.items()}
        if not all(datos.values()):
            raise ValueError("Rellena todos los datos.")
        chip = validar_chip({"id_chip": datos["chip"].upper()})
        try:
            peso = float(datos["peso"].replace(",", "."))
        except ValueError:
            raise ValueError("El peso debe ser un número (por ejemplo 12.5).") from None
        if peso <= 0:
            raise ValueError("El peso debe ser mayor que 0.")
        try:
            nacimiento = date.fromisoformat(datos["nacimiento"])
        except ValueError:
            raise ValueError("La fecha debe tener formato AAAA-MM-DD.") from None
        if nacimiento > date.today():
            raise ValueError("La fecha de nacimiento no puede ser futura.")
        return Animal(
            chip, datos["nombre"], datos["especie"], peso, datos["sexo"],
            (nacimiento.year, nacimiento.month, nacimiento.day),
        )