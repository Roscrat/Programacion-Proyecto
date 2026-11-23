from datetime import date

DIAS_SEMANA = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]


def validar_fecha(texto: str) -> str:
    limpio = (texto or "").strip()
    try:
        date.fromisoformat(limpio)
    except ValueError:
        raise ValueError("La fecha debe tener el formato AAAA-MM-DD.")
    return limpio


def validar_texto(texto: str, nombre: str) -> str:
    limpio = (texto or "").strip()
    if not limpio:
        raise ValueError(f"{nombre} no puede estar vacio.")
    return limpio


def leer_numero(texto: str, nombre: str = "El valor") -> float:
    """Convierte texto a numero. Los puntos se toman como separador de miles
    y la coma como decimal, por eso 12.500 es doce mil quinientos."""
    limpio = (texto or "").strip().replace("$", "").replace(".", "").replace(",", ".")
    try:
        return float(limpio)
    except ValueError:
        raise ValueError(f"{nombre} debe ser un numero.")


def leer_entero(texto: str, nombre: str = "El valor") -> int:
    numero = leer_numero(texto, nombre)
    if numero != int(numero):
        raise ValueError(f"{nombre} debe ser un numero entero.")
    return int(numero)
