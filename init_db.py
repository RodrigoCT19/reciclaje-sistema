# init_db.py
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "db" / "reciclaje.db"
DB_PATH.parent.mkdir(exist_ok=True)

DDL = """
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS residuos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT NOT NULL,
    proceso TEXT NOT NULL,
    lote TEXT,
    kg_totales REAL NOT NULL,
    kg_reciclados REAL NOT NULL,
    destino TEXT,
    responsable TEXT
);

CREATE TABLE IF NOT EXISTS costos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mes TEXT NOT NULL,
    ingresos REAL NOT NULL,
    costos_evitados REAL NOT NULL,
    costos_gestion REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS checklist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT NOT NULL,
    area TEXT,
    responsable TEXT,
    item1 TEXT, item2 TEXT, item3 TEXT, item4 TEXT, item5 TEXT,
    item6 TEXT, item7 TEXT, item8 TEXT, item9 TEXT, item10 TEXT
);
"""

def main():
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(DDL)
        conn.commit()
        print(f"Base creada/actualizada en: {DB_PATH.resolve()}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
