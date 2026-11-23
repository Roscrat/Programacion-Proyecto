from typing import Optional

from domain.validaciones import validar_texto

ESTADOS_MESA = ("libre", "ocupada")


class Mesa:
    """Una mesa del restaurante. Esta libre o esta ocupada."""

    def __init__(
        self,
        nombre: str,
        zona: str = "Salón Principal",
        estado: str = "libre",
        id_mesa: Optional[int] = None,
    ) -> None:
        if estado not in ESTADOS_MESA:
            raise ValueError("El estado de la mesa debe ser libre u ocupada.")
        self.id: Optional[int] = id_mesa
        self.estado: str = estado
        self.__nombre: str = validar_texto(nombre, "El nombre de la mesa")
        self.__zona: str = validar_texto(zona, "La zona")

    @property
    def nombre(self) -> str:
        return self.__nombre

    @property
    def zona(self) -> str:
        return self.__zona

    @property
    def ocupada(self) -> bool:
        return self.estado == "ocupada"

    @classmethod
    def desde_tupla(cls, registro: tuple) -> "Mesa":
        """Espera (id, nombre, zona, estado)."""
        return cls(id_mesa=registro[0], nombre=registro[1], zona=registro[2], estado=registro[3])

    def __str__(self) -> str:
        return f"{self.nombre} ({self.zona}) - {self.estado}"

    def __repr__(self) -> str:
        return f"Mesa(id={self.id}, nombre='{self.nombre}', estado='{self.estado}')"

    def __eq__(self, otro: object) -> bool:
        if not isinstance(otro, Mesa):
            return NotImplemented
        return self.id is not None and self.id == otro.id
