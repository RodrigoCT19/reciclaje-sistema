# migrate_add_periodo.py
"""Agrega columna 'periodo' a tablas existentes sin perder datos."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "db" / "reciclaje.db"

def add_column_if_missing(conn, table, coldef):
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table})")
    cols = [r[1] for r in cur.fetchall()]
    colname = coldef.split()[0]
    if colname not in cols:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {coldef}")
        print(f"[OK] Columna agregada: {table}.{colname}")
    else:
        print(f"[SKIP] {table}.{colname} ya existe")

def main():
    conn = sqlite3.connect(DB_PATH)
    try:
        add_column_if_missing(conn, "residuos",  "periodo TEXT DEFAULT 'PRE'")
        add_column_if_missing(conn, "costos",    "periodo TEXT DEFAULT 'PRE'")
        add_column_if_missing(conn, "checklist", "periodo TEXT DEFAULT 'PRE'")
        conn.commit()
        print("Migración aplicada correctamente.")
        print("TIP: Marca tus datos nuevos como 'POST' desde los formularios.")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
