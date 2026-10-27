"""Lanza la interfaz con datos de demostración: python -m refugio.ui"""

from ..demo import construir_refugio_demo
from .app import App

def main() -> None:
    App(construir_refugio_demo()).mainloop()

if __name__ == "__main__":
    main()