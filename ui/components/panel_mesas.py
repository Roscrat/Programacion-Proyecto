from datetime import datetime
from typing import Optional

import flet as ft

from domain.mesa import Mesa
from domain.pedido import DetallePedido, Pedido
from ui import tema
from ui.components.dialogo_cobro import DialogoCobro
from ui.components.utilidades import confirmar, moneda
from ui.contexto import Contexto


class PanelMesas:
    """Muestra las mesas. Al tocar una se abre su comanda, donde se puede ajustar
    el pedido, agregar mas productos, cobrar o cancelar."""

    def __init__(self, ctx: Contexto) -> None:
        self.ctx = ctx
        self.page = ctx.page
        self.area = ft.Container(expand=True)
        self.contenido = self.area

    def refrescar(self) -> None:
        """Se llama al entrar a la pantalla: siempre empieza mostrando la lista de mesas."""
        self._mostrar_lista()
        self.page.update()

    # --------------------------------------------------------- lista de mesas
    def _mostrar_lista(self) -> None:
        mesas = self.ctx.mesas.obtener_todos()
        grid = ft.GridView(expand=True, max_extent=210, child_aspect_ratio=1.1, spacing=14, run_spacing=14)
        grid.controls = [self._tarjeta_mesa(m) for m in mesas]
        if not mesas:
            grid.controls = [ft.Text("No hay mesas. Créalas en Configuración.", color=tema.GRIS)]
        self.area.content = ft.Column(
            [tema.titulo("Mesas"),
             ft.Text("Toca una mesa para ver o abrir su comanda.", color=tema.GRIS),
             grid],
            expand=True,
            spacing=10,
        )

    def _tarjeta_mesa(self, mesa: Mesa) -> ft.Container:
        if mesa.ocupada:
            estado = tema.etiqueta_estado("Ocupada", tema.ROJO_CLARO, tema.ROJO)
        else:
            estado = tema.etiqueta_estado("Libre", tema.VERDE_CLARO, tema.VERDE)
        return ft.Container(
            bgcolor=tema.BLANCO, border_radius=18, padding=16, shadow=tema.sombra(), ink=True,
            on_click=lambda e, m=mesa: self._mostrar_comanda(m.id),
            content=ft.Column(
                [ft.Icon(ft.Icons.TABLE_RESTAURANT, size=40, color=tema.AZUL),
                 ft.Text(mesa.nombre, size=18, weight=ft.FontWeight.BOLD, color=tema.TEXTO),
                 ft.Text(mesa.zona, size=12, color=tema.GRIS),
                 estado],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6,
            ),
        )

    # ---------------------------------------------------------------- comanda
    def _mostrar_comanda(self, id_mesa: int) -> None:
        """Dibuja la comanda de una mesa. Se vuelve a llamar cada vez que algo cambia."""
        mesa = self.ctx.mesas.obtener_por_id(id_mesa)
        pedido = self.ctx.pedidos.obtener_abierto_de_mesa(id_mesa)

        estado = (tema.etiqueta_estado("Ocupada", tema.ROJO_CLARO, tema.ROJO) if mesa.ocupada
                  else tema.etiqueta_estado("Libre", tema.VERDE_CLARO, tema.VERDE))
        ahora = datetime.now()
        encabezado = ft.Row(
            [ft.IconButton(icon=ft.Icons.ARROW_BACK, tooltip="Volver a las mesas",
                           on_click=lambda e: self.refrescar()),
             ft.Column([ft.Text(f"Comanda {mesa.nombre}", size=24, weight=ft.FontWeight.BOLD, color=tema.TEXTO),
                        ft.Text(f"Zona: {mesa.zona}", color=tema.GRIS)], spacing=0, expand=True),
             estado,
             ft.Container(bgcolor=tema.BLANCO, border_radius=16, padding=ft.padding.symmetric(horizontal=14, vertical=6),
                          content=ft.Text(f"{ahora:%H:%M}  {ahora:%d/%m/%Y}", weight=ft.FontWeight.BOLD, color=tema.TEXTO))],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        if pedido is None:
            cuerpo = self._comanda_vacia(mesa)
        else:
            cuerpo = self._comanda_con_pedido(mesa, pedido)

        self.area.content = ft.Column([encabezado, cuerpo], expand=True, spacing=12)
        self.page.update()

    def _comanda_vacia(self, mesa: Mesa) -> ft.Control:
        return ft.Container(
            expand=True, alignment=ft.alignment.center,
            content=ft.Column(
                [ft.Icon(ft.Icons.TABLE_RESTAURANT, size=60, color="#B7C3E6"),
                 ft.Text("La mesa está libre.", size=18, weight=ft.FontWeight.BOLD, color=tema.TEXTO),
                 ft.Text("Agrega productos para abrir un pedido.", color=tema.GRIS),
                 tema.boton("Agregar productos", lambda e: self._ir_a_inicio(mesa.id), icono=ft.Icons.ADD)],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10,
            ),
        )

    def _comanda_con_pedido(self, mesa: Mesa, pedido: Pedido) -> ft.Control:
        txt_observaciones = tema.campo(hint_text="Novedades u observaciones...",
                                       prefix_icon=ft.Icons.RECEIPT_LONG, value=pedido.observaciones)

        def guardar_observaciones(e=None):
            pedido.observaciones = txt_observaciones.value or ""
            self.ctx.pedidos.guardar(pedido)

        txt_observaciones.on_blur = guardar_observaciones
        txt_observaciones.on_submit = guardar_observaciones

        filas = ft.Column([self._fila_detalle(mesa, pedido, d) for d in pedido.detalles],
                          spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)

        subtotal = ft.Container(
            bgcolor=tema.AZUL_CLARO, border_radius=14, padding=14,
            content=ft.Row(
                [ft.Text(f"Subtotal ({pedido.cantidad_items} ítems)", weight=ft.FontWeight.BOLD, color=tema.TEXTO),
                 ft.Text(moneda(pedido.total), size=22, weight=ft.FontWeight.BOLD, color=tema.TEXTO)],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )

        def cobrar(e):
            guardar_observaciones()
            DialogoCobro(self.ctx, pedido, self.refrescar).abrir()

        def cancelar(e):
            confirmar(self.page, f"Se cancelará el pedido de {mesa.nombre} y la mesa quedará libre.",
                      lambda: self._cancelar_pedido(pedido))

        botones = ft.Column(
            [tema.boton("Agregar productos", lambda e: self._ir_a_inicio(mesa.id), icono=ft.Icons.ADD, ancho=200),
             tema.boton("Cobrar mesa", cobrar, icono=ft.Icons.CREDIT_CARD, color=tema.VERDE, ancho=200),
             tema.boton("Cancelar pedido", cancelar, icono=ft.Icons.DELETE, color=tema.ROJO_CLARO,
                        color_texto=tema.ROJO, ancho=200)],
            spacing=12,
        )

        izquierda = ft.Column(
            [txt_observaciones, tema.titulo("Pedido", 18), filas, subtotal],
            expand=True, spacing=10,
        )
        return ft.Row([izquierda, botones], expand=True, spacing=16,
                      vertical_alignment=ft.CrossAxisAlignment.START)

    def _fila_detalle(self, mesa: Mesa, pedido: Pedido, detalle: DetallePedido) -> ft.Container:
        textos = [ft.Text(detalle.nombre_plato, weight=ft.FontWeight.BOLD, color=tema.TEXTO),
                  ft.Text(moneda(detalle.precio_unitario), size=12, color=tema.GRIS)]
        if detalle.notas:
            textos.insert(1, ft.Text(detalle.notas, size=12, color=tema.GRIS))
        return ft.Container(
            bgcolor=tema.BLANCO, border_radius=14, padding=12,
            content=ft.Row(
                [ft.Column(textos, spacing=0, expand=True),
                 ft.IconButton(icon=ft.Icons.REMOVE, icon_color=tema.AZUL, bgcolor=tema.AZUL_CLARO,
                               on_click=lambda e: self._cambiar_cantidad(mesa, pedido, detalle, -1)),
                 ft.Text(str(detalle.cantidad), size=18, weight=ft.FontWeight.BOLD, color=tema.TEXTO),
                 ft.IconButton(icon=ft.Icons.ADD, icon_color=tema.AZUL, bgcolor=tema.AZUL_CLARO,
                               on_click=lambda e: self._cambiar_cantidad(mesa, pedido, detalle, 1)),
                 ft.Text(moneda(detalle.subtotal), weight=ft.FontWeight.BOLD, color=tema.TEXTO, width=90,
                         text_align=ft.TextAlign.RIGHT)],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    # ---------------------------------------------------------------- acciones
    def _cambiar_cantidad(self, mesa: Mesa, pedido: Pedido, detalle: DetallePedido, cambio: int) -> None:
        nueva = detalle.cantidad + cambio
        if nueva <= 0:
            pedido.quitar_detalle(detalle)
        else:
            detalle.cantidad = nueva

        if len(pedido) == 0:
            # Si ya no queda ningun producto, el pedido se cancela y la mesa se libera
            self.ctx.pedidos.eliminar(pedido.id)
            self.ctx.aviso("Pedido cancelado. La mesa quedó libre.")
        elif not self.ctx.pedidos.guardar(pedido):
            self.ctx.aviso(self.ctx.pedidos.ultimo_error, error=True)
        self._mostrar_comanda(mesa.id)

    def _cancelar_pedido(self, pedido: Pedido) -> None:
        if self.ctx.pedidos.eliminar(pedido.id):
            self.ctx.aviso("Pedido cancelado. La mesa quedó libre.")
        else:
            self.ctx.aviso(self.ctx.pedidos.ultimo_error, error=True)
        self.refrescar()

    def _ir_a_inicio(self, id_mesa: int) -> None:
        """Va al punto de venta con esta mesa ya elegida."""
        self.ctx.id_mesa_activa = id_mesa
        self.ctx.ir_a("Inicio")
