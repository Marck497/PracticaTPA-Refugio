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

    def to_dict(self) -> dict:
        return {
            "fecha": self.fecha.isoformat(),
            "motivo": self.motivo,
            "diagnostico": self.diagnostico,
            "tratamiento": self.tratamiento,
        }

    @classmethod
    def from_dict(cls, datos: dict) -> "RevisionVeterinaria":
        return cls(
            fecha=date.fromisoformat(datos["fecha"]),
            motivo=datos["motivo"],
            diagnostico=datos["diagnostico"],
            tratamiento=datos["tratamiento"],
        )

    def __repr__(self):
        return (
            f"RevisionVeterinaria(fecha={self.fecha}, motivo={self.motivo}, "
            f"diagnostico={self.diagnostico}, tratamiento={self.tratamiento})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RevisionVeterinaria):
            return NotImplemented
        return self.to_dict() == other.to_dict()
