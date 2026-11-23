import secrets
from typing import Optional

from data.repositorio_base import RepositorioBase
from domain.usuario import Usuario


class UsuarioRepository(RepositorioBase):

    def agregar(self, usuario: Usuario) -> bool:
        ok = self._escribir(
            "INSERT INTO usuarios (usuario, clave, rol) VALUES (?, ?, ?);",
            (usuario.usuario, usuario.clave_hash, usuario.rol),
            "Ya existe un usuario con ese nombre.",
        )
        if ok:
            usuario.id = self.ultimo_id
        return ok

    def obtener_todos(self) -> list[Usuario]:
        filas = self._leer("SELECT id, usuario, clave, rol FROM usuarios ORDER BY usuario;")
        return [Usuario.desde_tupla(f) for f in filas]

    def obtener_por_nombre(self, nombre: str) -> Optional[Usuario]:
        filas = self._leer(
            "SELECT id, usuario, clave, rol FROM usuarios WHERE usuario = ?;", (nombre,)
        )
        return Usuario.desde_tupla(filas[0]) if filas else None

    def autenticar(self, nombre: str, clave: str, rol: str) -> Optional[Usuario]:
        """Devuelve el usuario si el nombre, la clave y el rol coinciden. Si no, None."""
        usuario = self.obtener_por_nombre(nombre.strip())
        if usuario and usuario.rol == rol and usuario.clave_correcta(clave):
            return usuario
        return None

    def eliminar(self, id_registro: int) -> bool:
        return self._escribir(
            "DELETE FROM usuarios WHERE id = ?;",
            (id_registro,),
            "No se puede borrar: el usuario ya tomó pedidos.",
        )

    def obtener_general(self) -> Usuario:
        """Devuelve el usuario interno que firma todos los pedidos (se crea si no existe).
        La app ya no pide login; este registro solo existe porque cada pedido guarda quien lo tomo."""
        usuario = self.obtener_por_nombre("general")
        if usuario is None:
            usuario = Usuario.nuevo("general", secrets.token_hex(8), "admin")
            self.agregar(usuario)
        return usuario
