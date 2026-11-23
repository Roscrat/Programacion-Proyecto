import sqlite3
from typing import Optional


# Estructura de la base de datos. Se ejecuta cada vez que arranca la app,
# pero CREATE TABLE IF NOT EXISTS no hace nada si la tabla ya existe.
ESQUEMA = """
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT UNIQUE NOT NULL COLLATE NOCASE,
    clave TEXT NOT NULL,
    rol TEXT NOT NULL CHECK(rol IN ('admin', 'cajero'))
);

CREATE TABLE IF NOT EXISTS mesas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL COLLATE NOCASE,
    zona TEXT NOT NULL,
    estado TEXT NOT NULL DEFAULT 'libre' CHECK(estado IN ('libre', 'ocupada'))
);

CREATE TABLE IF NOT EXISTS categorias_gasto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS gastos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    descripcion TEXT NOT NULL,
    monto REAL NOT NULL CHECK(monto >= 0),
    fecha TEXT NOT NULL,
    id_categoria INTEGER NOT NULL,
    FOREIGN KEY (id_categoria) REFERENCES categorias_gasto(id)
);

CREATE TABLE IF NOT EXISTS platos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL COLLATE NOCASE,
    precio REAL NOT NULL CHECK(precio >= 0),
    tipo TEXT NOT NULL DEFAULT 'otro' CHECK(tipo IN ('almuerzo', 'bebida', 'otro'))
);

CREATE TABLE IF NOT EXISTS opciones_almuerzo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paso TEXT NOT NULL CHECK(paso IN ('proteina', 'principio', 'complemento')),
    nombre TEXT NOT NULL,
    UNIQUE (paso, nombre)
);

CREATE TABLE IF NOT EXISTS pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT NOT NULL,
    id_mesa INTEGER NOT NULL,
    id_usuario INTEGER NOT NULL,
    cliente TEXT NOT NULL DEFAULT '',
    observaciones TEXT NOT NULL DEFAULT '',
    estado TEXT NOT NULL DEFAULT 'abierto' CHECK(estado IN ('abierto', 'pagado')),
    metodo_pago TEXT NOT NULL DEFAULT '',
    FOREIGN KEY (id_mesa) REFERENCES mesas(id),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
);

CREATE TABLE IF NOT EXISTS detalles_pedido (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_pedido INTEGER NOT NULL,
    id_plato INTEGER NOT NULL,
    cantidad INTEGER NOT NULL CHECK(cantidad > 0),
    precio_unitario REAL NOT NULL CHECK(precio_unitario >= 0),
    notas TEXT NOT NULL DEFAULT '',
    FOREIGN KEY (id_pedido) REFERENCES pedidos(id) ON DELETE CASCADE,
    FOREIGN KEY (id_plato) REFERENCES platos(id)
);

CREATE TABLE IF NOT EXISTS aportes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    descripcion TEXT NOT NULL,
    monto REAL NOT NULL CHECK(monto >= 0),
    fecha TEXT NOT NULL
);
"""

# Datos de ejemplo. Solo se cargan la primera vez que se crea la base de datos,
# para que si se borra algo no vuelva a aparecer al reiniciar.
DATOS_INICIALES = """
INSERT INTO categorias_gasto (nombre) VALUES
    ('Alimentos'), ('Gas'), ('Servicios'), ('Personal'), ('Otros');

INSERT INTO mesas (nombre, zona) VALUES
    ('Mesa 1', 'Salón Principal'), ('Mesa 2', 'Salón Principal'),
    ('Mesa 3', 'Salón Principal'), ('Mesa 4', 'Salón Principal'),
    ('Mesa 5', 'Terraza'), ('Mesa 6', 'Terraza');

INSERT INTO platos (nombre, precio, tipo) VALUES
    ('Almuerzo', 15000, 'almuerzo'),
    ('Limonada', 5000, 'bebida'),
    ('Coca Cola Litro', 9000, 'bebida'),
    ('Coca Cola Personal', 5000, 'bebida'),
    ('Postobon Personal', 5000, 'bebida'),
    ('Postobon Litro', 9000, 'bebida');

INSERT INTO opciones_almuerzo (paso, nombre) VALUES
    ('proteina', 'Res'), ('proteina', 'Cerdo'), ('proteina', 'Pollo'),
    ('proteina', 'Pescado'), ('proteina', 'Sin proteína'),
    ('principio', 'Frijol'), ('principio', 'Garbanzo'), ('principio', 'Lentejas'),
    ('principio', 'Pepino'), ('principio', 'Verduras'), ('principio', 'Espagueti'),
    ('complemento', 'Sopa'), ('complemento', 'Huevo');
"""


class DatabaseManager:
    """Abre la conexion, entrega un cursor y al salir decide entre commit y rollback."""

    def __init__(self, db_path: str = "la_buena_mesa.db") -> None:
        self.db_path: str = db_path
        self.__connection: Optional[sqlite3.Connection] = None
        self.__cursor: Optional[sqlite3.Cursor] = None

    def __enter__(self) -> sqlite3.Cursor:
        self.__connection = sqlite3.connect(self.db_path)
        # Sin esta linea SQLite ignora las llaves foraneas
        self.__connection.execute("PRAGMA foreign_keys = ON;")
        self.__cursor = self.__connection.cursor()
        return self.__cursor

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[object],
    ) -> bool:
        if self.__connection:
            if exc_type is not None:
                self.__connection.rollback()
            else:
                self.__connection.commit()
            if self.__cursor:
                self.__cursor.close()
            self.__connection.close()
        # No se silencian las excepciones, las maneja quien llama
        return False

    def crear_tablas(self) -> None:
        with self as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type = 'table' AND name = 'platos';"
            )
            es_nueva = cursor.fetchone()[0] == 0
            cursor.executescript(ESQUEMA)
            if es_nueva:
                cursor.executescript(DATOS_INICIALES)
