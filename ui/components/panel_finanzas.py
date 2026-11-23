import flet as ft

from ui import tema
from ui.components.panel_gastos import PanelGastos
from ui.components.panel_resumen import PanelResumen
from ui.contexto import Contexto


class PanelFinanzas:
    """Junta dos pantallas: el resumen del dinero y los gastos."""

    def __init__(self, ctx: Contexto) -> None:
        self.page = ctx.page
        self.resumen = PanelResumen(ctx.page, ctx.aportes, ctx.gastos, ctx.pedidos)
        self.gastos = PanelGastos(ctx.page, ctx.gastos, ctx.categorias, self.resumen.cargar)
        self.actual = self.resumen

        self.area = ft.Container(expand=True)
        botones = ft.Row(
            [tema.boton_suave("Resumen del dinero", lambda e: self.mostrar(self.resumen),
                              icono=ft.Icons.ACCOUNT_BALANCE_WALLET),
             tema.boton_suave("Gastos", lambda e: self.mostrar(self.gastos), icono=ft.Icons.RECEIPT_LONG)],
        )
        self.contenido = ft.Column([botones, self.area], expand=True, spacing=12)

    def mostrar(self, panel) -> None:
        self.actual = panel
        self.area.content = panel.contenido
        panel.refrescar()

    def refrescar(self) -> None:
        self.mostrar(self.actual)
