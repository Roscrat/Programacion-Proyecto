import flet as ft

from domain.mesa import Mesa
from domain.opcion import PASOS, OpcionAlmuerzo
from ui import tema
from ui.components.utilidades import (
    confirmar,
    con_scroll,
    encabezados,
    mostrar_mensaje,
)
from ui.contexto import Contexto


class SeccionMesas:
    """Alta y baja de mesas."""

    def __init__(self, ctx: Contexto) -> None:
        self.ctx = ctx
        self.txt_nombre = tema.campo(label="Nombre de la mesa", width=220)
        self.txt_zona = tema.campo(label="Zona", width=220, value="Salón Principal")
        self.mensaje = ft.Text("")
        self.tabla = ft.DataTable(columns=encabezados("Mesa", "Zona", "Estado", ""), rows=[])
        self.contenido = ft.Column(
            [ft.Row([self.txt_nombre, self.txt_zona, tema.boton("Agregar mesa", self.agregar)], wrap=True),
             self.mensaje, con_scroll(self.tabla)],
            scroll=ft.ScrollMode.AUTO, expand=True,
        )

    def refrescar(self) -> None:
        self.tabla.rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(m.nombre)), ft.DataCell(ft.Text(m.zona)),
                ft.DataCell(ft.Text("Ocupada" if m.ocupada else "Libre")),
                ft.DataCell(ft.IconButton(icon=ft.Icons.DELETE, tooltip="Eliminar",
                                          on_click=lambda e, mesa=m: self.pedir_eliminar(mesa))),
            ])
            for m in self.ctx.mesas.obtener_todos()
        ]
        self.ctx.page.update()

    def agregar(self, e) -> None:
        try:
            mesa = Mesa(self.txt_nombre.value, self.txt_zona.value)
        except ValueError as err:
            mostrar_mensaje(self.mensaje, str(err), error=True)
            self.ctx.page.update()
            return
        if self.ctx.mesas.agregar(mesa):
            self.txt_nombre.value = ""
            mostrar_mensaje(self.mensaje, "Mesa agregada.")
        else:
            mostrar_mensaje(self.mensaje, self.ctx.mesas.ultimo_error, error=True)
        self.refrescar()

    def pedir_eliminar(self, mesa: Mesa) -> None:
        confirmar(self.ctx.page, f"Se eliminará la mesa: {mesa.nombre}", lambda: self.eliminar(mesa))

    def eliminar(self, mesa: Mesa) -> None:
        if self.ctx.mesas.eliminar(mesa.id):
            mostrar_mensaje(self.mensaje, "Mesa eliminada.")
        else:
            mostrar_mensaje(self.mensaje, self.ctx.mesas.ultimo_error, error=True)
        self.refrescar()


class SeccionOpciones:
    """Opciones que aparecen al personalizar el almuerzo (proteínas, principios, complementos)."""

    def __init__(self, ctx: Contexto) -> None:
        self.ctx = ctx
        self.dd_paso = tema.lista(
            label="Paso", width=220, value="proteina",
            options=[ft.dropdown.Option(key=k, text=v) for k, v in PASOS.items()],
        )
        self.txt_nombre = tema.campo(label="Nombre de la opción", width=240)
        self.mensaje = ft.Text("")
        self.tabla = ft.DataTable(columns=encabezados("Paso", "Opción", ""), rows=[])
        self.contenido = ft.Column(
            [ft.Row([self.dd_paso, self.txt_nombre, tema.boton("Agregar opción", self.agregar)], wrap=True),
             self.mensaje, con_scroll(self.tabla)],
            scroll=ft.ScrollMode.AUTO, expand=True,
        )

    def refrescar(self) -> None:
        self.tabla.rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(PASOS[o.paso])), ft.DataCell(ft.Text(o.nombre)),
                ft.DataCell(ft.IconButton(icon=ft.Icons.DELETE, tooltip="Eliminar",
                                          on_click=lambda e, op=o: self.pedir_eliminar(op))),
            ])
            for o in self.ctx.opciones.obtener_todos()
        ]
        self.ctx.page.update()

    def agregar(self, e) -> None:
        try:
            opcion = OpcionAlmuerzo(self.dd_paso.value, self.txt_nombre.value)
        except ValueError as err:
            mostrar_mensaje(self.mensaje, str(err), error=True)
            self.ctx.page.update()
            return
        if self.ctx.opciones.agregar(opcion):
            self.txt_nombre.value = ""
            mostrar_mensaje(self.mensaje, "Opción agregada.")
        else:
            mostrar_mensaje(self.mensaje, self.ctx.opciones.ultimo_error, error=True)
        self.refrescar()

    def pedir_eliminar(self, opcion: OpcionAlmuerzo) -> None:
        confirmar(self.ctx.page, f"Se eliminará la opción: {opcion.nombre}", lambda: self.eliminar(opcion))

    def eliminar(self, opcion: OpcionAlmuerzo) -> None:
        if self.ctx.opciones.eliminar(opcion.id):
            mostrar_mensaje(self.mensaje, "Opción eliminada.")
        else:
            mostrar_mensaje(self.mensaje, self.ctx.opciones.ultimo_error, error=True)
        self.refrescar()


class PanelConfig:
    """Configuracion del restaurante : mesas y opciones del almuerzo."""

    def __init__(self, ctx: Contexto) -> None:
        self.secciones = {
            "Mesas": SeccionMesas(ctx),
            "Opciones del almuerzo": SeccionOpciones(ctx),
        }
        self.actual = "Mesas"
        self.area = ft.Container(expand=True)
        botones = ft.Row(
            [tema.boton_suave(nombre, lambda e, n=nombre: self.mostrar(n)) for nombre in self.secciones],
            wrap=True,
        )
        self.contenido = ft.Column(
            [tema.titulo("Configuración"), botones, self.area], expand=True, spacing=12
        )

    def mostrar(self, nombre: str) -> None:
        self.actual = nombre
        seccion = self.secciones[nombre]
        self.area.content = seccion.contenido
        seccion.refrescar()

    def refrescar(self) -> None:
        self.mostrar(self.actual)
