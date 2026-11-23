import sqlite3
from typing import Optional

from data.repositorio_base import RepositorioBase
from domain.pedido import DetallePedido, Pedido

# Columnas que se piden siempre que se lee un pedido (el orden debe coincidir
# con Pedido.desde_tupla)
SELECT_PEDIDO = (
    "SELECT p.id, p.fecha, p.id_mesa, m.nombre, p.cliente, p.observaciones, "
    "p.estado, p.metodo_pago, p.id_usuario "
    "FROM pedidos p JOIN mesas m ON m.id = p.id_mesa "
)


class PedidoRepository(RepositorioBase):

    def agregar(self, pedido: Pedido) -> bool:
        return self.guardar(pedido)

    def guardar(self, pedido: Pedido) -> bool:
        """Guarda un pedido abierto con sus lineas, en una sola transaccion.
        Si el pedido es nuevo lo inserta; si ya existe, reemplaza sus lineas.
        Ademas deja la mesa como ocupada."""
        self.ultimo_error = ""
        if len(pedido) == 0:
            self.ultimo_error = "El pedido no tiene productos."
            return False
        era_nuevo = pedido.id is None
        try:
            with self.db as cursor:
                if era_nuevo:
                    cursor.execute(
                        "INSERT INTO pedidos (fecha, id_mesa, id_usuario, cliente, observaciones) "
                        "VALUES (?, ?, ?, ?, ?);",
                        (pedido.fecha, pedido.id_mesa, pedido.id_usuario,
                         pedido.cliente, pedido.observaciones),
                    )
                    pedido.id = cursor.lastrowid
                else:
                    cursor.execute(
                        "UPDATE pedidos SET cliente = ?, observaciones = ? WHERE id = ?;",
                        (pedido.cliente, pedido.observaciones, pedido.id),
                    )
                    cursor.execute("DELETE FROM detalles_pedido WHERE id_pedido = ?;", (pedido.id,))
                cursor.executemany(
                    "INSERT INTO detalles_pedido "
                    "(id_pedido, id_plato, cantidad, precio_unitario, notas) VALUES (?, ?, ?, ?, ?);",
                    [(pedido.id, d.id_plato, d.cantidad, d.precio_unitario, d.notas)
                     for d in pedido.detalles],
                )
                cursor.execute("UPDATE mesas SET estado = 'ocupada' WHERE id = ?;", (pedido.id_mesa,))
            return True
        except sqlite3.IntegrityError:
            if era_nuevo:
                pedido.id = None
            self.ultimo_error = "La mesa, el usuario o algún producto del pedido ya no existe."
            return False
        except sqlite3.Error as err:
            if era_nuevo:
                pedido.id = None
            self.ultimo_error = f"Error de base de datos: {err}"
            return False

    def _cargar_detalles(self, pedido: Pedido) -> Pedido:
        filas = self._leer(
            "SELECT d.id_plato, pl.nombre, d.cantidad, d.precio_unitario, d.notas "
            "FROM detalles_pedido d JOIN platos pl ON pl.id = d.id_plato "
            "WHERE d.id_pedido = ? ORDER BY d.id;",
            (pedido.id,),
        )
        for fila in filas:
            pedido.agregar_detalle(DetallePedido.desde_tupla(fila))
        return pedido

    def obtener_todos(self) -> list[Pedido]:
        filas = self._leer(SELECT_PEDIDO + "ORDER BY p.fecha DESC, p.id DESC;")
        return [self._cargar_detalles(Pedido.desde_tupla(f)) for f in filas]

    def obtener_abierto_de_mesa(self, id_mesa: int) -> Optional[Pedido]:
        filas = self._leer(
            SELECT_PEDIDO + "WHERE p.id_mesa = ? AND p.estado = 'abierto' ORDER BY p.id DESC LIMIT 1;",
            (id_mesa,),
        )
        return self._cargar_detalles(Pedido.desde_tupla(filas[0])) if filas else None

    def cobrar(self, id_pedido: int, metodo_pago: str, cliente: str = "") -> bool:
        """Marca el pedido como pagado y libera la mesa, las dos cosas o ninguna."""
        self.ultimo_error = ""
        try:
            with self.db as cursor:
                cursor.execute(
                    "UPDATE pedidos SET estado = 'pagado', metodo_pago = ?, cliente = ? "
                    "WHERE id = ? AND estado = 'abierto';",
                    (metodo_pago, cliente, id_pedido),
                )
                if cursor.rowcount == 0:
                    self.ultimo_error = "El pedido no existe o ya fue cobrado."
                    return False
                cursor.execute(
                    "UPDATE mesas SET estado = 'libre' "
                    "WHERE id = (SELECT id_mesa FROM pedidos WHERE id = ?);",
                    (id_pedido,),
                )
            return True
        except sqlite3.Error as err:
            self.ultimo_error = f"Error de base de datos: {err}"
            return False

    def eliminar(self, id_registro: int) -> bool:
        """Borra el pedido (sus lineas se borran solas por ON DELETE CASCADE).
        Si estaba abierto, la mesa queda libre."""
        self.ultimo_error = ""
        try:
            with self.db as cursor:
                cursor.execute("SELECT id_mesa, estado FROM pedidos WHERE id = ?;", (id_registro,))
                fila = cursor.fetchone()
                if fila is None:
                    self.ultimo_error = "No se encontró el pedido."
                    return False
                cursor.execute("DELETE FROM pedidos WHERE id = ?;", (id_registro,))
                if fila[1] == "abierto":
                    cursor.execute("UPDATE mesas SET estado = 'libre' WHERE id = ?;", (fila[0],))
            return True
        except sqlite3.Error as err:
            self.ultimo_error = f"Error de base de datos: {err}"
            return False

    def total_cobrado(self) -> float:
        return self._escalar(
            "SELECT COALESCE(SUM(d.cantidad * d.precio_unitario), 0) "
            "FROM detalles_pedido d JOIN pedidos p ON p.id = d.id_pedido "
            "WHERE p.estado = 'pagado';"
        )

    def total_por_cobrar(self) -> float:
        return self._escalar(
            "SELECT COALESCE(SUM(d.cantidad * d.precio_unitario), 0) "
            "FROM detalles_pedido d JOIN pedidos p ON p.id = d.id_pedido "
            "WHERE p.estado = 'abierto';"
        )
