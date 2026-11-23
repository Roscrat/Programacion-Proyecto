from datetime import date
from typing import Optional

from domain.validaciones import DIAS_SEMANA, validar_fecha


class DetallePedido:
    """Una linea del pedido: cuantas unidades de un producto, a que precio y con que notas."""

    def __init__(
        self,
        id_plato: int,
        nombre_plato: str,
        cantidad: int,
        precio_unitario: float,
        notas: str = "",
    ) -> None:
        self.id_plato: int = id_plato
        self.nombre_plato: str = nombre_plato
        self.precio_unitario: float = float(precio_unitario)
        self.notas: str = notas
        self.__cantidad: int = 1
        self.cantidad = cantidad

    @property
    def cantidad(self) -> int:
        return self.__cantidad

    @cantidad.setter
    def cantidad(self, valor: int) -> None:
        if valor <= 0:
            raise ValueError("La cantidad debe ser mayor que cero.")
        self.__cantidad = int(valor)

    @property
    def subtotal(self) -> float:
        return self.cantidad * self.precio_unitario

    @classmethod
    def desde_tupla(cls, registro: tuple) -> "DetallePedido":
        """Espera (id_plato, nombre_plato, cantidad, precio_unitario, notas)."""
        return cls(registro[0], registro[1], registro[2], registro[3], registro[4])

    def __str__(self) -> str:
        texto = f"{self.cantidad} {self.nombre_plato}"
        return f"{texto} ({self.notas})" if self.notas else texto

    def __repr__(self) -> str:
        return (
            f"DetallePedido(plato={self.nombre_plato!r}, cantidad={self.cantidad}, "
            f"precio_unitario={self.precio_unitario}, notas={self.notas!r})"
        )


class Pedido:
    """Lo que consume una mesa. Esta abierto hasta que se cobra y pasa a pagado."""

    def __init__(
        self,
        fecha: str,
        id_mesa: int,
        id_usuario: int,
        nombre_mesa: str = "",
        cliente: str = "",
        observaciones: str = "",
        estado: str = "abierto",
        metodo_pago: str = "",
        id_pedido: Optional[int] = None,
    ) -> None:
        self.id: Optional[int] = id_pedido
        self.id_mesa: int = id_mesa
        self.id_usuario: int = id_usuario
        self.nombre_mesa: str = nombre_mesa
        self.cliente: str = cliente
        self.observaciones: str = observaciones
        self.estado: str = estado
        self.metodo_pago: str = metodo_pago
        self.__fecha: str = validar_fecha(fecha)
        self.__detalles: list[DetallePedido] = []

    @property
    def fecha(self) -> str:
        return self.__fecha

    @property
    def detalles(self) -> list[DetallePedido]:
        return list(self.__detalles)

    @property
    def pagado(self) -> bool:
        return self.estado == "pagado"

    @property
    def total(self) -> float:
        return sum(d.subtotal for d in self.__detalles)

    @property
    def cantidad_items(self) -> int:
        return sum(d.cantidad for d in self.__detalles)

    @property
    def dia_semana(self) -> str:
        return DIAS_SEMANA[date.fromisoformat(self.__fecha).weekday()]

    def agregar_detalle(self, detalle: DetallePedido) -> None:
        # Si ya hay una linea igual (mismo producto y mismas notas) se suman las unidades
        for existente in self.__detalles:
            if existente.id_plato == detalle.id_plato and existente.notas == detalle.notas:
                existente.cantidad += detalle.cantidad
                return
        self.__detalles.append(detalle)

    def quitar_detalle(self, detalle: DetallePedido) -> None:
        self.__detalles = [d for d in self.__detalles if d is not detalle]

    @classmethod
    def desde_tupla(cls, registro: tuple) -> "Pedido":
        """Espera (id, fecha, id_mesa, nombre_mesa, cliente, observaciones, estado,
        metodo_pago, id_usuario). Los detalles se agregan aparte."""
        return cls(
            id_pedido=registro[0],
            fecha=registro[1],
            id_mesa=registro[2],
            nombre_mesa=registro[3],
            cliente=registro[4],
            observaciones=registro[5],
            estado=registro[6],
            metodo_pago=registro[7],
            id_usuario=registro[8],
        )

    def __len__(self) -> int:
        return len(self.__detalles)

    def __str__(self) -> str:
        productos = ", ".join(str(d) for d in self.__detalles)
        return f"{self.dia_semana} {self.fecha} - {self.nombre_mesa}: {productos}"

    def __repr__(self) -> str:
        return (
            f"Pedido(id={self.id}, fecha='{self.fecha}', mesa='{self.nombre_mesa}', "
            f"items={len(self)}, estado='{self.estado}')"
        )

    def __eq__(self, otro: object) -> bool:
        if not isinstance(otro, Pedido):
            return NotImplemented
        return self.id is not None and self.id == otro.id
