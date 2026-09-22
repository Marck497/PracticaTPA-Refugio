from datetime import date

class RevisionVeterinaria:
    """
    Un evento veterinario puntual dentro del historial 
    de un Animal.
    """

    def __init__(self, fecha: date, motivo: str, diagnostico: str, tratamiento: str):
        self.fecha = fecha
        self.motivo = motivo
        self.diagnostico = diagnostico
        self.tratamiento = tratamiento

    def __repr__(self):
        return(
            f"(RevisionVeterinaria(fecha={self.fecha}, motivo={self.motivo}, )"
            f"diagnóstico={self.diagnostico}, tratamiento={self.tratamiento})"
        )