from data.repositorio_base import RepositorioBase
from domain.opcion import OpcionAlmuerzo


class OpcionRepository(RepositorioBase):

    def agregar(self, opcion: OpcionAlmuerzo) -> bool:
        ok = self._escribir(
            "INSERT INTO opciones_almuerzo (paso, nombre) VALUES (?, ?);",
            (opcion.paso, opcion.nombre),
            "Esa opción ya existe en ese paso.",
        )
        if ok:
            opcion.id = self.ultimo_id
        return ok

    def obtener_todos(self) -> list[OpcionAlmuerzo]:
        filas = self._leer("SELECT id, paso, nombre FROM opciones_almuerzo ORDER BY paso, id;")
        return [OpcionAlmuerzo.desde_tupla(f) for f in filas]

    def obtener_por_paso(self, paso: str) -> list[OpcionAlmuerzo]:
        filas = self._leer(
            "SELECT id, paso, nombre FROM opciones_almuerzo WHERE paso = ? ORDER BY id;", (paso,)
        )
        return [OpcionAlmuerzo.desde_tupla(f) for f in filas]

    def eliminar(self, id_registro: int) -> bool:
        return self._escribir("DELETE FROM opciones_almuerzo WHERE id = ?;", (id_registro,))
