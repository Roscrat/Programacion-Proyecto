import flet as ft

from domain.pedido import Pedido
from domain.validaciones import leer_numero
from ui import tema
from ui.components.utilidades import moneda
from ui.contexto import Contexto

METODOS = [("Efectivo", ft.Icons.PAYMENTS), ("Tarjeta", ft.Icons.CREDIT_CARD), ("Otro", ft.Icons.MORE_HORIZ)]


class DialogoCobro:
    """Ventana para cobrar una mesa. Al confirmar muestra dos avisos seguidos:
    'Pago registrado' y 'Mesa liberada'."""

    def __init__(self, ctx: Contexto, pedido: Pedido, al_terminar) -> None:
        self.ctx = ctx
        self.pedido = pedido
        self.al_terminar = al_terminar
        self.total = pedido.total
        self.metodo = "Efectivo"
        self.cambio = 0.0

        self.txt_cliente = tema.campo(hint_text="Datos del cliente (opcional)", prefix_icon=ft.Icons.PERSON)
        self.txt_recibido = tema.campo(hint_text="Efectivo recibido", prefix_text="$ ",
                                       width=190, on_change=self.recalcular)
        self.btn_exacto = tema.boton_suave("Pago exacto", self.pago_exacto, icono=ft.Icons.CHECK, compacto=True)
        self.lbl_cambio = ft.Text("$0", size=20, weight=ft.FontWeight.BOLD, color=tema.AZUL)
        self.lbl_error = ft.Text("", color=tema.ROJO, size=13)

        # Botones de metodo de pago: se guarda cada uno para poder repintarlos
        self.botones_metodo = {}
        fila_metodos = ft.Row(
            [self._boton_metodo(nombre, icono) for nombre, icono in METODOS],
            spacing=10,
        )
        self.fila_efectivo = ft.Row(
            [ft.Text("Efectivo recibido:", weight=ft.FontWeight.BOLD, color=tema.TEXTO),
             self.txt_recibido, self.btn_exacto],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self.fila_cambio = ft.Container(
            bgcolor=tema.AZUL_CLARO, border_radius=14, padding=12,
            content=ft.Row(
                [ft.Text("Cambio a devolver:", weight=ft.FontWeight.BOLD, color=tema.TEXTO), self.lbl_cambio],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )
        self._pintar_metodos()

        contenido = ft.Column(
            [
                ft.Row(
                    [ft.Icon(ft.Icons.CREDIT_CARD, color=tema.AZUL, size=34),
                     ft.Column(
                         [ft.Text(f"Cobrar {pedido.nombre_mesa}", size=20, weight=ft.FontWeight.BOLD, color=tema.TEXTO),
                          ft.Text("Registra el pago y libera la mesa", size=13, color=tema.GRIS)],
                         spacing=0, expand=True),
                     ft.IconButton(icon=ft.Icons.CLOSE, on_click=self.cerrar)],
                ),
                ft.Container(
                    bgcolor=tema.VERDE_CLARO, border_radius=14, padding=14,
                    content=ft.Row(
                        [ft.Text("Total a pagar:", size=16, weight=ft.FontWeight.BOLD, color=tema.TEXTO),
                         ft.Text(moneda(self.total), size=30, weight=ft.FontWeight.BOLD, color=tema.VERDE)],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ),
                self.txt_cliente,
                ft.Text("Método de pago:", weight=ft.FontWeight.BOLD, color=tema.TEXTO),
                fila_metodos,
                self.fila_efectivo,
                self.fila_cambio,
                self.lbl_error,
                ft.Row(
                    [tema.boton_suave("Cancelar", self.cerrar, icono=ft.Icons.CLOSE),
                     tema.boton("Confirmar y facturar", self.confirmar, icono=ft.Icons.CHECK, color=tema.VERDE)],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ],
            spacing=12,
            tight=True,
        )
        self.dialogo = ft.AlertDialog(
            modal=True,
            content=ft.Container(width=560, content=contenido),
            shape=ft.RoundedRectangleBorder(radius=22),
        )

    def abrir(self) -> None:
        self.ctx.page.open(self.dialogo)

    def cerrar(self, e=None) -> None:
        self.ctx.page.close(self.dialogo)

    # --------------------------------------------------------- metodo de pago
    def _boton_metodo(self, nombre: str, icono) -> ft.Container:
        icon = ft.Icon(icono, size=22)
        texto = ft.Text(nombre, size=13, weight=ft.FontWeight.BOLD)
        contenedor = ft.Container(
            expand=True, padding=10, border_radius=14, ink=True,
            on_click=lambda e: self.elegir_metodo(nombre),
            content=ft.Column([icon, texto], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
        )
        self.botones_metodo[nombre] = (contenedor, icon, texto)
        return contenedor

    def _pintar_metodos(self) -> None:
        for nombre, (contenedor, icon, texto) in self.botones_metodo.items():
            elegido = nombre == self.metodo
            contenedor.bgcolor = tema.AZUL if elegido else tema.AZUL_CLARO
            icon.color = tema.BLANCO if elegido else tema.AZUL
            texto.color = tema.BLANCO if elegido else tema.AZUL
        # El efectivo recibido y el cambio solo tienen sentido si se paga en efectivo
        es_efectivo = self.metodo == "Efectivo"
        self.fila_efectivo.visible = es_efectivo
        self.fila_cambio.visible = es_efectivo

    def elegir_metodo(self, nombre: str) -> None:
        self.metodo = nombre
        self.lbl_error.value = ""
        self._pintar_metodos()
        self.recalcular()

    # ------------------------------------------------------------- efectivo
    def pago_exacto(self, e) -> None:
        self.txt_recibido.value = str(int(self.total))
        self.recalcular()

    def recalcular(self, e=None) -> None:
        """Calcula el cambio cada vez que se escribe el efectivo recibido."""
        try:
            recibido = leer_numero(self.txt_recibido.value, "El efectivo recibido")
        except ValueError:
            recibido = 0.0
        self.cambio = max(recibido - self.total, 0.0)
        self.lbl_cambio.value = moneda(self.cambio)
        self.ctx.page.update()

    # ------------------------------------------------------------ confirmar
    def confirmar(self, e) -> None:
        if self.metodo == "Efectivo":
            try:
                recibido = leer_numero(self.txt_recibido.value, "El efectivo recibido")
            except ValueError as err:
                self.lbl_error.value = str(err)
                self.ctx.page.update()
                return
            if recibido < self.total:
                self.lbl_error.value = "El efectivo recibido es menor que el total."
                self.ctx.page.update()
                return
            self.cambio = recibido - self.total
        else:
            self.cambio = 0.0

        cliente = (self.txt_cliente.value or "").strip()
        if not self.ctx.pedidos.cobrar(self.pedido.id, self.metodo, cliente):
            self.lbl_error.value = self.ctx.pedidos.ultimo_error
            self.ctx.page.update()
            return

        self.cerrar()
        self._mostrar_pago_registrado()

    # -------------------------------------------------------- avisos finales
    def _mostrar_pago_registrado(self) -> None:
        def fila(etiqueta, valor):
            return ft.Row(
                [ft.Text(etiqueta, weight=ft.FontWeight.BOLD, color=tema.TEXTO),
                 ft.Text(valor, weight=ft.FontWeight.BOLD, color=tema.TEXTO)],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )

        def aceptar(e):
            self.ctx.page.close(dialogo)
            self._mostrar_mesa_liberada()

        dialogo = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=22),
            content=ft.Container(
                width=420,
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.CHECK_CIRCLE, size=70, color=tema.VERDE),
                        ft.Text("Pago registrado", size=26, weight=ft.FontWeight.BOLD, color=tema.TEXTO),
                        ft.Container(
                            bgcolor=tema.AZUL_CLARO, border_radius=14, padding=16,
                            content=ft.Column(
                                [fila("Mesa:", self.pedido.nombre_mesa),
                                 fila("Método de pago:", self.metodo),
                                 fila("Total pagado:", moneda(self.total)),
                                 fila("Cambio a devolver:", moneda(self.cambio))],
                                spacing=8,
                            ),
                        ),
                        tema.boton("Aceptar", aceptar, icono=ft.Icons.CHECK, ancho=240),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=14,
                    tight=True,
                ),
            ),
        )
        self.ctx.page.open(dialogo)

    def _mostrar_mesa_liberada(self) -> None:
        def aceptar(e):
            self.ctx.page.close(dialogo)
            self.al_terminar()

        dialogo = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=22),
            content=ft.Container(
                width=420,
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.RESTAURANT, size=70, color=tema.AZUL),
                        ft.Text("Mesa liberada", size=26, weight=ft.FontWeight.BOLD, color=tema.TEXTO),
                        ft.Text(f"La {self.pedido.nombre_mesa.lower()} ha sido cerrada correctamente.",
                                color=tema.GRIS, text_align=ft.TextAlign.CENTER),
                        tema.boton("Aceptar", aceptar, icono=ft.Icons.CHECK, color=tema.VERDE, ancho=240),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=14,
                    tight=True,
                ),
            ),
        )
        self.ctx.page.open(dialogo)
