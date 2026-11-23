from typing import Optional

from domain.validaciones import validar_fecha, validar_texto


class Gasto:
    """Dinero que sale del restaurante: mercado, gas, servicios, etc."""

    def __init__(
        self,
        descripcion: str,
        monto: float,
        fecha: str,
        id_categoria: int,
        nombre_categoria: str = "",
        id_gasto: Optional[int] = None,
    ) -> None:
        self.id: Optional[int] = id_gasto
        self.id_categoria: int = id_categoria
        self.nombre_categoria: str = nombre_categoria
        self.__descripcion: str = validar_texto(descripcion, "La descripcion")
        self.__fecha: str = validar_fecha(fecha)
        self.__monto: float = 0.0
        self.monto = monto

    @property
    def descripcion(self) -> str:
        return self.__descripcion

    @property
    def fecha(self) -> str:
        return self.__fecha

    @property
    def monto(self) -> float:
        return self.__monto

    @monto.setter
    def monto(self, valor: float) -> None:
        if valor < 0:
            raise ValueError("El monto no puede ser negativo.")
        self.__monto = float(valor)

    @classmethod
    def desde_tupla(cls, registro: tuple) -> "Gasto":
        """Espera (id, descripcion, monto, fecha, id_categoria, nombre_categoria)."""
        return cls(
            id_gasto=registro[0],
            descripcion=registro[1],
            monto=registro[2],
            fecha=registro[3],
            id_categoria=registro[4],
            nombre_categoria=registro[5],
        )

    def __str__(self) -> str:
        return f"{self.fecha} - {self.descripcion}: ${self.monto:,.0f}"

    def __repr__(self) -> str:
        return (
            f"Gasto(id={self.id}, descripcion='{self.descripcion}', "
            f"monto={self.monto}, fecha='{self.fecha}')"
        )

    def __eq__(self, otro: object) -> bool:
        if not isinstance(otro, Gasto):
            return NotImplemented
        return self.id is not None and self.id == otro.id
