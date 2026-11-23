import flet as ft

from domain.pedido import Pedido
from ui import tema
from ui.components.utilidades import (
    confirmar,
    con_scroll,
    encabezados,
    moneda,
    mostrar_mensaje,
)
from ui.contexto import Contexto


class PanelPedidos:
    """Historial de todos los pedidos: los abiertos (por cobrar) y los ya pagados."""

    def __init__(self, ctx: Contexto) -> None:
        self.ctx = ctx
        self.page = ctx.page
        self.mensaje = ft.Text("")
        self.tabla = ft.DataTable(
            columns=encabezados("N", "Fecha", "Día", "Mesa", "Detalle", "Total", "Estado", "Pago", ""),
            rows=[],
        )
        self.contenido = ft.Column(
            [
                tema.titulo("Pedidos"),
                ft.Text("Historial de pedidos. Para cobrar uno abierto, entra a Mesas.", color=tema.GRIS),
                self.mensaje,
                con_scroll(self.tabla),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    def refrescar(self) -> None:
        self.tabla.rows = []
        for pedido in self.ctx.pedidos.obtener_todos():
            if pedido.pagado:
                estado = tema.etiqueta_estado("Pagado", tema.VERDE_CLARO, tema.VERDE)
            else:
                estado = tema.etiqueta_estado("Por cobrar", tema.ROJO_CLARO, tema.ROJO)
            detalle = ", ".join(str(d) for d in pedido.detalles)

            accion = ft.IconButton(icon=ft.Icons.DELETE, tooltip="Eliminar",
                                   on_click=lambda e, p=pedido: self.pedir_eliminar(p))

            self.tabla.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(pedido.id))),
                        ft.DataCell(ft.Text(pedido.fecha)),
                        ft.DataCell(ft.Text(pedido.dia_semana)),
                        ft.DataCell(ft.Text(pedido.nombre_mesa)),
                        ft.DataCell(ft.Container(content=ft.Text(detalle, size=12), width=300)),
                        ft.DataCell(ft.Text(moneda(pedido.total))),
                        ft.DataCell(estado),
                        ft.DataCell(ft.Text(pedido.metodo_pago or "-")),
                        ft.DataCell(accion),
                    ]
                )
            )
        self.page.update()

    def pedir_eliminar(self, pedido: Pedido) -> None:
        confirmar(self.page, f"Se eliminará el pedido {pedido.id} de {pedido.nombre_mesa}.",
                  lambda: self.eliminar(pedido))

    def eliminar(self, pedido: Pedido) -> None:
        if self.ctx.pedidos.eliminar(pedido.id):
            mostrar_mensaje(self.mensaje, "Pedido eliminado.")
        else:
            mostrar_mensaje(self.mensaje, self.ctx.pedidos.ultimo_error, error=True)
        self.refrescar()
