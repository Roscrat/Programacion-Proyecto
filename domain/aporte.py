from typing import Optional

from domain.validaciones import validar_fecha, validar_texto


class Aporte:
    """Dinero que se pone en el restaurante (capital inicial, plata propia, prestamos)."""

    def __init__(
        self, descripcion: str, monto: float, fecha: str, id_aporte: Optional[int] = None
    ) -> None:
        self.id: Optional[int] = id_aporte
        self.__descripcion: str = validar_texto(descripcion, "La descripcion")
        self.__fecha: str = validar_fecha(fecha)
        if monto <= 0:
            raise ValueError("El aporte debe ser mayor que cero.")
        self.__monto: float = float(monto)

    @property
    def descripcion(self) -> str:
        return self.__descripcion

    @property
    def fecha(self) -> str:
        return self.__fecha

    @property
    def monto(self) -> float:
        return self.__monto

    @classmethod
    def desde_tupla(cls, registro: tuple) -> "Aporte":
        return cls(id_aporte=registro[0], descripcion=registro[1], monto=registro[2], fecha=registro[3])

    def __str__(self) -> str:
        return f"{self.fecha} - {self.descripcion}: ${self.monto:,.0f}"

    def __repr__(self) -> str:
        return f"Aporte(id={self.id}, descripcion='{self.descripcion}', monto={self.monto})"
