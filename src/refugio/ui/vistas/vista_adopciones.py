"""Vista de gestión de adopciones del refugio."""

from datetime import date
from functools import partial
import tkinter as tk
from tkinter import messagebox, ttk

from refugio import Adoptante, RefugioError
from .base import Vista


COLUMNAS = ("chip", "animal", "dni", "adoptante", "telefono", "correo", "fecha")


class VistaAdopciones(Vista):
    titulo = "Adopciones"

    def construir(self) -> None:
        self._sort_col = None
        self._sort_reverse = False

        barra_superior = ttk.Frame(self, padding=(10, 10))
        barra_superior.pack(side="top", fill="x")

        ttk.Button(barra_superior, text="Nueva adopción", command=self._on_nuevo_click).pack(side="left", padx=5)
        ttk.Button(barra_superior, text="Modificar", command=self._on_modificar_click).pack(side="left", padx=5)
        ttk.Button(barra_superior, text="Eliminar", command=self._on_eliminar_click).pack(side="left", padx=5)
        ttk.Button(barra_superior, text="Ver detalles", command=self._on_ver_detalles_click).pack(side="left", padx=5)

        barra_busqueda = ttk.Frame(self, padding=(10, 0, 10, 10))
        barra_busqueda.pack(side="top", fill="x")
        ttk.Label(barra_busqueda, text="Buscar:").pack(side="left", padx=(0, 5))
        self.entry_buscar = ttk.Entry(barra_busqueda, width=30)
        self.entry_buscar.pack(side="left", padx=5)
        self.entry_buscar.bind("<KeyRelease>", lambda event: self.refrescar())
        ttk.Button(barra_busqueda, text="Limpiar", command=self._limpiar_busqueda).pack(side="left", padx=5)

        contenedor_tabla = ttk.Frame(self, padding=(10, 0, 10, 10))
        contenedor_tabla.pack(side="top", fill="both", expand=True)
        self.tabla = self.crear_tabla(COLUMNAS)
        self.tabla.pack_forget()
        self.tabla.pack(in_=contenedor_tabla, fill="both", expand=True)

        cabeceras = {
            "chip": "Chip", "animal": "Animal", "dni": "DNI",
            "adoptante": "Adoptante", "telefono": "Teléfono",
            "correo": "Correo", "fecha": "Fecha de adopción",
        }
        for col in COLUMNAS:
            self.tabla.heading(col, text=cabeceras[col], command=partial(self._ordenar_por, col))
            self.tabla.column(col, anchor="center", width=140)
        self.tabla.column("correo", width=200)
        self.tabla.bind("<Double-1>", lambda event: self._on_ver_detalles_click())
        self.refrescar()

    def _mostrar_error(self, error: Exception) -> None:
        self.mostrar_error(error)

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

    def _obtener_adopciones_filtradas(self) -> list:
        texto = self.entry_buscar.get().strip().lower()
        adopciones = [
            a for a in self.refugio.adopciones
            if not texto or any(texto in campo.lower() for campo in (
                a.animal.id_chip, a.animal.nombre, a.adoptante.dni,
                a.adoptante.nombre, a.adoptante.telefono,
                a.adoptante.correo, a.fecha.isoformat(),
            ))
        ]
        if self._sort_col:
            claves = {
                "chip": lambda a: a.animal.id_chip.lower(),
                "animal": lambda a: a.animal.nombre.lower(),
                "dni": lambda a: a.adoptante.dni.lower(),
                "adoptante": lambda a: a.adoptante.nombre.lower(),
                "telefono": lambda a: a.adoptante.telefono,
                "correo": lambda a: a.adoptante.correo.lower(),
                "fecha": lambda a: a.fecha,
            }
            adopciones.sort(key=claves[self._sort_col], reverse=self._sort_reverse)
        return adopciones

    def _adopcion_seleccionada(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showinfo("Aviso", "Selecciona una adopción de la tabla.")
            return None
        indice = self.tabla.index(seleccion[0])
        adopciones = self._obtener_adopciones_filtradas()
        return adopciones[indice] if indice < len(adopciones) else None

    @staticmethod
    def _validar_dni(dni: str) -> bool:
        return len(dni) == 9 and dni[:8].isdigit() and dni[8].isalpha()

    def _leer_datos(self, entradas: dict) -> tuple:
        dni = entradas["dni"].get().strip().upper()
        nombre = entradas["nombre"].get().strip()
        telefono = entradas["telefono"].get().strip()
        correo = entradas["correo"].get().strip()
        fecha_texto = entradas["fecha"].get().strip()
        max_texto = entradas["max_adopciones"].get().strip()

        if not all((dni, nombre, telefono, correo, fecha_texto, max_texto)):
            raise ValueError("Rellena todos los campos.")
        if not self._validar_dni(dni):
            raise ValueError("El DNI debe tener 8 números y una letra.")
        if not telefono.isdigit() or len(telefono) != 9:
            raise ValueError("El teléfono debe contener exactamente 9 dígitos.")
        if "@" not in correo or "." not in correo.split("@")[-1]:
            raise ValueError("Introduce un correo electrónico válido.")
        try:
            max_adopciones = int(max_texto)
        except ValueError:
            raise ValueError("El máximo de adopciones debe ser un número entero.") from None
        if max_adopciones <= 0:
            raise ValueError("El máximo de adopciones debe ser positivo.")
        try:
            fecha = date.fromisoformat(fecha_texto)
        except ValueError:
            raise ValueError("La fecha debe tener formato AAAA-MM-DD.") from None
        if fecha > date.today():
            raise ValueError("La fecha de adopción no puede ser futura.")
        return dni, nombre, telefono, correo, max_adopciones, fecha

    def _crear_formulario(self, ventana, adopcion=None) -> dict:
        frame = ttk.Frame(ventana, padding=15)
        frame.pack(fill="both", expand=True)
        entradas = {}
        datos = (
            ("dni", "DNI", adopcion.adoptante.dni if adopcion else ""),
            ("nombre", "Nombre", adopcion.adoptante.nombre if adopcion else ""),
            ("telefono", "Teléfono", adopcion.adoptante.telefono if adopcion else ""),
            ("correo", "Correo", adopcion.adoptante.correo if adopcion else ""),
            ("max_adopciones", "Máximo de adopciones", str(adopcion.adoptante.max_adopciones) if adopcion else "3"),
            ("fecha", "Fecha (AAAA-MM-DD)", adopcion.fecha.isoformat() if adopcion else date.today().isoformat()),
        )
        for fila, (clave, etiqueta, valor) in enumerate(datos):
            ttk.Label(frame, text=etiqueta + ":").grid(row=fila, column=0, sticky="e", padx=5, pady=5)
            entrada = ttk.Entry(frame, width=32)
            entrada.insert(0, valor)
            entrada.grid(row=fila, column=1, sticky="w", pady=5)
            if adopcion and clave == "dni":
                entrada.configure(state="readonly")
            entradas[clave] = entrada
        return entradas

    def _on_nuevo_click(self) -> None:
        disponibles = [a for a in self.refugio.animales if a.esta_disponible()]
        if not disponibles:
            messagebox.showinfo("Aviso", "No hay animales disponibles para adoptar.")
            return
        ventana = tk.Toplevel(self)
        ventana.title("Nueva adopción")
        ventana.geometry("510x395")
        ventana.resizable(False, False)
        ventana.grab_set()
        frame_animal = ttk.Frame(ventana, padding=(15, 12, 15, 0))
        frame_animal.pack(fill="x")
        ttk.Label(frame_animal, text="Animal:").pack(side="left", padx=(0, 8))
        opciones = [f"{a.id_chip} - {a.nombre} ({a.especie})" for a in disponibles]
        combo_animal = ttk.Combobox(frame_animal, values=opciones, state="readonly", width=43)
        combo_animal.pack(side="left")
        entradas = self._crear_formulario(ventana)
        ttk.Button(ventana, text="Guardar adopción", command=partial(
            self._guardar_nueva, ventana, entradas, combo_animal
        )).pack(pady=(0, 12))

    def _guardar_nueva(self, ventana, entradas: dict, combo_animal) -> None:
        try:
            seleccion = combo_animal.get().strip()
            if not seleccion:
                raise ValueError("Selecciona un animal.")
            dni, nombre, telefono, correo, max_adopciones, fecha = self._leer_datos(entradas)
            chip = seleccion.split(" - ", 1)[0]
            # El gestor se encarga de comprobar disponibilidad y marcar 'adoptado'.
            animal = self.refugio.buscar_animal_por_chip(chip)
            if not animal.esta_disponible():
                raise ValueError("El animal ya no está disponible.")
            anteriores = [a for a in self.refugio.adopciones if a.adoptante.dni.upper() == dni]
            if len(anteriores) >= max_adopciones:
                raise ValueError("Este adoptante ha alcanzado su máximo de adopciones.")
            if anteriores:
                existente = anteriores[0].adoptante
                if (existente.nombre != nombre or existente.telefono != telefono
                        or existente.correo != correo or existente.max_adopciones != max_adopciones):
                    raise ValueError("El DNI ya existe con otros datos. Usa los datos del adoptante registrado.")
                adoptante = existente
            else:
                adoptante = Adoptante(dni, nombre, telefono, correo, max_adopciones)
            self.refugio.tramitar_adopcion(chip, adoptante, fecha)
        except (ValueError, RefugioError) as e:
            self._mostrar_error(e)
            return
        ventana.destroy()
        self.refrescar()
        messagebox.showinfo("Éxito", "Adopción registrada correctamente.")

    def _on_modificar_click(self) -> None:
        adopcion = self._adopcion_seleccionada()
        if adopcion is None:
            return
        ventana = tk.Toplevel(self)
        ventana.title(f"Modificar adopción: {adopcion.animal.nombre}")
        ventana.geometry("480x370")
        ventana.resizable(False, False)
        ventana.grab_set()
        ttk.Label(ventana, text=f"Animal: {adopcion.animal.nombre} (chip {adopcion.animal.id_chip})",
                  font=("Arial", 10, "bold")).pack(pady=(12, 0))
        entradas = self._crear_formulario(ventana, adopcion)
        ttk.Button(ventana, text="Actualizar", command=partial(
            self._guardar_modificacion, ventana, adopcion, entradas
        )).pack(pady=(0, 12))

    def _guardar_modificacion(self, ventana, adopcion, entradas: dict) -> None:
        try:
            dni, nombre, telefono, correo, max_adopciones, fecha = self._leer_datos(entradas)
            relacionadas = [a for a in self.refugio.adopciones if a.adoptante.dni.upper() == dni]
            if len(relacionadas) > max_adopciones:
                raise ValueError("El máximo de adopciones no puede ser inferior a las registradas.")
            # Compartimos los datos actualizados entre registros del mismo adoptante.
            for registro in relacionadas:
                registro.adoptante.nombre = nombre
                registro.adoptante.telefono = telefono
                registro.adoptante.correo = correo
                registro.adoptante.max_adopciones = max_adopciones
            adopcion.fecha = fecha
        except (ValueError, RefugioError) as e:
            self._mostrar_error(e)
            return
        ventana.destroy()
        self.refrescar()
        messagebox.showinfo("Éxito", "Adopción actualizada correctamente.")

    def _on_eliminar_click(self) -> None:
        adopcion = self._adopcion_seleccionada()
        if adopcion is None:
            return
        if not messagebox.askyesno(
            "Eliminar", f"¿Eliminar la adopción de {adopcion.animal.nombre} "
            f"por {adopcion.adoptante.nombre}?\n\n"
            "Esto borrará el registro y devolverá el animal a disponible."
        ):
            return
        self.refugio.adopciones.remove(adopcion)
        if not any(a.animal.id_chip == adopcion.animal.id_chip for a in self.refugio.adopciones):
            adopcion.animal.estado_adopcion = "disponible"
        self.refrescar()

    def _on_ver_detalles_click(self) -> None:
        adopcion = self._adopcion_seleccionada()
        if adopcion is None:
            return
        mensaje = (
            f"Animal: {adopcion.animal.nombre}\n"
            f"Especie: {adopcion.animal.especie}\n"
            f"Chip: {adopcion.animal.id_chip}\n"
            f"Estado: {adopcion.animal.estado_adopcion}\n\n"
            f"Adoptante: {adopcion.adoptante.nombre}\n"
            f"DNI: {adopcion.adoptante.dni}\n"
            f"Teléfono: {adopcion.adoptante.telefono}\n"
            f"Correo: {adopcion.adoptante.correo}\n"
            f"Máximo de adopciones: {adopcion.adoptante.max_adopciones}\n\n"
            f"Fecha de adopción: {adopcion.fecha.isoformat()}"
        )
        messagebox.showinfo("Detalles de la adopción", mensaje)

    def refrescar(self) -> None:
        filas = []
        for a in self._obtener_adopciones_filtradas():
            filas.append((
                a.animal.id_chip, a.animal.nombre, a.adoptante.dni,
                a.adoptante.nombre, a.adoptante.telefono,
                a.adoptante.correo, a.fecha.isoformat(),
            ))
        self.rellenar_tabla(self.tabla, filas)
