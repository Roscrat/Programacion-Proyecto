import flet as ft


def moneda(valor: float) -> str:
    """Formato con punto de miles, por ejemplo $85.000."""
    return "$" + f"{valor:,.0f}".replace(",", ".")


def mostrar_mensaje(control: ft.Text, texto: str, error: bool = False) -> None:
    control.value = texto
    control.color = ft.Colors.RED_700 if error else ft.Colors.GREEN_700


def confirmar(page: ft.Page, texto: str, al_aceptar) -> None:
    """Abre un cuadro de dialogo y ejecuta al_aceptar solo si se confirma."""

    def cerrar(e) -> None:
        page.close(dialogo)

    def aceptar(e) -> None:
        page.close(dialogo)
        al_aceptar()

    dialogo = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirmar"),
        content=ft.Text(texto),
        actions=[
            ft.TextButton("Cancelar", on_click=cerrar),
            ft.TextButton("Eliminar", on_click=aceptar),
        ],
    )
    page.open(dialogo)


def encabezados(*titulos: str) -> list[ft.DataColumn]:
    return [ft.DataColumn(ft.Text(t, weight=ft.FontWeight.BOLD)) for t in titulos]


def con_scroll(tabla: ft.DataTable) -> ft.Row:
    """Evita que una tabla ancha se corte en pantallas pequenas."""
    return ft.Row([tabla], scroll=ft.ScrollMode.AUTO)
