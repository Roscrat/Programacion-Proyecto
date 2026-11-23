from datetime import date

import flet as ft

from ui import tema

from data.aporte_dao import AporteDAO
from data.gasto_dao import GastoDAO
from data.pedido_repository import PedidoRepository
from domain.aporte import Aporte
from domain.resumen import ResumenCaja
from domain.validaciones import leer_numero
from ui.components.utilidades import (
    confirmar,
    con_scroll,
    encabezados,
    moneda,
    mostrar_mensaje,
)


class PanelResumen:
    def __init__(self, page: ft.Page, aporte_dao: AporteDAO, gasto_dao: GastoDAO, pedido_repo: PedidoRepository) -> None:
        self.page = page
        self.aporte_dao = aporte_dao
        self.gasto_dao = gasto_dao
        self.pedido_repo = pedido_repo

        self.lbl_saldo = ft.Text("", size=30, weight=ft.FontWeight.BOLD)
        self.lbl_aportes = ft.Text("", size=18, weight=ft.FontWeight.BOLD)
        self.lbl_cobrado = ft.Text("", size=18, weight=ft.FontWeight.BOLD)
        self.lbl_gastos = ft.Text("", size=18, weight=ft.FontWeight.BOLD)
        self.lbl_por_cobrar = ft.Text("", size=18, weight=ft.FontWeight.BOLD)

        self.txt_descripcion = tema.campo(label="Descripcion del aporte", width=320)
        self.txt_monto = tema.campo(label="Monto", width=160)
        self.txt_fecha = tema.campo(label="Fecha (AAAA-MM-DD)", width=190, value=date.today().isoformat())
        self.btn_aporte = tema.boton("Registrar aporte", self.agregar_aporte)
        self.mensaje = ft.Text("")
        self.tabla_aportes = ft.DataTable(columns=encabezados("Fecha", "Descripcion", "Monto", ""), rows=[])
        self.tabla_categorias = ft.DataTable(columns=encabezados("Categoria", "Total gastado"), rows=[])

        self.contenido = ft.Column(
            [
                ft.Text("Resumen del dinero", size=22, weight=ft.FontWeight.BOLD),
                self._tarjeta("Plata disponible", self.lbl_saldo, ft.Colors.GREEN_50, 320),
                ft.Row(
                    [
                        self._tarjeta("Aportes", self.lbl_aportes, ft.Colors.BLUE_50),
                        self._tarjeta("Cobrado en pedidos", self.lbl_cobrado, ft.Colors.BLUE_50),
                        self._tarjeta("Gastos", self.lbl_gastos, ft.Colors.RED_50),
                        self._tarjeta("Por cobrar", self.lbl_por_cobrar, ft.Colors.AMBER_50),
                    ],
                    wrap=True,
                ),
                ft.Divider(),
                ft.Text("Plata que se pone en el restaurante", size=18, weight=ft.FontWeight.BOLD),
                ft.Row([self.txt_descripcion, self.txt_monto, self.txt_fecha], wrap=True),
                self.btn_aporte,
                self.mensaje,
                con_scroll(self.tabla_aportes),
                ft.Divider(),
                ft.Text("Gastos por categoria", size=18, weight=ft.FontWeight.BOLD),
                con_scroll(self.tabla_categorias),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    @staticmethod
    def _tarjeta(titulo: str, valor: ft.Text, color: str, ancho: int = 220) -> ft.Container:
        return ft.Container(
            content=ft.Column([ft.Text(titulo, size=13, color=ft.Colors.BLACK87), valor], spacing=4),
            bgcolor=color,
            padding=15,
            border_radius=8,
            width=ancho,
        )

    def cargar(self) -> None:
        """Recalcula los datos sin llamar a page.update, lo hace quien invoca."""
        resumen = ResumenCaja(
            aportes=self.aporte_dao.total(),
            cobrado=self.pedido_repo.total_cobrado(),
            por_cobrar=self.pedido_repo.total_por_cobrar(),
            gastos=self.gasto_dao.total(),
        )
        self.lbl_saldo.value = moneda(resumen.saldo)
        self.lbl_saldo.color = ft.Colors.RED_700 if resumen.saldo < 0 else ft.Colors.GREEN_800
        self.lbl_aportes.value = moneda(resumen.aportes)
        self.lbl_cobrado.value = moneda(resumen.cobrado)
        self.lbl_gastos.value = moneda(resumen.gastos)
        self.lbl_por_cobrar.value = moneda(resumen.por_cobrar)
        for etiqueta in (self.lbl_aportes, self.lbl_cobrado, self.lbl_gastos, self.lbl_por_cobrar):
            etiqueta.color = ft.Colors.BLACK87

        self.tabla_aportes.rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(a.fecha)),
                    ft.DataCell(ft.Text(a.descripcion)),
                    ft.DataCell(ft.Text(moneda(a.monto))),
                    ft.DataCell(
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            tooltip="Eliminar",
                            on_click=lambda e, ap=a: self.pedir_eliminar(ap),
                        )
                    ),
                ]
            )
            for a in self.aporte_dao.obtener_todos()
        ]
        self.tabla_categorias.rows = [
            ft.DataRow(cells=[ft.DataCell(ft.Text(nombre)), ft.DataCell(ft.Text(moneda(total)))])
            for nombre, total in self.gasto_dao.total_por_categoria()
        ]

    def refrescar(self) -> None:
        self.cargar()
        self.page.update()

    def agregar_aporte(self, e) -> None:
        try:
            aporte = Aporte(
                descripcion=self.txt_descripcion.value,
                monto=leer_numero(self.txt_monto.value, "El monto"),
                fecha=self.txt_fecha.value,
            )
        except ValueError as err:
            mostrar_mensaje(self.mensaje, str(err), error=True)
            self.page.update()
            return

        if self.aporte_dao.agregar(aporte):
            self.txt_descripcion.value = ""
            self.txt_monto.value = ""
            mostrar_mensaje(self.mensaje, "Aporte registrado.")
        else:
            mostrar_mensaje(self.mensaje, self.aporte_dao.ultimo_error, error=True)
        self.refrescar()

    def pedir_eliminar(self, aporte: Aporte) -> None:
        confirmar(self.page, f"Se eliminara el aporte: {aporte}", lambda: self.eliminar(aporte))

    def eliminar(self, aporte: Aporte) -> None:
        if self.aporte_dao.eliminar(aporte.id):
            mostrar_mensaje(self.mensaje, "Aporte eliminado.")
        else:
            mostrar_mensaje(self.mensaje, self.aporte_dao.ultimo_error, error=True)
        self.refrescar()
