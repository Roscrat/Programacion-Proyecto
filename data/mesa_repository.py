from typing import Optional

from data.repositorio_base import RepositorioBase
from domain.mesa import Mesa


class MesaRepository(RepositorioBase):

    def agregar(self, mesa: Mesa) -> bool:
        ok = self._escribir(
            "INSERT INTO mesas (nombre, zona, estado) VALUES (?, ?, ?);",
            (mesa.nombre, mesa.zona, mesa.estado),
            "Ya existe una mesa con ese nombre.",
        )
        if ok:
            mesa.id = self.ultimo_id
        return ok

    def obtener_todos(self) -> list[Mesa]:
        filas = self._leer("SELECT id, nombre, zona, estado FROM mesas ORDER BY id;")
        return [Mesa.desde_tupla(f) for f in filas]

    def obtener_por_id(self, id_mesa: int) -> Optional[Mesa]:
        filas = self._leer("SELECT id, nombre, zona, estado FROM mesas WHERE id = ?;", (id_mesa,))
        return Mesa.desde_tupla(filas[0]) if filas else None

    def eliminar(self, id_registro: int) -> bool:
        return self._escribir(
            "DELETE FROM mesas WHERE id = ?;",
            (id_registro,),
            "No se puede borrar: la mesa tiene pedidos registrados.",
        )
