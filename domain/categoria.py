from typing import Optional

from domain.validaciones import validar_texto


class Categoria:

    def __init__(self, nombre: str, id_categoria: Optional[int] = None) -> None:
        self.id: Optional[int] = id_categoria
        self.__nombre: str = validar_texto(nombre, "El nombre de la categoria")

    @property
    def nombre(self) -> str:
        return self.__nombre

    @classmethod
    def desde_tupla(cls, registro: tuple) -> "Categoria":
        return cls(id_categoria=registro[0], nombre=registro[1])

    def __str__(self) -> str:
        return self.__nombre

    def __repr__(self) -> str:
        return f"Categoria(id={self.id}, nombre='{self.__nombre}')"
