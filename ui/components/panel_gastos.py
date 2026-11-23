from datetime import date

import flet as ft

from ui import tema

from data.categoria_dao import CategoriaDAO
from data.gasto_dao import GastoDAO
from domain.gasto import Gasto
from domain.validaciones import leer_numero
from ui.components.utilidades import (
    confirmar,
    con_scroll,
    encabezados,
    moneda,
    mostrar_mensaje,
)


class PanelGastos:
    def __init__(self, page: ft.Page, gasto_dao: GastoDAO, categoria_dao: CategoriaDAO, al_cambiar) -> None:
        self.page = page
        self.gasto_dao = gasto_dao
        self.categoria_dao = categoria_dao
        self.al_cambiar = al_cambiar
        self.id_editando = None

        self.txt_descripcion = tema.campo(label="Descripcion", width=320)
        self.txt_monto = tema.campo(label="Monto", width=150)
        self.txt_fecha = tema.campo(label="Fecha (AAAA-MM-DD)", width=190)
        self.dd_categoria = tema.lista(label="Categoria", width=200)
        self.btn_guardar = tema.boton("Agregar gasto", self.guardar)
        self.btn_cancelar = tema.boton_suave("Cancelar edicion", self.cancelar)
        self.mensaje = ft.Text("")
        self.tabla = ft.DataTable(
            columns=encabezados("Fecha", "Descripcion", "Categoria", "Monto", "Acciones"),
            rows=[],
        )

        self.contenido = ft.Column(
            [
                ft.Text("Gastos del restaurante", size=22, weight=ft.FontWeight.BOLD),
                ft.Row(
                    [self.txt_descripcion, self.txt_monto, self.txt_fecha, self.dd_categoria],
                    wrap=True,
                ),
                ft.Row([self.btn_guardar, self.btn_cancelar]),
                self.mensaje,
                con_scroll(self.tabla),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        self._limpiar_formulario()

    def refrescar(self) -> None:
        self._cargar_categorias()
        self._cargar_tabla()
        self.page.update()

    def _cargar_categorias(self) -> None:
        seleccionada = self.dd_categoria.value
        categorias = self.categoria_dao.obtener_todos()
        self.dd_categoria.options = [
            ft.dropdown.Option(key=str(c.id), text=c.nombre) for c in categorias
        ]
        if not seleccionada and categorias:
            self.dd_categoria.value = str(categorias[0].id)

    def _cargar_tabla(self) -> None:
        self.tabla.rows = []
        for gasto in self.gasto_dao.obtener_todos():
            self.tabla.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(gasto.fecha)),
                        ft.DataCell(ft.Text(gasto.descripcion)),
                        ft.DataCell(ft.Text(gasto.nombre_categoria)),
                        ft.DataCell(ft.Text(moneda(gasto.monto))),
                        ft.DataCell(
                            ft.Row(
                                [
                                    ft.IconButton(
                                        icon=ft.Icons.EDIT,
                                        tooltip="Editar",
                                        on_click=lambda e, g=gasto: self.editar(g),
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE,
                                        tooltip="Eliminar",
                                        on_click=lambda e, g=gasto: self.pedir_eliminar(g),
                                    ),
                                ]
                            )
                        ),
                    ]
                )
            )

    def _limpiar_formulario(self) -> None:
        self.id_editando = None
        self.txt_descripcion.value = ""
        self.txt_monto.value = ""
        self.txt_fecha.value = date.today().isoformat()
        self.btn_guardar.text = "Agregar gasto"
        self.btn_cancelar.visible = False

    def guardar(self, e) -> None:
        try:
            if not self.dd_categoria.value:
                raise ValueError("Selecciona una categoria.")
            gasto = Gasto(
                descripcion=self.txt_descripcion.value,
                monto=leer_numero(self.txt_monto.value, "El monto"),
                fecha=self.txt_fecha.value,
                id_categoria=int(self.dd_categoria.value),
                id_gasto=self.id_editando,
            )
        except ValueError as err:
            mostrar_mensaje(self.mensaje, str(err), error=True)
            self.page.update()
            return

        if self.id_editando is None:
            ok = self.gasto_dao.agregar(gasto)
        else:
            ok = self.gasto_dao.actualizar(gasto)

        if ok:
            self._limpiar_formulario()
            mostrar_mensaje(self.mensaje, "Gasto guardado.")
            self.al_cambiar()
        else:
            mostrar_mensaje(self.mensaje, self.gasto_dao.ultimo_error, error=True)
        self.refrescar()

    def editar(self, gasto: Gasto) -> None:
        self.id_editando = gasto.id
        self.txt_descripcion.value = gasto.descripcion
        self.txt_monto.value = str(int(gasto.monto))
        self.txt_fecha.value = gasto.fecha
        self.dd_categoria.value = str(gasto.id_categoria)
        self.btn_guardar.text = "Guardar cambios"
        self.btn_cancelar.visible = True
        mostrar_mensaje(self.mensaje, "Editando gasto.")
        self.page.update()

    def cancelar(self, e) -> None:
        self._limpiar_formulario()
        mostrar_mensaje(self.mensaje, "")
        self.page.update()

    def pedir_eliminar(self, gasto: Gasto) -> None:
        confirmar(self.page, f"Se eliminara el gasto: {gasto}", lambda: self.eliminar(gasto))

    def eliminar(self, gasto: Gasto) -> None:
        if self.gasto_dao.eliminar(gasto.id):
            mostrar_mensaje(self.mensaje, "Gasto eliminado.")
            self.al_cambiar()
        else:
            mostrar_mensaje(self.mensaje, self.gasto_dao.ultimo_error, error=True)
        self.refrescar()
