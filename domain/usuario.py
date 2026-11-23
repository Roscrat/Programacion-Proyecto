import hashlib
import secrets
from typing import Optional

from domain.validaciones import validar_texto

ROLES = {"admin": "Admin", "cajero": "Cajero"}


def crear_hash(clave: str, sal: Optional[str] = None) -> str:
    """Convierte la contrasena en un texto que no se puede leer.
    La sal es un texto al azar que hace que dos claves iguales den resultados distintos."""
    sal = sal or secrets.token_hex(8)
    resumen = hashlib.sha256((sal + clave).encode("utf-8")).hexdigest()
    return f"{sal}${resumen}"


class Usuario:
    """Persona que puede entrar al sistema, con un rol (admin o cajero)."""

    def __init__(
        self, usuario: str, clave_hash: str, rol: str, id_usuario: Optional[int] = None
    ) -> None:
        if rol not in ROLES:
            raise ValueError("El rol debe ser admin o cajero.")
        self.id: Optional[int] = id_usuario
        self.__usuario: str = validar_texto(usuario, "El usuario")
        self.__clave_hash: str = clave_hash
        self.__rol: str = rol

    @property
    def usuario(self) -> str:
        return self.__usuario

    @property
    def clave_hash(self) -> str:
        return self.__clave_hash

    @property
    def rol(self) -> str:
        return self.__rol

    @property
    def es_admin(self) -> bool:
        return self.__rol == "admin"

    @classmethod
    def nuevo(cls, usuario: str, clave: str, rol: str) -> "Usuario":
        """Crea un usuario a partir de la clave escrita por la persona."""
        if len(clave) < 4:
            raise ValueError("La contraseña debe tener al menos 4 caracteres.")
        return cls(usuario, crear_hash(clave), rol)

    @classmethod
    def desde_tupla(cls, registro: tuple) -> "Usuario":
        """Espera (id, usuario, clave, rol)."""
        return cls(
            id_usuario=registro[0], usuario=registro[1], clave_hash=registro[2], rol=registro[3]
        )

    def clave_correcta(self, clave: str) -> bool:
        sal = self.__clave_hash.split("$")[0]
        return secrets.compare_digest(crear_hash(clave, sal), self.__clave_hash)

    def __str__(self) -> str:
        return f"{self.usuario} ({ROLES[self.rol]})"

    def __repr__(self) -> str:
        return f"Usuario(id={self.id}, usuario='{self.usuario}', rol='{self.rol}')"
