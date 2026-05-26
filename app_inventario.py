from __future__ import annotations

import csv
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "inventario.db"
CSV_INVENTARIO = BASE_DIR / "INVENTARIO_BASE.csv"
CSV_MOVIMIENTOS = BASE_DIR / "MOVIMIENTOS.csv"
CSV_PROVEEDORES = BASE_DIR / "PROVEEDORES.csv"


@dataclass
class Producto:
    sku: str
    nombre: str
    categoria: str
    unidad: str
    stock_actual: int
    stock_minimo: int
    precio_compra: float
    precio_venta: float
    proveedor: str
    ubicacion: str
    fecha_ultima_entrada: str
    fecha_ultima_salida: str
    observaciones: str


def connect_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS productos (
            sku TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            categoria TEXT NOT NULL,
            unidad TEXT NOT NULL,
            stock_actual INTEGER NOT NULL,
            stock_minimo INTEGER NOT NULL,
            precio_compra REAL NOT NULL,
            precio_venta REAL NOT NULL,
            proveedor TEXT NOT NULL,
            ubicacion TEXT NOT NULL,
            fecha_ultima_entrada TEXT,
            fecha_ultima_salida TEXT,
            observaciones TEXT DEFAULT ''
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS proveedores (
            proveedor_id TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            contacto TEXT,
            telefono TEXT,
            correo TEXT,
            dias_credito INTEGER,
            tiempo_entrega_dias INTEGER,
            notas TEXT DEFAULT ''
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS movimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            tipo TEXT NOT NULL CHECK(tipo IN ('ENTRADA', 'SALIDA', 'AJUSTE')),
            sku TEXT NOT NULL,
            producto TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            costo_unitario REAL NOT NULL,
            precio_unitario REAL NOT NULL,
            motivo TEXT,
            responsable TEXT,
            FOREIGN KEY (sku) REFERENCES productos(sku)
        )
        """
    )
    conn.commit()


def table_is_empty(conn: sqlite3.Connection, table_name: str) -> bool:
    row = conn.execute(f"SELECT COUNT(*) AS total FROM {table_name}").fetchone()
    return bool(row and row["total"] == 0)


def parse_int(value: str, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def parse_float(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def seed_from_csv_if_empty(conn: sqlite3.Connection) -> None:
    if table_is_empty(conn, "productos") and CSV_INVENTARIO.exists():
        with CSV_INVENTARIO.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = [
                (
                    r.get("SKU", "").strip(),
                    r.get("Producto", "").strip(),
                    r.get("Categoria", "").strip(),
                    r.get("Unidad", "").strip(),
                    parse_int(r.get("Stock_Actual", "0")),
                    parse_int(r.get("Stock_Minimo", "0")),
                    parse_float(r.get("Precio_Compra", "0")),
                    parse_float(r.get("Precio_Venta", "0")),
                    r.get("Proveedor", "").strip(),
                    r.get("Ubicacion", "").strip(),
                    r.get("Fecha_Ultima_Entrada", "").strip(),
                    r.get("Fecha_Ultima_Salida", "").strip(),
                    r.get("Observaciones", "").strip(),
                )
                for r in reader
                if r.get("SKU")
            ]

        conn.executemany(
            """
            INSERT OR REPLACE INTO productos (
                sku, nombre, categoria, unidad, stock_actual, stock_minimo,
                precio_compra, precio_venta, proveedor, ubicacion,
                fecha_ultima_entrada, fecha_ultima_salida, observaciones
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )

    if table_is_empty(conn, "proveedores") and CSV_PROVEEDORES.exists():
        with CSV_PROVEEDORES.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = [
                (
                    r.get("Proveedor_ID", "").strip(),
                    r.get("Nombre", "").strip(),
                    r.get("Contacto", "").strip(),
                    r.get("Telefono", "").strip(),
                    r.get("Correo", "").strip(),
                    parse_int(r.get("Dias_Credito", "0")),
                    parse_int(r.get("Tiempo_Entrega_Dias", "0")),
                    r.get("Notas", "").strip(),
                )
                for r in reader
                if r.get("Proveedor_ID")
            ]

        conn.executemany(
            """
            INSERT OR REPLACE INTO proveedores (
                proveedor_id, nombre, contacto, telefono, correo,
                dias_credito, tiempo_entrega_dias, notas
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )

    if table_is_empty(conn, "movimientos") and CSV_MOVIMIENTOS.exists():
        with CSV_MOVIMIENTOS.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = [
                (
                    r.get("Fecha", "").strip(),
                    r.get("Tipo", "").strip().upper(),
                    r.get("SKU", "").strip(),
                    r.get("Producto", "").strip(),
                    parse_int(r.get("Cantidad", "0")),
                    parse_float(r.get("Costo_Unitario", "0")),
                    parse_float(r.get("Precio_Unitario", "0")),
                    r.get("Motivo", "").strip(),
                    r.get("Responsable", "").strip(),
                )
                for r in reader
                if r.get("SKU")
            ]

        conn.executemany(
            """
            INSERT INTO movimientos (
                fecha, tipo, sku, producto, cantidad, costo_unitario,
                precio_unitario, motivo, responsable
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )

    conn.commit()


def print_table(headers: list[str], rows: Iterable[Iterable[object]]) -> None:
    rows = [list(r) for r in rows]
    widths = [len(h) for h in headers]
    for row in rows:
        for i, col in enumerate(row):
            widths[i] = max(widths[i], len(str(col)))

    line = " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    sep = "-+-".join("-" * widths[i] for i in range(len(headers)))
    print(line)
    print(sep)
    for row in rows:
        print(" | ".join(str(col).ljust(widths[i]) for i, col in enumerate(row)))


def listar_productos(conn: sqlite3.Connection) -> None:
    rows = conn.execute(
        """
        SELECT sku, nombre, categoria, stock_actual, stock_minimo,
               precio_compra, precio_venta, proveedor
        FROM productos
        ORDER BY nombre
        """
    ).fetchall()

    if not rows:
        print("No hay productos cargados.")
        return

    data = []
    for r in rows:
        estado = "BAJO" if r["stock_actual"] <= r["stock_minimo"] else "OK"
        data.append(
            [
                r["sku"],
                r["nombre"],
                r["categoria"],
                r["stock_actual"],
                r["stock_minimo"],
                f"{r['precio_compra']:.2f}",
                f"{r['precio_venta']:.2f}",
                estado,
            ]
        )

    print_table(
        ["SKU", "Producto", "Categoria", "Stock", "Min", "Costo", "Venta", "Estado"],
        data,
    )


def registrar_producto(conn: sqlite3.Connection) -> None:
    print("\nNuevo producto")
    sku = input("SKU: ").strip().upper()
    if not sku:
        print("SKU requerido.")
        return

    exists = conn.execute("SELECT 1 FROM productos WHERE sku = ?", (sku,)).fetchone()
    if exists:
        print("Ese SKU ya existe.")
        return

    nombre = input("Nombre: ").strip()
    categoria = input("Categoria: ").strip() or "General"
    unidad = input("Unidad (pza, servicio, etc): ").strip() or "pza"
    stock_actual = parse_int(input("Stock inicial: ").strip(), 0)
    stock_minimo = parse_int(input("Stock minimo: ").strip(), 0)
    precio_compra = parse_float(input("Precio compra: ").strip(), 0.0)
    precio_venta = parse_float(input("Precio venta: ").strip(), 0.0)
    proveedor = input("Proveedor (ID): ").strip() or "INTERNO"
    ubicacion = input("Ubicacion: ").strip() or "Sin asignar"
    observaciones = input("Observaciones: ").strip()

    conn.execute(
        """
        INSERT INTO productos (
            sku, nombre, categoria, unidad, stock_actual, stock_minimo,
            precio_compra, precio_venta, proveedor, ubicacion,
            fecha_ultima_entrada, fecha_ultima_salida, observaciones
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '', '', ?)
        """,
        (
            sku,
            nombre,
            categoria,
            unidad,
            stock_actual,
            stock_minimo,
            precio_compra,
            precio_venta,
            proveedor,
            ubicacion,
            observaciones,
        ),
    )
    conn.commit()
    print("Producto registrado correctamente.")


def registrar_movimiento(conn: sqlite3.Connection) -> None:
    print("\nRegistrar movimiento")
    tipo = input("Tipo (ENTRADA/SALIDA/AJUSTE): ").strip().upper()
    if tipo not in {"ENTRADA", "SALIDA", "AJUSTE"}:
        print("Tipo invalido.")
        return

    sku = input("SKU: ").strip().upper()
    producto = conn.execute(
        "SELECT * FROM productos WHERE sku = ?", (sku,)
    ).fetchone()
    if not producto:
        print("SKU no encontrado.")
        return

    cantidad = parse_int(input("Cantidad: ").strip(), 0)
    if tipo in {"ENTRADA", "SALIDA"} and cantidad <= 0:
        print("La cantidad debe ser mayor que 0 para ENTRADA/SALIDA.")
        return

    if tipo == "SALIDA" and cantidad > producto["stock_actual"]:
        print("Stock insuficiente para esa salida.")
        return

    if tipo == "ENTRADA":
        delta = cantidad
    elif tipo == "SALIDA":
        delta = -cantidad
    else:
        # En ajuste, se permite cantidad positiva o negativa.
        delta = cantidad

    nuevo_stock = producto["stock_actual"] + delta
    if nuevo_stock < 0:
        print("El ajuste deja stock negativo. Operacion cancelada.")
        return

    fecha = datetime.now().strftime("%Y-%m-%d")
    costo_unitario = parse_float(input("Costo unitario: ").strip(), producto["precio_compra"])
    precio_unitario = parse_float(input("Precio unitario: ").strip(), producto["precio_venta"])
    motivo = input("Motivo: ").strip()
    responsable = input("Responsable: ").strip()

    conn.execute(
        """
        INSERT INTO movimientos (
            fecha, tipo, sku, producto, cantidad, costo_unitario,
            precio_unitario, motivo, responsable
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            fecha,
            tipo,
            sku,
            producto["nombre"],
            delta,
            costo_unitario,
            precio_unitario,
            motivo,
            responsable,
        ),
    )

    fecha_entrada = producto["fecha_ultima_entrada"]
    fecha_salida = producto["fecha_ultima_salida"]
    if delta > 0:
        fecha_entrada = fecha
    if delta < 0:
        fecha_salida = fecha

    conn.execute(
        """
        UPDATE productos
        SET stock_actual = ?,
            precio_compra = ?,
            precio_venta = ?,
            fecha_ultima_entrada = ?,
            fecha_ultima_salida = ?
        WHERE sku = ?
        """,
        (nuevo_stock, costo_unitario, precio_unitario, fecha_entrada, fecha_salida, sku),
    )

    conn.commit()
    print(f"Movimiento guardado. Nuevo stock de {sku}: {nuevo_stock}")


def reporte_stock_bajo(conn: sqlite3.Connection) -> None:
    rows = conn.execute(
        """
        SELECT sku, nombre, stock_actual, stock_minimo, proveedor
        FROM productos
        WHERE stock_actual <= stock_minimo
        ORDER BY (stock_minimo - stock_actual) DESC, nombre
        """
    ).fetchall()

    if not rows:
        print("No hay productos con stock bajo.")
        return

    print_table(
        ["SKU", "Producto", "Stock", "Minimo", "Proveedor"],
        [[r["sku"], r["nombre"], r["stock_actual"], r["stock_minimo"], r["proveedor"]] for r in rows],
    )


def resumen_financiero(conn: sqlite3.Connection) -> None:
    row = conn.execute(
        """
        SELECT
            COUNT(*) AS total_productos,
            COALESCE(SUM(stock_actual * precio_compra), 0) AS valor_inventario,
            COALESCE(SUM(stock_actual * (precio_venta - precio_compra)), 0) AS utilidad_potencial
        FROM productos
        """
    ).fetchone()

    print("\nResumen")
    print(f"Productos registrados: {row['total_productos']}")
    print(f"Valor de inventario (costo): {row['valor_inventario']:.2f}")
    print(f"Utilidad potencial: {row['utilidad_potencial']:.2f}")


def exportar_csv(conn: sqlite3.Connection) -> None:
    inventario_path = BASE_DIR / "INVENTARIO_BASE_actualizado.csv"
    movimientos_path = BASE_DIR / "MOVIMIENTOS_actualizado.csv"

    productos = conn.execute(
        """
        SELECT sku, nombre, categoria, unidad, stock_actual, stock_minimo,
               precio_compra, precio_venta, proveedor, ubicacion,
               fecha_ultima_entrada, fecha_ultima_salida, observaciones
        FROM productos
        ORDER BY sku
        """
    ).fetchall()

    with inventario_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "SKU",
                "Producto",
                "Categoria",
                "Unidad",
                "Stock_Actual",
                "Stock_Minimo",
                "Precio_Compra",
                "Precio_Venta",
                "Proveedor",
                "Ubicacion",
                "Fecha_Ultima_Entrada",
                "Fecha_Ultima_Salida",
                "Observaciones",
            ]
        )
        for p in productos:
            writer.writerow(list(p))

    movimientos = conn.execute(
        """
        SELECT fecha, tipo, sku, producto, cantidad, costo_unitario,
               precio_unitario, motivo, responsable
        FROM movimientos
        ORDER BY id
        """
    ).fetchall()

    with movimientos_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "Fecha",
                "Tipo",
                "SKU",
                "Producto",
                "Cantidad",
                "Costo_Unitario",
                "Precio_Unitario",
                "Motivo",
                "Responsable",
            ]
        )
        for m in movimientos:
            writer.writerow(list(m))

    print(f"Exportado: {inventario_path.name}")
    print(f"Exportado: {movimientos_path.name}")


def mostrar_menu() -> None:
    print("\n=== SISTEMA DE INVENTARIO - TIENDA UNIVERSITARIA ===")
    print("1. Listar productos")
    print("2. Registrar nuevo producto")
    print("3. Registrar movimiento (entrada/salida/ajuste)")
    print("4. Ver reporte de stock bajo")
    print("5. Ver resumen financiero")
    print("6. Exportar datos a CSV")
    print("7. Salir")


def main() -> None:
    conn = connect_db()
    init_db(conn)
    seed_from_csv_if_empty(conn)

    while True:
        mostrar_menu()
        opcion = input("Elige una opcion: ").strip()

        if opcion == "1":
            listar_productos(conn)
        elif opcion == "2":
            registrar_producto(conn)
        elif opcion == "3":
            registrar_movimiento(conn)
        elif opcion == "4":
            reporte_stock_bajo(conn)
        elif opcion == "5":
            resumen_financiero(conn)
        elif opcion == "6":
            exportar_csv(conn)
        elif opcion == "7":
            conn.close()
            print("Hasta luego.")
            break
        else:
            print("Opcion invalida.")


if __name__ == "__main__":
    main()
