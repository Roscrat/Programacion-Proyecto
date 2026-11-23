import flet as ft

from data.database_manager import DatabaseManager
from ui import tema
from ui.components.panel_config import PanelConfig
from ui.components.panel_finanzas import PanelFinanzas
from ui.components.panel_inicio import PanelInicio
from ui.components.panel_menu import PanelMenu
from ui.components.panel_mesas import PanelMesas
from ui.components.panel_pedidos import PanelPedidos
from ui.contexto import Contexto

# Opciones de la barra lateral (todas disponibles, sin cuentas ni roles).
MENU = [
    ("Inicio", ft.Icons.HOME),
    ("Menú", ft.Icons.RESTAURANT_MENU),
    ("Pedidos", ft.Icons.RECEIPT_LONG),
    ("Mesas", ft.Icons.TABLE_RESTAURANT),
    ("Finanzas", ft.Icons.ACCOUNT_BALANCE_WALLET),
    ("Configuración", ft.Icons.SETTINGS),
]


class AppView:
    """Controla que pantalla se ve: la aplicacion con su barra lateral (sin login)."""

    def __init__(self, page: ft.Page, db: DatabaseManager) -> None:
        self.page = page
        self.ctx = Contexto(page, db)
        self.ctx.ir_a = self.mostrar
        self.ctx.usuario = self.ctx.usuarios.obtener_general()  # firma los pedidos

        self.paneles = {}
        self.actual = "Inicio"
        self.barra = ft.Container(
            width=210,
            bgcolor=tema.AZUL_OSCURO,
            padding=14,
            border_radius=ft.border_radius.only(top_right=24, bottom_right=24),
        )
        self.area = ft.Container(expand=True, padding=20)

    def construir(self) -> None:
        self.page.title = "La Buena Mesa - Restaurante"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.bgcolor = tema.FONDO
        self.page.padding = 0
        self.page.window.width = 1280
        self.page.window.height = 820
        self.page.window.min_width = 1050
        self.page.window.min_height = 680
        self.entrar()

    # ----------------------------------------------------------------- inicio
    def entrar(self) -> None:
        """Arma todos los paneles y muestra la aplicacion."""
        self.paneles = {
            "Inicio": PanelInicio(self.ctx),
            "Pedidos": PanelPedidos(self.ctx),
            "Mesas": PanelMesas(self.ctx),
            "Menú": PanelMenu(self.ctx),
            "Finanzas": PanelFinanzas(self.ctx),
            "Configuración": PanelConfig(self.ctx),
        }

        self.page.clean()
        self.page.add(
            ft.Row(
                [self.barra, self.area],
                expand=True,
                spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
            )
        )
        self.mostrar("Inicio")

    # ------------------------------------------------------------ navegacion
    def mostrar(self, nombre: str) -> None:
        if nombre not in self.paneles:
            nombre = "Inicio"
        self.actual = nombre
        panel = self.paneles[nombre]
        self.area.content = panel.contenido
        self.barra.content = self._contenido_barra()
        panel.refrescar()  # cada panel recarga sus datos y hace page.update()

    def _contenido_barra(self) -> ft.Column:
        items = []
        for nombre, icono in MENU:
            activo = nombre == self.actual
            items.append(
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=14, vertical=12),
                    border_radius=14,
                    bgcolor=tema.AZUL if activo else None,
                    ink=True,
                    on_click=lambda e, n=nombre: self.mostrar(n),
                    content=ft.Row(
                        [ft.Icon(icono, color=tema.BLANCO, size=20),
                         ft.Text(nombre, color=tema.BLANCO,
                                 weight=ft.FontWeight.BOLD if activo else ft.FontWeight.NORMAL)],
                        spacing=12,
                    ),
                )
            )

        logo = ft.Column(
            [ft.Icon(ft.Icons.RESTAURANT, size=40, color=tema.BLANCO),
             ft.Text("La Buena Mesa", size=22, italic=True, weight=ft.FontWeight.BOLD,
                     color=tema.BLANCO, text_align=ft.TextAlign.CENTER),
             ft.Text("RESTAURANTE", size=10, color="#BFD0FF")],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=2,
        )
        pie = ft.Text("¡Buen apetito!", italic=True, color="#BFD0FF", size=16)
        return ft.Column(
            [logo, ft.Container(height=14), ft.Column(items, spacing=6, expand=True), pie],
            expand=True,
        )
