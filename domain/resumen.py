class ResumenCaja:
    """Junta los totales para saber cuanta plata tiene el restaurante."""

    def __init__(self, aportes: float, cobrado: float, por_cobrar: float, gastos: float) -> None:
        self.aportes: float = aportes
        self.cobrado: float = cobrado
        self.por_cobrar: float = por_cobrar
        self.gastos: float = gastos

    @property
    def saldo(self) -> float:
        return self.aportes + self.cobrado - self.gastos

    def __str__(self) -> str:
        return f"Saldo actual: ${self.saldo:,.0f}"

    def __repr__(self) -> str:
        return (
            f"ResumenCaja(aportes={self.aportes}, cobrado={self.cobrado}, "
            f"por_cobrar={self.por_cobrar}, gastos={self.gastos})"
        )
