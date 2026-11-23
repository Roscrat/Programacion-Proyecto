from typing import Optional

from domain.validaciones import validar_texto

# Los tres pasos de la personalizacion del almuerzo
PASOS = {"proteina": "Proteína", "principio": "Principio", "complemento": "Complementos"}


class OpcionAlmuerzo:
    """Una opcion que se puede elegir al personalizar el almuerzo (por ejemplo Res o Sopa)."""

    def __init__(self, paso: str, nombre: str, id_opcion: Optional[int] = None) -> None:
        if paso not in PASOS:
            raise ValueError("El paso debe ser proteina, principio o complemento.")
        self.id: Optional[int] = id_opcion
        self.__paso: str = paso
        self.__nombre: str = validar_texto(nombre, "El nombre de la opcion")

    @property
    def paso(self) -> str:
        return self.__paso

    @property
    def nombre(self) -> str:
        return self.__nombre

    @classmethod
    def desde_tupla(cls, registro: tuple) -> "OpcionAlmuerzo":
        """Espera (id, paso, nombre)."""
        return cls(id_opcion=registro[0], paso=registro[1], nombre=registro[2])

    def __str__(self) -> str:
        return f"{PASOS[self.paso]}: {self.nombre}"

    def __repr__(self) -> str:
        return f"OpcionAlmuerzo(id={self.id}, paso='{self.paso}', nombre='{self.nombre}')"
