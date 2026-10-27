"""Vistas de la interfaz. Para añadir una: crear su archivo y registrarla aquí y en App.VISTAS"""

from .vista_adopciones import VistaAdopciones
from .vista_animales import VistaAnimales
from .vista_voluntarios import VistaVoluntarios
from .base import Vista

__all__ = ["Vista", "VistaAdopciones", "VistaAnimales", "VistaVoluntarios"]