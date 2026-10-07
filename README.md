# Refugio — Sistema de gestión de un refugio de animales

Proyecto de *Técnicas de Programación Avanzada*. Es un **paquete Python sin interfaz**: contiene el modelo (animales, voluntarios, adoptantes, adopciones, revisiones) y la lógica del refugio.

## Requisitos

- Python 3.10 o superior.
- La biblioteca `regex` (solo la usan las pruebas de validación):

```powershell
python -m pip install -r requirements.txt
```

## Cómo ejecutar

**Todos los comandos se lanzan desde la carpeta `src/`**:

```powershell
cd src
```

### La demo

```powershell
python -m refugio
```

Construye un refugio con 8 animales, asigna un voluntario, registra una revisión y una adopción, e imprime la ficha de un animal y el informe de actividad. Al final demuestra las validaciones de `id_chip` y `capacidad_maxima`.

### Las pruebas

Cada prueba es un script que imprime su resultado. Se ejecutan como módulos (con puntos y **sin** `.py`):

| Comando | Qué comprueba |
| --- | --- |
| `python -m pruebas.prueba_practica2_apartado1` | La clase abstracta `Persona` no se puede instanciar (`TypeError`); `Voluntario` y `Adoptante` implementan `descripcion()` a su manera; la igualdad por DNI |
| `python -m pruebas.prueba_practica2_apartado2` | El protocolo `Resumible`: `RevisionVeterinaria` y `Adopcion` lo cumplen sin heredar de una base común |

### Usarlo como módulo (p. ej. desde una UI)

```python
from refugio import Refugio, Animal, Adoptante

refugio = Refugio("Refugio Esperanza", capacidad_maxima=10)
refugio.registrar_ingreso(Animal("CHIP001", "Rex", "Perro", 22.5, "Macho", (2021, 3, 12)))
refugio.tramitar_adopcion("CHIP001", Adoptante("87654321B", "Carlos", "611222333", "c@example.com"))
print(refugio.informe_actividad())
```

`Refugio` (en `gestor.py`) es el **gestor**: la puerta de entrada para operar sobre el modelo. Todo lo que necesita una UI se importa de `refugio` (ver `__init__.py`).

## Estructura del repositorio

```
requirements.txt
src/
├── refugio/                  ← el paquete (el código de la aplicación)
│   ├── __init__.py           API pública del paquete
│   ├── __main__.py           punto de entrada: python -m refugio
│   ├── demo.py               script de demostración
│   ├── gestor.py             Refugio: coordina animales, voluntarios y adopciones
│   ├── excepciones.py        errores propios del dominio
│   ├── protocolos.py         Resumible (typing.Protocol)
│   ├── repositorio.py        Repositorio[T], estructura genérica
│   ├── persistencia.py       guardar/cargar el refugio en JSON
│   ├── validacion.py         patrón del chip y excepciones de validación
│   └── modelo/               las entidades del dominio
│       ├── __init__.py
│       ├── persona.py        clase abstracta (ABC)
│       ├── voluntario.py     hereda de Persona
│       ├── adoptante.py      hereda de Persona
│       ├── animal.py
│       ├── adopcion.py
│       └── revision_veterinaria.py
└── pruebas/                  ← scripts de prueba (no forman parte del paquete)
```

**Por qué esta estructura:**

- **`src/`** separa el código de la aplicación de todo lo demás, y deja claro qué se importa.
- **`refugio/` es un paquete** porque la UI futura necesita importar el código (`from refugio import ...`), no ejecutar scripts sueltos.
- **`modelo/`** agrupa las entidades; `gestor.py`, `persistencia.py`, `repositorio.py`… son la lógica que opera sobre ellas. Así el dominio queda separado de lo que lo usa.
- **`excepciones.py`** centraliza los errores propios y los hace derivar de una base común, `RefugioError`, para poder capturarlos todos con un único `except`.
- **`pruebas/`** está fuera del paquete: son scripts que *usan* el paquete, no parte de él.

## Cómo funcionan los imports

### Imports relativos (`from .x import ...`)

Dentro del paquete, los módulos se importan entre sí con un **punto** delante:

```python
# en refugio/modelo/animal.py
from .revision_veterinaria import RevisionVeterinaria   # "del mismo paquete"
```

- `.` significa «este mismo paquete»; `..` sería el paquete padre.
- Así el paquete no depende de cómo se llame ni de desde dónde se ejecute: solo de sus propios módulos.
- Un import sin punto (`from animal import Animal`) buscaría `animal` en la ruta global de Python y fallaría.

Consecuencia: **un archivo del paquete no se puede ejecutar directamente** (`python refugio/demo.py` da `ImportError: attempted relative import with no known parent package`). Se ejecuta como módulo, con `python -m`.

### Qué es un `__init__.py`

Un `__init__.py` convierte una carpeta en **paquete** y se ejecuta al importarla. Aquí tiene dos usos:

- **`refugio/modelo/__init__.py`** reexporta las entidades, para poder escribir `from .modelo import Animal` en vez de `from .modelo.animal import Animal`.
- **`refugio/__init__.py`** define la **API pública**: importa del resto de módulos lo que debe usar el exterior y lo lista en `__all__`. Por eso desde fuera basta con `from refugio import Refugio, Animal, ...`, sin conocer la estructura interna.

`pruebas/` **no tiene** `__init__.py`: Python 3 permite carpetas sin él (*paquetes de espacio de nombres*), lo que basta para ejecutarla con `python -m pruebas.nombre`.

### Qué es `__all__`

`__all__` es una lista de nombres (como cadenas) que declara **qué es público** en un módulo o paquete:

```python
# refugio/__init__.py
__all__ = ["Refugio", "Animal", "Adoptante", ...]
```

- **Controla `from refugio import *`:** importa solo los nombres de esa lista. Sin `__all__`, importaría todo lo que no empiece por `_`, incluidos nombres internos como los submódulos.
- **Documenta la API:** quien lea el archivo ve de un vistazo qué puede usar desde fuera y qué es interno.
- **No es una barrera:** `from refugio.gestor import Refugio` sigue funcionando aunque `gestor` no esté en la lista. Es una convención, no una restricción.
- **Hay que mantenerla:** al añadir una clase pública nueva (por ejemplo, otra entidad), se importa en `__init__.py` y se añade a `__all__`.

## `__main__.py` y por qué `python -m`

`python -m refugio` ejecuta el archivo `refugio/__main__.py`, que solo llama a `main()` de `demo.py`. Hace falta por dos motivos:

- **Es el punto de entrada del paquete.** Sin él, `python -m refugio` no sabría qué ejecutar.
- **Con `-m`, Python añade la carpeta actual (`src/`) a su ruta de búsqueda**, y desde ahí encuentra `refugio`. Al lanzar un archivo suelto, en cambio, Python solo busca en la carpeta donde está ese archivo.

Errores típicos:

| Error | Causa |
| --- | --- |
| `No module named refugio` | Estás en otra carpeta; haz `cd src` |
| `No module named pruebas` | Igual: no estás en `src/`, o has escrito `.py` al final |
| `attempted relative import with no known parent package` | Has lanzado un archivo del paquete directamente; usa `python -m` |

## Decisiones de diseño

- **`Persona` (ABC)** agrupa lo común de `Voluntario` y `Adoptante` (DNI, nombre, teléfono, igualdad por DNI). Es una relación «es-un»; `Animal` no hereda porque un animal no es una persona.
- **`Resumible` (Protocol)** define un rol por estructura: cualquier clase con un método `resumen()` lo cumple sin heredar de nada. Es lo que permite que `Adopcion` y `RevisionVeterinaria`, sin relación entre sí, se traten igual.
- **`Repositorio[T]`** es genérico (`TypeVar` + `Generic`): la misma clase sirve para animales, voluntarios, etc.
- **Persistencia en JSON:** cada clase tiene `to_dict()`/`from_dict()`. Las referencias entre objetos se guardan por clave (el chip del animal, el DNI del voluntario) y se re-enlazan al cargar.
- **Validación:** el `id_chip` tiene formato `CHIP` + 3 dígitos, comprobado con un patrón `re` compilado una sola vez; los registros inválidos se rechazan con excepciones propias sin perder los válidos.
- **Validación:** el `id_chip` tiene formato `CHIP` + 3 dígitos, comprobado con un patrón `re` compilado una sola vez; los registros inválidos se rechazan con excepciones propias sin perder los válidos.
