import flet as ft

from domain.plato import TIPOS_PLATO, Plato
from domain.validaciones import leer_numero
from ui import tema
from ui.components.utilidades import (
    confirmar,
    con_scroll,
    encabezados,
    moneda,
    mostrar_mensaje,
)
from ui.contexto import Contexto


class PanelMenu:
    """Administracion de los productos y sus precios."""

    def __init__(self, ctx: Contexto) -> None:
        self.ctx = ctx
        self.page = ctx.page
        self.repo = ctx.platos
        self.id_editando = None

        self.txt_nombre = tema.campo(label="Nombre del producto", width=300)
        self.txt_precio = tema.campo(label="Precio de venta", width=170)
        self.dd_tipo = tema.lista(
            label="Tipo", width=240, value="otro",
            options=[ft.dropdown.Option(key=k, text=v) for k, v in TIPOS_PLATO.items()],
        )
        self.btn_guardar = tema.boton("Agregar producto", self.guardar)
        self.btn_cancelar = tema.boton_suave("Cancelar edición", self.cancelar)
        self.btn_cancelar.visible = False
        self.mensaje = ft.Text("")
        self.tabla = ft.DataTable(columns=encabezados("Producto", "Tipo", "Precio", "Acciones"), rows=[])

        self.contenido = ft.Column(
            [
                tema.titulo("Menú y precios"),
                ft.Text("Aquí se registran los productos que se venden. Los de tipo almuerzo "
                        "se personalizan en 3 pasos al venderlos.", color=tema.GRIS),
                ft.Row([self.txt_nombre, self.txt_precio, self.dd_tipo], wrap=True),
                ft.Row([self.btn_guardar, self.btn_cancelar]),
                self.mensaje,
                con_scroll(self.tabla),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    def refrescar(self) -> None:
        self.tabla.rows = []
        for plato in self.repo.obtener_todos():
            self.tabla.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(plato.nombre)),
                        ft.DataCell(ft.Text(TIPOS_PLATO[plato.tipo])),
                        ft.DataCell(ft.Text(moneda(plato.precio))),
                        ft.DataCell(
                            ft.Row(
                                [
                                    ft.IconButton(icon=ft.Icons.EDIT, tooltip="Editar",
                                                  on_click=lambda e, p=plato: self.editar(p)),
                                    ft.IconButton(icon=ft.Icons.DELETE, tooltip="Eliminar",
                                                  on_click=lambda e, p=plato: self.pedir_eliminar(p)),
                                ]
                            )
                        ),
                    ]
                )
            )
        self.page.update()

    def _limpiar_formulario(self) -> None:
        self.id_editando = None
        self.txt_nombre.value = ""
        self.txt_precio.value = ""
        self.dd_tipo.value = "otro"
        self.btn_guardar.text = "Agregar producto"
        self.btn_cancelar.visible = False

    def guardar(self, e) -> None:
        try:
            plato = Plato(
                nombre=self.txt_nombre.value,
                precio=leer_numero(self.txt_precio.value, "El precio"),
                tipo=self.dd_tipo.value,
                id_plato=self.id_editando,
            )
        except ValueError as err:
            mostrar_mensaje(self.mensaje, str(err), error=True)
            self.page.update()
            return

        if self.id_editando is None:
            ok = self.repo.agregar(plato)
        else:
            ok = self.repo.actualizar(plato)

        if ok:
            self._limpiar_formulario()
            mostrar_mensaje(self.mensaje, "Producto guardado.")
        else:
            mostrar_mensaje(self.mensaje, self.repo.ultimo_error, error=True)
        self.refrescar()

    def editar(self, plato: Plato) -> None:
        self.id_editando = plato.id
        self.txt_nombre.value = plato.nombre
        self.txt_precio.value = str(int(plato.precio))
        self.dd_tipo.value = plato.tipo
        self.btn_guardar.text = "Guardar cambios"
        self.btn_cancelar.visible = True
        mostrar_mensaje(self.mensaje, "Editando producto.")
        self.page.update()

    def cancelar(self, e) -> None:
        self._limpiar_formulario()
        mostrar_mensaje(self.mensaje, "")
        self.page.update()

    def pedir_eliminar(self, plato: Plato) -> None:
        confirmar(self.page, f"Se eliminará el producto: {plato.nombre}", lambda: self.eliminar(plato))

    def eliminar(self, plato: Plato) -> None:
        if self.repo.eliminar(plato.id):
            mostrar_mensaje(self.mensaje, "Producto eliminado.")
        else:
            mostrar_mensaje(self.mensaje, self.repo.ultimo_error, error=True)
        self.refrescar()
