import flet as ft

from domain.plato import Plato
from ui import tema
from ui.contexto import Contexto

# (clave del paso, nombre corto, titulo, subtitulo, permite elegir varias)
PASOS = [
    ("proteina", "Proteína", "Seleccionar proteína", "Selecciona una opción para tu almuerzo.", False),
    ("principio", "Principio", "Seleccionar principio", "Elige el acompañamiento de tu almuerzo.", False),
    ("complemento", "Complementos", "Selecciona los complementos", "Elige los complementos que deseas incluir.", True),
]


class DialogoPersonalizar:
    """Ventana de 3 pasos para armar un almuerzo. Al terminar entrega un texto
    con lo elegido, por ejemplo 'Res, Frijol, Sopa', que queda como nota del producto."""

    def __init__(self, ctx: Contexto, plato: Plato, al_agregar) -> None:
        self.ctx = ctx
        self.plato = plato
        self.al_agregar = al_agregar
        self.paso = 0  # 0, 1 o 2

        # Opciones de cada paso, leidas de la base de datos
        self.opciones = {
            clave: [o.nombre for o in ctx.opciones.obtener_por_paso(clave)]
            for clave, _, _, _, _ in PASOS
        }
        # Lo que la persona ha elegido en cada paso. En los pasos de una sola
        # opcion se deja la primera marcada, como en el diseno.
        self.elegidas = {
            clave: (self.opciones[clave][:1] if not varias else [])
            for clave, _, _, _, varias in PASOS
        }

        self.cuerpo = ft.Container(width=600)
        self.dialogo = ft.AlertDialog(
            modal=True,
            content=self.cuerpo,
            shape=ft.RoundedRectangleBorder(radius=22),
        )

    def abrir(self) -> None:
        self._pintar()
        self.ctx.page.open(self.dialogo)

    def cerrar(self, e=None) -> None:
        self.ctx.page.close(self.dialogo)

    # ------------------------------------------------------------ dibujo
    def _pintar(self) -> None:
        clave, _, titulo, subtitulo, varias = PASOS[self.paso]

        encabezado = ft.Row(
            [
                ft.Icon(ft.Icons.RESTAURANT, color=tema.AZUL, size=34),
                ft.Column(
                    [
                        ft.Text(f"Personalizar {self.plato.nombre}", size=20,
                                weight=ft.FontWeight.BOLD, color=tema.TEXTO),
                        ft.Text(f"Paso {self.paso + 1} de 3", size=13, color=tema.GRIS),
                    ],
                    spacing=0,
                    expand=True,
                ),
                ft.IconButton(icon=ft.Icons.CLOSE, on_click=self.cerrar),
            ]
        )

        opciones = ft.Column(
            [self._fila_opcion(clave, nombre, varias) for nombre in self.opciones[clave]]
            or [ft.Text("No hay opciones configuradas para este paso.", color=tema.GRIS)],
            spacing=8,
            height=250,
            scroll=ft.ScrollMode.AUTO,
        )

        self.cuerpo.content = ft.Column(
            [
                encabezado,
                self._indicador_pasos(),
                ft.Text(titulo, size=22, weight=ft.FontWeight.BOLD, color=tema.TEXTO),
                ft.Text(subtitulo, color=tema.GRIS),
                opciones,
                self._botones(),
            ],
            spacing=14,
            tight=True,
        )

    def _indicador_pasos(self) -> ft.Row:
        """Los tres circulos de arriba (1, 2, 3) con el paso actual resaltado."""
        items = []
        for i, (_, nombre, _, _, _) in enumerate(PASOS):
            activo = i == self.paso
            circulo = ft.Container(
                width=30, height=30, border_radius=15,
                bgcolor=tema.AZUL if activo else tema.AZUL_CLARO,
                alignment=ft.alignment.center,
                content=ft.Text(str(i + 1), weight=ft.FontWeight.BOLD,
                                color=tema.BLANCO if activo else tema.AZUL),
            )
            items.append(
                ft.Column(
                    [circulo, ft.Text(nombre, size=12,
                                      weight=ft.FontWeight.BOLD if activo else ft.FontWeight.NORMAL,
                                      color=tema.TEXTO if activo else tema.GRIS)],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=4,
                )
            )
        return ft.Row(items, alignment=ft.MainAxisAlignment.SPACE_EVENLY)

    def _fila_opcion(self, clave: str, nombre: str, varias: bool) -> ft.Container:
        marcada = nombre in self.elegidas[clave]
        if varias:
            icono = ft.Icons.CHECK_BOX if marcada else ft.Icons.CHECK_BOX_OUTLINE_BLANK
        else:
            icono = ft.Icons.RADIO_BUTTON_CHECKED if marcada else ft.Icons.RADIO_BUTTON_UNCHECKED
        return ft.Container(
            padding=ft.padding.symmetric(horizontal=14, vertical=10),
            border_radius=12,
            bgcolor=tema.AZUL_CLARO if marcada else "#F4F6FC",
            border=ft.border.all(1, tema.AZUL if marcada else tema.AZUL_CLARO),
            ink=True,
            on_click=lambda e: self.elegir(clave, nombre, varias),
            content=ft.Row(
                [ft.Icon(icono, color=tema.AZUL),
                 ft.Text(nombre, weight=ft.FontWeight.BOLD, color=tema.TEXTO)],
            ),
        )

    def _botones(self) -> ft.Row:
        if self.paso == 0:
            izquierda = tema.boton_suave("Cancelar", self.cerrar, icono=ft.Icons.CLOSE)
        else:
            izquierda = tema.boton_suave("Anterior", self.anterior, icono=ft.Icons.ARROW_BACK)

        if self.paso < 2:
            derecha = tema.boton("Siguiente", self.siguiente, icono=ft.Icons.ARROW_FORWARD)
        else:
            derecha = tema.boton("Agregar al pedido", self.terminar,
                                 icono=ft.Icons.SHOPPING_CART, color=tema.VERDE)
        return ft.Row([izquierda, derecha], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    # ----------------------------------------------------------- acciones
    def elegir(self, clave: str, nombre: str, varias: bool) -> None:
        if varias:
            # En los complementos se puede marcar y desmarcar cada opcion
            if nombre in self.elegidas[clave]:
                self.elegidas[clave].remove(nombre)
            else:
                self.elegidas[clave].append(nombre)
        else:
            self.elegidas[clave] = [nombre]
        self._pintar()
        self.ctx.page.update()

    def siguiente(self, e) -> None:
        self.paso += 1
        self._pintar()
        self.ctx.page.update()

    def anterior(self, e) -> None:
        self.paso -= 1
        self._pintar()
        self.ctx.page.update()

    def terminar(self, e) -> None:
        todas = []
        for clave, _, _, _, _ in PASOS:
            todas.extend(self.elegidas[clave])
        notas = ", ".join(todas)
        self.cerrar()
        self.al_agregar(notas)
