from datetime import date, datetime
from typing import Optional

import flet as ft

from domain.pedido import DetallePedido, Pedido
from domain.plato import Plato
from ui import tema
from ui.components.dialogo_personalizar import DialogoPersonalizar
from ui.components.utilidades import moneda
from ui.contexto import Contexto

ICONOS_TIPO = {"almuerzo": ft.Icons.RESTAURANT, "bebida": ft.Icons.LOCAL_DRINK}


class PanelInicio:
    """Punto de venta: a la izquierda el menu con tarjetas y a la derecha el pedido
    de la mesa elegida. Es la pantalla principal del cajero."""

    def __init__(self, ctx: Contexto) -> None:
        self.ctx = ctx
        self.page = ctx.page
        self.pedido: Optional[Pedido] = None  # pedido de la mesa que esta elegida
        self.platos: list[Plato] = []

        # ---- parte superior: buscador, mesa y hora
        self.txt_buscar = tema.campo(hint_text="Buscar producto...", prefix_icon=ft.Icons.SEARCH,
                                     expand=True, on_change=self.filtrar)
        self.dd_mesa = tema.lista(width=170, on_change=self.cambiar_mesa)
        self.lbl_hora = ft.Text("", weight=ft.FontWeight.BOLD, color=tema.TEXTO)
        self.lbl_fecha = ft.Text("", size=11, color=tema.GRIS)

        # ---- menu de productos
        self.grid = ft.GridView(expand=True, max_extent=190, child_aspect_ratio=0.8,
                                spacing=14, run_spacing=14)

        # ---- panel "Tu pedido"
        self.lbl_mesa_pedido = ft.Text("Tu pedido", weight=ft.FontWeight.BOLD, color=tema.BLANCO, size=16)
        self.lbl_cantidad = ft.Text("0", weight=ft.FontWeight.BOLD, color=tema.AZUL_OSCURO, size=12)
        self.lista_pedido = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)
        self.lbl_total = ft.Text("$0", size=22, weight=ft.FontWeight.BOLD, color=tema.TEXTO)
        self.btn_finalizar = tema.boton("Finalizar pedido", self.finalizar,
                                        icono=ft.Icons.RECEIPT_LONG, ancho=280)

        panel_pedido = ft.Container(
            width=310,
            bgcolor=tema.BLANCO,
            border_radius=18,
            shadow=tema.sombra(),
            content=ft.Column(
                [
                    ft.Container(
                        bgcolor=tema.AZUL,
                        padding=14,
                        border_radius=ft.border_radius.only(top_left=18, top_right=18),
                        content=ft.Row(
                            [ft.Icon(ft.Icons.SHOPPING_CART, color=tema.BLANCO),
                             self.lbl_mesa_pedido,
                             ft.Container(content=self.lbl_cantidad, bgcolor=tema.BLANCO,
                                          border_radius=12, padding=ft.padding.symmetric(horizontal=9, vertical=2))],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                    ),
                    ft.Container(content=self.lista_pedido, expand=True, padding=12),
                    ft.Container(
                        padding=12,
                        content=ft.Column(
                            [ft.Row([ft.Text("Total:", weight=ft.FontWeight.BOLD, color=tema.TEXTO), self.lbl_total],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                             self.btn_finalizar],
                            spacing=10,
                        ),
                    ),
                ],
                spacing=0,
            ),
        )

        izquierda = ft.Column(
            [
                ft.Row(
                    [self.txt_buscar,
                     self.dd_mesa,
                     ft.Container(
                         bgcolor=tema.BLANCO, border_radius=16, padding=ft.padding.symmetric(horizontal=14, vertical=6),
                         content=ft.Row([ft.Icon(ft.Icons.ACCESS_TIME, color=tema.AZUL),
                                         ft.Column([self.lbl_hora, self.lbl_fecha], spacing=0)]),
                     )],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                tema.titulo("Menú"),
                self.grid,
            ],
            expand=True,
            spacing=12,
        )

        self.contenido = ft.Row([izquierda, panel_pedido], expand=True, spacing=16,
                                vertical_alignment=ft.CrossAxisAlignment.STRETCH)

    # ------------------------------------------------------------- cargar datos
    def refrescar(self) -> None:
        ahora = datetime.now()
        self.lbl_hora.value = f"{ahora:%H:%M}"
        self.lbl_fecha.value = f"{ahora:%d/%m/%Y}"

        self.platos = self.ctx.platos.obtener_todos()

        mesas = self.ctx.mesas.obtener_todos()
        self.dd_mesa.options = [ft.dropdown.Option(key=str(m.id), text=m.nombre) for m in mesas]
        ids = [m.id for m in mesas]
        if self.ctx.id_mesa_activa not in ids:
            self.ctx.id_mesa_activa = ids[0] if ids else None
        self.dd_mesa.value = str(self.ctx.id_mesa_activa) if self.ctx.id_mesa_activa else None

        self._cargar_pedido()
        self._pintar_grid()
        self._pintar_pedido()
        self.page.update()

    def _cargar_pedido(self) -> None:
        """Si la mesa ya tiene un pedido abierto se continua con ese; si no, se empieza uno nuevo."""
        self.pedido = None
        id_mesa = self.ctx.id_mesa_activa
        if id_mesa is None:
            return
        self.pedido = self.ctx.pedidos.obtener_abierto_de_mesa(id_mesa)
        if self.pedido is None:
            mesa = self.ctx.mesas.obtener_por_id(id_mesa)
            self.pedido = Pedido(
                fecha=date.today().isoformat(),
                id_mesa=id_mesa,
                id_usuario=self.ctx.usuario.id,
                nombre_mesa=mesa.nombre if mesa else "",
            )

    # ------------------------------------------------------------------ menu
    def _pintar_grid(self) -> None:
        texto = (self.txt_buscar.value or "").strip().lower()
        self.grid.controls = [
            self._tarjeta_producto(p) for p in self.platos if texto in p.nombre.lower()
        ]

    def _tarjeta_producto(self, plato: Plato) -> ft.Container:
        icono = ICONOS_TIPO.get(plato.tipo, ft.Icons.FASTFOOD)
        if plato.es_almuerzo:
            accion = tema.boton("Personalizar", lambda e, p=plato: self.personalizar(p),
                                icono=ft.Icons.RESTAURANT, compacto=True)
        else:
            accion = ft.IconButton(icon=ft.Icons.ADD, icon_color=tema.BLANCO, bgcolor=tema.AZUL,
                                   on_click=lambda e, p=plato: self.agregar_producto(p))
        return ft.Container(
            bgcolor=tema.BLANCO,
            border_radius=18,
            padding=10,
            shadow=tema.sombra(),
            content=ft.Column(
                [
                    ft.Container(content=ft.Icon(icono, size=44, color=tema.AZUL), bgcolor=tema.AZUL_CLARO,
                                 border_radius=14, height=84, alignment=ft.alignment.center),
                    ft.Text(plato.nombre, weight=ft.FontWeight.BOLD, size=13, color=tema.TEXTO,
                            text_align=ft.TextAlign.CENTER),
                    ft.Text(moneda(plato.precio), size=16, weight=ft.FontWeight.BOLD, color=tema.TEXTO),
                    accion,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=6,
            ),
        )

    def filtrar(self, e) -> None:
        self._pintar_grid()
        self.page.update()

    def cambiar_mesa(self, e) -> None:
        self.ctx.id_mesa_activa = int(self.dd_mesa.value)
        self._cargar_pedido()
        self._pintar_pedido()
        self.page.update()

    # ------------------------------------------------------------ pedido actual
    def personalizar(self, plato: Plato) -> None:
        """Abre la ventana de 3 pasos y, al terminar, agrega el almuerzo con sus notas."""
        DialogoPersonalizar(self.ctx, plato, lambda notas: self.agregar_producto(plato, notas)).abrir()

    def agregar_producto(self, plato: Plato, notas: str = "") -> None:
        if self.pedido is None:
            self.ctx.aviso("Primero crea una mesa en Configuración.", error=True)
            return
        self.pedido.agregar_detalle(DetallePedido(plato.id, plato.nombre, 1, plato.precio, notas))
        self._pintar_pedido()
        self.page.update()

    def _cambiar_cantidad(self, detalle: DetallePedido, cambio: int) -> None:
        nueva = detalle.cantidad + cambio
        if nueva <= 0:
            self.pedido.quitar_detalle(detalle)
        else:
            detalle.cantidad = nueva
        self._pintar_pedido()
        self.page.update()

    def _pintar_pedido(self) -> None:
        self.lista_pedido.controls.clear()
        if self.pedido is None:
            self.lbl_mesa_pedido.value = "Tu pedido"
            self.lbl_cantidad.value = "0"
            self.lbl_total.value = moneda(0)
            self.lista_pedido.controls.append(self._mensaje_vacio("No hay mesas", "Crea mesas en Configuración"))
            return

        self.lbl_mesa_pedido.value = f"Tu pedido - {self.pedido.nombre_mesa}"
        self.lbl_cantidad.value = str(self.pedido.cantidad_items)
        self.lbl_total.value = moneda(self.pedido.total)

        if len(self.pedido) == 0:
            self.lista_pedido.controls.append(
                self._mensaje_vacio("Tu pedido está vacío", "Agrega productos del menú"))
            return
        for detalle in self.pedido.detalles:
            self.lista_pedido.controls.append(self._fila_detalle(detalle))

    def _mensaje_vacio(self, titulo: str, detalle: str) -> ft.Container:
        return ft.Container(
            alignment=ft.alignment.center, padding=30,
            content=ft.Column(
                [ft.Icon(ft.Icons.SHOPPING_BAG, size=44, color="#B7C3E6"),
                 ft.Text(titulo, color=tema.GRIS, weight=ft.FontWeight.BOLD),
                 ft.Text(detalle, size=12, color=tema.GRIS)],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4,
            ),
        )

    def _fila_detalle(self, detalle: DetallePedido) -> ft.Container:
        textos = [ft.Text(detalle.nombre_plato, weight=ft.FontWeight.BOLD, color=tema.TEXTO)]
        if detalle.notas:
            textos.append(ft.Text(detalle.notas, size=11, color=tema.GRIS))
        return ft.Container(
            bgcolor=tema.FONDO, border_radius=12, padding=10,
            content=ft.Column(
                [
                    ft.Row([ft.Column(textos, spacing=0, expand=True),
                            ft.Text(moneda(detalle.subtotal), weight=ft.FontWeight.BOLD, color=tema.TEXTO)],
                           vertical_alignment=ft.CrossAxisAlignment.START),
                    ft.Row(
                        [ft.IconButton(icon=ft.Icons.REMOVE, icon_size=18,
                                       on_click=lambda e, d=detalle: self._cambiar_cantidad(d, -1)),
                         ft.Text(str(detalle.cantidad), weight=ft.FontWeight.BOLD),
                         ft.IconButton(icon=ft.Icons.ADD, icon_size=18,
                                       on_click=lambda e, d=detalle: self._cambiar_cantidad(d, 1))],
                        spacing=0,
                    ),
                ],
                spacing=0,
            ),
        )

    def finalizar(self, e) -> None:
        """Guarda el pedido de la mesa y la deja ocupada (equivale a enviarlo a cocina)."""
        if self.pedido is None:
            return
        if len(self.pedido) == 0:
            self.ctx.aviso("Agrega productos al pedido antes de finalizar.", error=True)
            return
        if not self.ctx.pedidos.guardar(self.pedido):
            self.ctx.aviso(self.ctx.pedidos.ultimo_error, error=True)
            return
        self.ctx.aviso(f"Pedido guardado en {self.pedido.nombre_mesa}. Ya puedes cobrarlo desde Mesas.")
        self._cargar_pedido()
        self._pintar_pedido()
        self.page.update()
