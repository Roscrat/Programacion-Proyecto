"""Colores y piezas de diseno que se repiten en toda la aplicacion.
Si quieres cambiar el aspecto de la app, casi siempre basta con cambiar este archivo."""
import flet as ft

AZUL_OSCURO = "#12348E"
AZUL = "#2F55C8"
AZUL_CLARO = "#E3EAFB"
FONDO = "#EEF3FF"
BLANCO = "#FFFFFF"
TEXTO = "#16255C"
GRIS = "#5A6478"
VERDE = "#2E9E5B"
VERDE_CLARO = "#DDF3E6"
ROJO = "#C0392B"
ROJO_CLARO = "#FBE3E0"


def sombra() -> ft.BoxShadow:
    return ft.BoxShadow(
        blur_radius=14,
        color=ft.Colors.with_opacity(0.12, ft.Colors.BLACK),
        offset=ft.Offset(0, 4),
    )


def boton(texto, al_hacer_click, icono=None, color=AZUL, color_texto=BLANCO,
          ancho=None, compacto=False) -> ft.ElevatedButton:
    """Boton redondeado. Con compacto=True queda mas pequeno."""
    relleno = (
        ft.padding.symmetric(horizontal=14, vertical=8)
        if compacto
        else ft.padding.symmetric(horizontal=20, vertical=14)
    )
    return ft.ElevatedButton(
        text=texto,
        icon=icono,
        on_click=al_hacer_click,
        width=ancho,
        style=ft.ButtonStyle(
            bgcolor=color,
            color=color_texto,
            padding=relleno,
            shape=ft.RoundedRectangleBorder(radius=14),
        ),
    )


def boton_suave(texto, al_hacer_click, icono=None, ancho=None, compacto=False):
    """Boton de fondo azul claro, para acciones secundarias."""
    return boton(texto, al_hacer_click, icono, color=AZUL_CLARO, color_texto=AZUL,
                 ancho=ancho, compacto=compacto)


def campo(etiqueta=None, **opciones) -> ft.TextField:
    """Campo de texto con el estilo de la app. Acepta los mismos parametros que ft.TextField."""
    if etiqueta:
        opciones["label"] = etiqueta
    return ft.TextField(
        filled=True,
        bgcolor=BLANCO,
        border_radius=14,
        border_color=AZUL_CLARO,
        focused_border_color=AZUL,
        **opciones,
    )


def lista(etiqueta=None, **opciones) -> ft.Dropdown:
    """Lista desplegable con el estilo de la app."""
    if etiqueta:
        opciones["label"] = etiqueta
    return ft.Dropdown(
        filled=True,
        bgcolor=BLANCO,
        border_radius=14,
        border_color=AZUL_CLARO,
        **opciones,
    )


def titulo(texto: str, tamano: int = 24) -> ft.Text:
    return ft.Text(texto, size=tamano, weight=ft.FontWeight.BOLD, color=TEXTO)


def etiqueta_estado(texto: str, color_fondo: str, color_texto: str) -> ft.Container:
    """Pequena pastilla de color, por ejemplo 'Libre' o 'Ocupada'."""
    return ft.Container(
        content=ft.Text(texto, size=12, weight=ft.FontWeight.BOLD, color=color_texto),
        bgcolor=color_fondo,
        padding=ft.padding.symmetric(horizontal=12, vertical=4),
        border_radius=20,
    )
