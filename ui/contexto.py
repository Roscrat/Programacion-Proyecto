"""Objeto que comparten todas las pantallas.

En vez de pasar diez parametros a cada panel, se les pasa un solo objeto (ctx)
con la pagina, los repositorios, el usuario que inicio sesion y algunas funciones
para moverse entre pantallas."""
from typing import Callable, Optional

import flet as ft

from data.aporte_dao import AporteDAO
from data.categoria_dao import CategoriaDAO
from data.database_manager import DatabaseManager
from data.gasto_dao import GastoDAO
from data.mesa_repository import MesaRepository
from data.opcion_repository import OpcionRepository
from data.pedido_repository import PedidoRepository
from data.plato_repository import PlatoRepository
from data.usuario_repository import UsuarioRepository
from domain.usuario import Usuario
from ui.tema import ROJO, VERDE


class Contexto:
    def __init__(self, page: ft.Page, db: DatabaseManager) -> None:
        self.page: ft.Page = page

        # Capa de datos
        self.usuarios = UsuarioRepository(db)
        self.mesas = MesaRepository(db)
        self.platos = PlatoRepository(db)
        self.opciones = OpcionRepository(db)
        self.pedidos = PedidoRepository(db)
        self.gastos = GastoDAO(db)
        self.categorias = CategoriaDAO(db)
        self.aportes = AporteDAO(db)

        # Estado de la sesion
        self.usuario: Optional[Usuario] = None
        self.id_mesa_activa: Optional[int] = None

        # Los asigna AppView: sirven para cambiar de pantalla 
        self.ir_a: Callable[[str], None] = lambda nombre: None

    def aviso(self, texto: str, error: bool = False) -> None:
        """Muestra un mensaje corto en la parte de abajo de la ventana."""
        barra = ft.SnackBar(
            content=ft.Text(texto, color=ft.Colors.WHITE),
            bgcolor=ROJO if error else VERDE,
        )
        self.page.open(barra)
