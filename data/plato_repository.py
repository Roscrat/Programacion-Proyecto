from data.repositorio_base import RepositorioBase
from domain.plato import Plato


class PlatoRepository(RepositorioBase):

    def agregar(self, plato: Plato) -> bool:
        ok = self._escribir(
            "INSERT INTO platos (nombre, precio, tipo) VALUES (?, ?, ?);",
            (plato.nombre, plato.precio, plato.tipo),
            "Ya existe un producto con ese nombre.",
        )
        if ok:
            plato.id = self.ultimo_id
        return ok

    def obtener_todos(self) -> list[Plato]:
        filas = self._leer("SELECT id, nombre, precio, tipo FROM platos ORDER BY id;")
        return [Plato.desde_tupla(f) for f in filas]

    def actualizar(self, plato: Plato) -> bool:
        return self._escribir(
            "UPDATE platos SET nombre = ?, precio = ?, tipo = ? WHERE id = ?;",
            (plato.nombre, plato.precio, plato.tipo, plato.id),
            "Ya existe un producto con ese nombre.",
        )

    def eliminar(self, id_registro: int) -> bool:
        return self._escribir(
            "DELETE FROM platos WHERE id = ?;",
            (id_registro,),
            "No se puede borrar: el producto ya aparece en algún pedido.",
        )
