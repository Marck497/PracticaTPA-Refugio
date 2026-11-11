"""Vista de voluntarios."""

from functools import partial
import tkinter as tk
from tkinter import messagebox, ttk

from refugio import RefugioError, Voluntario
from .base import Vista

COLUMNAS = ("dni", "nombre", "telefono", "area", "animales")
AREAS_DISPONIBLES = ["Perros", "Gatos", "Exóticos", "Rehabilitación", "Adopciones"]


class VistaVoluntarios(Vista):
    titulo = "Voluntarios"

    def construir(self) -> None:
        # Variables de control para la ordenación de la tabla
        self._sort_col = None
        self._sort_reverse = False

        # Barra superior con botones de acción
        barra_superior = ttk.Frame(self, padding=(10, 10))
        barra_superior.pack(side="top", fill="x")

        ttk.Button(barra_superior, text="Asignar a animal", command=self._on_asignar_click).pack(side="left", padx=5)
        ttk.Button(barra_superior, text="Nuevo voluntario", command=self._on_nuevo_click).pack(side="left", padx=5)
        ttk.Button(barra_superior, text="Modificar", command=self._on_modificar_click).pack(side="left", padx=5)
        ttk.Button(barra_superior, text="Eliminar", command=self._on_eliminar_click).pack(side="left", padx=5)
        ttk.Button(barra_superior, text="Ver Animales", command=self._on_ver_animales_click).pack(side="left", padx=5)

        # Barra de búsqueda (por nombre, DNI, teléfono, área...)
        barra_busqueda = ttk.Frame(self, padding=(10, 0, 10, 10))
        barra_busqueda.pack(side="top", fill="x")

        ttk.Label(barra_busqueda, text="🔍 Buscar:").pack(side="left", padx=(0, 5))
        self.entry_buscar = ttk.Entry(barra_busqueda, width=30)
        self.entry_buscar.pack(side="left", padx=5)
        self.entry_buscar.bind("<KeyRelease>", lambda event: self.refrescar())

        ttk.Button(barra_busqueda, text="Limpiar", command=self._limpiar_busqueda).pack(side="left", padx=5)

        # Contenedor de la tabla estándar
        contenedor_tabla = ttk.Frame(self, padding=(10, 0, 10, 10))
        contenedor_tabla.pack(side="top", fill="both", expand=True)

        self.tabla = self.crear_tabla(COLUMNAS)
        self.tabla.pack_forget()
        self.tabla.pack(in_=contenedor_tabla, fill="both", expand=True)

        cabeceras = {
            "dni": "DNI",
            "nombre": "Nombre y Apellidos",
            "telefono": "Teléfono",
            "area": "Área Asignada",
            "animales": "Animales"
        }
        for col in COLUMNAS:
            self.tabla.heading(col, text=cabeceras.get(col, col.capitalize()), command=partial(self._ordenar_por, col))
            self.tabla.column(col, anchor="center", width=130)

        # Evento de doble clic para ver animales asignados
        self.tabla.bind("<Double-1>", lambda event: self._on_ver_animales_click())
        self.refrescar()

    def _ordenar_por(self, col: str) -> None:
        if self._sort_col == col:
            self._sort_reverse = not self._sort_reverse
        else:
            self._sort_col = col
            self._sort_reverse = False
        self.refrescar()

    def _limpiar_busqueda(self) -> None:
        self.entry_buscar.delete(0, tk.END)
        self.refrescar()

    def _validar_dni_simple(self, dni: str) -> bool:
        dni = dni.upper().strip()
        if len(dni) != 9:
            return False
        return dni[:8].isdigit() and dni[8].isalpha()

    def _on_ver_animales_click(self) -> None:
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showinfo("Aviso", "Por favor, selecciona un voluntario de la tabla.")
            return

        indice_fila = self.tabla.index(seleccion)
        filtrados = self._obtener_voluntarios_filtrados()
        if indice_fila >= len(filtrados):
            return
        voluntario = filtrados[indice_fila]

        animales_asignados = [a for a in self.refugio.animales if voluntario in a.voluntarios_asignados]

        ventana = tk.Toplevel(self)
        ventana.title(f"Animales de {voluntario.nombre}")
        ventana.geometry("400x300")
        ventana.resizable(False, False)
        ventana.grab_set()

        frame = ttk.Frame(ventana, padding=15)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text=f"Voluntario: {voluntario.nombre} (DNI: {voluntario.dni})", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        ttk.Label(frame, text="Animales asignados a su cargo:").pack(anchor="w", pady=5)

        listbox_frame = ttk.Frame(frame)
        listbox_frame.pack(fill="both", expand=True, pady=5)

        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical")
        listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set, width=50, height=6)
        scrollbar.config(command=listbox.yview)
        scrollbar.pack(side="right", fill="y")
        listbox.pack(side="left", fill="both", expand=True)

        if animales_asignados:
            for a in animales_asignados:
                listbox.insert(tk.END, f"Chip: {a.id_chip} - {a.nombre} ({getattr(a, 'especie', 'Animal')})")
        else:
            listbox.insert(tk.END, "No tiene ningún animal asignado actualmente.")

        btn_desvincular = ttk.Button(
            frame,
            text="Desvincular animal seleccionado",
            command=lambda: self._desvincular_animal(voluntario, listbox, animales_asignados, ventana)
        )
        btn_desvincular.pack(pady=(10, 0), fill="x")

    def _desvincular_animal(self, voluntario: Voluntario, listbox: tk.Listbox, animales_asignados: list, ventana: tk.Toplevel) -> None:
        seleccion_lb = listbox.curselection()
        if not seleccion_lb:
            messagebox.showinfo("Aviso", "Selecciona un animal de la lista para desvincular.")
            return

        indice = seleccion_lb[0]
        if indice >= len(animales_asignados):
            return

        animal = animales_asignados[indice]
        if messagebox.askyesno("Confirmar", f"¿Deseas desvincular a {voluntario.nombre} del animal {animal.nombre}?"):
            try:
                self.refugio.desvincular_voluntario(voluntario, animal.id_chip)
            except (ValueError, RefugioError) as e:
                self.mostrar_error(e)
                return
            ventana.destroy()
            self.refrescar()
            messagebox.showinfo("Éxito", "Animal desvinculado correctamente.")

    def _obtener_voluntarios_filtrados(self) -> list:
        texto_busqueda = self.entry_buscar.get().strip().lower()
        if not texto_busqueda:
            filtrados = list(self.refugio.voluntarios)
        else:
            filtrados = []
            for v in self.refugio.voluntarios:
                num_anim = str(sum(1 for a in self.refugio.animales if v in a.voluntarios_asignados))
                if (texto_busqueda in v.dni.lower() or
                    texto_busqueda in v.nombre.lower() or
                    texto_busqueda in v.telefono.lower() or
                    texto_busqueda in v.area_asignada.lower() or
                    texto_busqueda == num_anim):
                    filtrados.append(v)
        
        if self._sort_col:
            col = self._sort_col
            reverse = self._sort_reverse
            if col == "dni":
                filtrados.sort(key=lambda x: x.dni, reverse=reverse)
            elif col == "nombre":
                filtrados.sort(key=lambda x: x.nombre, reverse=reverse)
            elif col == "telefono":
                filtrados.sort(key=lambda x: x.telefono, reverse=reverse)
            elif col == "area":
                filtrados.sort(key=lambda x: x.area_asignada, reverse=reverse)
            elif col == "animales":
                filtrados.sort(key=lambda x: sum(1 for a in self.refugio.animales if x in a.voluntarios_asignados), reverse=reverse)

        return filtrados

    def _on_asignar_click(self) -> None:
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showinfo("Aviso", "Por favor, selecciona un voluntario.")
            return

        indice_fila = self.tabla.index(seleccion)
        filtrados = self._obtener_voluntarios_filtrados()
        voluntario = filtrados[indice_fila]

        ventana = tk.Toplevel(self)
        ventana.title(f"Asignar animal a {voluntario.nombre}")
        ventana.geometry("380x160")
        ventana.resizable(False, False)
        ventana.grab_set()

        frame = ttk.Frame(ventana, padding=15)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Selecciona Animal (Chip - Nombre - Especie):").pack(anchor="w", pady=5)
        chips_detallados = [f"{a.id_chip} - {a.nombre} ({getattr(a, 'especie', 'Animal')})" for a in self.refugio.animales]
        desplegable = ttk.Combobox(frame, values=chips_detallados, state="readonly", width=45)
        desplegable.pack(fill="x", pady=5)

        ttk.Button(
            frame,
            text="Asignar",
            command=partial(self._ejecutar_asignacion, voluntario, desplegable, ventana)
        ).pack(pady=10)

    def _ejecutar_asignacion(self, voluntario: Voluntario, desplegable: ttk.Combobox, ventana: tk.Toplevel) -> None:
        seleccion_combo = desplegable.get().strip()
        if not seleccion_combo:
            self.mostrar_error(ValueError("Selecciona un animal válido."))
            return

        chip = seleccion_combo.split(" - ")[0].strip()
        animal = self.refugio.buscar_animal_por_chip(chip)
        voluntarios_antes = len(animal.voluntarios_asignados)

        try:
            self.refugio.asignar_voluntario(voluntario, chip)
            voluntarios_despues = len(animal.voluntarios_asignados)
            if voluntarios_antes == voluntarios_despues:
                messagebox.showinfo("Aviso", "El voluntario ya estaba asignado a este animal.")
            ventana.destroy()
            self.refrescar()
        except RefugioError as e:
            self.mostrar_error(e)

    def _on_nuevo_click(self) -> None:
        ventana = tk.Toplevel(self)
        ventana.title("Nuevo voluntario")
        ventana.geometry("400x320")
        ventana.resizable(False, False)
        ventana.grab_set()

        frame = ttk.Frame(ventana, padding=15)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="DNI:").grid(row=0, column=0, sticky="e", padx=5, pady=4)
        entry_dni = ttk.Entry(frame, width=28)
        entry_dni.grid(row=0, column=1, sticky="w", pady=4)

        ttk.Label(frame, text="Nombre:").grid(row=1, column=0, sticky="e", padx=5, pady=4)
        entry_nombre = ttk.Entry(frame, width=28)
        entry_nombre.grid(row=1, column=1, sticky="w", pady=4)

        ttk.Label(frame, text="Teléfono (9 dígitos):").grid(row=2, column=0, sticky="e", padx=5, pady=4)
        entry_telefono = ttk.Entry(frame, width=28)
        entry_telefono.grid(row=2, column=1, sticky="w", pady=4)

        ttk.Label(frame, text="Área Asignada:").grid(row=3, column=0, sticky="e", padx=5, pady=4)
        combo_area = ttk.Combobox(frame, values=AREAS_DISPONIBLES, state="readonly", width=26)
        combo_area.grid(row=3, column=1, sticky="w", pady=4)

        ttk.Label(frame, text="Animal Asignado:").grid(row=4, column=0, sticky="e", padx=5, pady=4)
        chips_detallados = [f"{a.id_chip} - {a.nombre} ({getattr(a, 'especie', 'Animal')})" for a in self.refugio.animales]
        combo_chip = ttk.Combobox(frame, values=chips_detallados, state="readonly", width=26)
        combo_chip.grid(row=4, column=1, sticky="w", pady=4)

        entradas = {"dni": entry_dni, "nombre": entry_nombre, "telefono": entry_telefono, "area": combo_area}

        ttk.Button(
            frame,
            text="Guardar",
            command=partial(self._guardar_nuevo_voluntario, ventana, entradas, combo_chip)
        ).grid(row=5, column=0, columnspan=2, pady=15)

    def _guardar_nuevo_voluntario(self, ventana: tk.Toplevel, entradas: dict, combo_chip: ttk.Combobox) -> None:
        dni = entradas["dni"].get().strip()
        nombre = entradas["nombre"].get().strip()
        telefono = entradas["telefono"].get().strip()
        area = entradas["area"].get().strip()
        seleccion_chip = combo_chip.get().strip()

        if not (dni and nombre and telefono and area and seleccion_chip):
            self.mostrar_error(ValueError("Rellena todos los campos"))
            return

        if not self._validar_dni_simple(dni):
            self.mostrar_error(ValueError("DNI inválido. Debe tener 8 números y una letra al final."))
            return

        if not telefono.isdigit() or len(telefono) != 9:
            self.mostrar_error(ValueError("El teléfono debe contener exactamente 9 dígitos numéricos."))
            return

        for v in self.refugio.voluntarios:
            if v.dni.upper() == dni.upper():
                self.mostrar_error(RefugioError(f"El DNI {dni} ya está registrado."))
                return

        chip = seleccion_chip.split(" - ")[0].strip()

        try:
            nuevo = Voluntario(dni.upper(), nombre, telefono, area)
            self.refugio.asignar_voluntario(nuevo, chip)
            ventana.destroy()
            self.refrescar()
        except RefugioError as e:
            self.mostrar_error(e)

    def _on_modificar_click(self) -> None:
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showinfo("Aviso", "Por favor, selecciona un voluntario.")
            return

        indice_fila = self.tabla.index(seleccion)
        filtrados = self._obtener_voluntarios_filtrados()
        voluntario = filtrados[indice_fila]

        ventana = tk.Toplevel(self)
        ventana.title(f"Modificar: {voluntario.nombre}")
        ventana.geometry("340x240")
        ventana.resizable(False, False)
        ventana.grab_set()

        frame = ttk.Frame(ventana, padding=15)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="DNI (No editable):").grid(row=0, column=0, sticky="e", padx=5, pady=6)
        ttk.Label(frame, text=voluntario.dni, font=("Arial", 9, "bold")).grid(row=0, column=1, sticky="w", pady=6)

        ttk.Label(frame, text="Nombre:").grid(row=1, column=0, sticky="e", padx=5, pady=6)
        entry_nombre = ttk.Entry(frame, width=20)
        entry_nombre.insert(0, voluntario.nombre)
        entry_nombre.grid(row=1, column=1, sticky="w", pady=6)

        ttk.Label(frame, text="Teléfono:").grid(row=2, column=0, sticky="e", padx=5, pady=6)
        entry_telefono = ttk.Entry(frame, width=20)
        entry_telefono.insert(0, voluntario.telefono)
        entry_telefono.grid(row=2, column=1, sticky="w", pady=6)

        ttk.Label(frame, text="Área Asignada:").grid(row=3, column=0, sticky="e", padx=5, pady=6)
        combo_area = ttk.Combobox(frame, values=AREAS_DISPONIBLES, state="readonly", width=18)
        combo_area.set(voluntario.area_asignada)
        combo_area.grid(row=3, column=1, sticky="w", pady=6)

        entradas = {"nombre": entry_nombre, "telefono": entry_telefono, "area": combo_area}

        ttk.Button(
            frame,
            text="Actualizar",
            command=partial(self._guardar_modificacion, ventana, voluntario, entradas)
        ).grid(row=4, column=0, columnspan=2, pady=15)

    def _guardar_modificacion(self, ventana: tk.Toplevel, voluntario: Voluntario, entradas: dict) -> None:
        nombre = entradas["nombre"].get().strip()
        telefono = entradas["telefono"].get().strip()
        area = entradas["area"].get().strip()

        if not (nombre and telefono and area):
            self.mostrar_error(ValueError("Rellena todos los campos"))
            return

        if not telefono.isdigit() or len(telefono) != 9:
            self.mostrar_error(ValueError("El teléfono debe contener exactamente 9 dígitos numéricos."))
            return

        try:
            self.refugio.modificar_voluntario(voluntario, nombre, telefono, area)
        except (ValueError, RefugioError) as e:
            self.mostrar_error(e)
            return
        ventana.destroy()
        self.refrescar()

    def _on_eliminar_click(self) -> None:
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showinfo("Aviso", "Por favor, selecciona un voluntario.")
            return

        indice_fila = self.tabla.index(seleccion)
        filtrados = self._obtener_voluntarios_filtrados()
        voluntario = filtrados[indice_fila]

        if messagebox.askyesno("Eliminar", f"¿Seguro que deseas eliminar a {voluntario.nombre}?"):
            try:
                self.refugio.eliminar_voluntario(voluntario)
            except (ValueError, RefugioError) as e:
                self.mostrar_error(e)
                return
            self.refrescar()

    def refrescar(self) -> None:
        filas_datos = []
        voluntarios_a_mostrar = self._obtener_voluntarios_filtrados()
        
        for v in voluntarios_a_mostrar:
            num_animales = sum(1 for a in self.refugio.animales if v in a.voluntarios_asignados)
            filas_datos.append((
                v.dni,
                v.nombre,
                v.telefono,
                v.area_asignada,
                str(num_animales)
            ))
        self.rellenar_tabla(self.tabla, filas_datos)