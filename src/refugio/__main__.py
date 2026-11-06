"""Permite ejecutar la demostración con 'python -m refugio'"""

from .demo import main
from .registro import configurar_logging

if __name__ == "__main__":
    configurar_logging()
    main()