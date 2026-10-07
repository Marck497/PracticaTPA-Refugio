from src.refugio.modelo.adoptante import Adoptante
from src.refugio.modelo.persona import Persona
from src.refugio.modelo.voluntario import Voluntario

# 1) La clase abstracta no se puede instanciar
try:
    Persona("00000000X", "Nadie", "600000000")
except TypeError as e:
    print("TypeError:", e)

# 2) Dos subclases concretas, cada una implementa descripcion() a su manera
personas: list[Persona] = [
    Voluntario("12345678A", "Ana Perez", "600111222", "Perros", max_animales=5),
    Adoptante("87654321B", "Carlos Ruiz", "611222333", "carlos@example.com", max_adopciones=2),
]
for p in personas:
    print(p.descripcion())   # cada objeto despacha a su propia version

# 3) La comparacion por DNI (heredada de Persona) sigue funcionando
print(personas[0] == Voluntario("12345678A", "Otro nombre", "0", "Gatos"))   # True
print(personas[0] == personas[1])                                            # False