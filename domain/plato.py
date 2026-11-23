from typing import Optional

from domain.validaciones import validar_texto

# Un "almuerzo" se personaliza en 3 pasos; una bebida o un otro se agrega directo
TIPOS_PLATO = {"almuerzo": "Almuerzo (se personaliza)", "bebida": "Bebida", "otro": "Otro"}


class Plato:
    """Un producto del menu con su precio de venta."""

    def __init__(
        self, nombre: str, precio: float, tipo: str = "otro", id_plato: Optional[int] = None
    ) -> None:
        if tipo not in TIPOS_PLATO:
            raise ValueError("El tipo debe ser almuerzo, bebida u otro.")
        self.id: Optional[int] = id_plato
        self.tipo: str = tipo
        self.__nombre: str = validar_texto(nombre, "El nombre del producto")
        self.__precio: float = 0.0
        self.precio = precio

    @property
    def nombre(self) -> str:
        return self.__nombre

    @property
    def precio(self) -> float:
        return self.__precio

    @precio.setter
    def precio(self, valor: float) -> None:
        if valor < 0:
            raise ValueError("El precio no puede ser negativo.")
        self.__precio = float(valor)

    @property
    def es_almuerzo(self) -> bool:
        return self.tipo == "almuerzo"

    @classmethod
    def desde_tupla(cls, registro: tuple) -> "Plato":
        """Espera (id, nombre, precio, tipo)."""
        return cls(id_plato=registro[0], nombre=registro[1], precio=registro[2], tipo=registro[3])

    def __str__(self) -> str:
        return f"{self.nombre} (${self.precio:,.0f})"

    def __repr__(self) -> str:
        return f"Plato(id={self.id}, nombre='{self.nombre}', precio={self.precio}, tipo='{self.tipo}')"

    def __eq__(self, otro: object) -> bool:
        if not isinstance(otro, Plato):
            return NotImplemented
        return self.nombre.lower() == otro.nombre.lower()
