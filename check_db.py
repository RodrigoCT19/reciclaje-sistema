# check_db.py
import sqlite3
from pathlib import Path
DB_PATH = Path(__file__).parent / "db" / "reciclaje.db"
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("Tablas:", cur.fetchall())
cur.execute("SELECT COUNT(*) FROM residuos")
print("Filas en residuos:", cur.fetchone()[0])
cur.execute("SELECT COUNT(*) FROM costos")
print("Filas en costos:", cur.fetchone()[0])
cur.execute("SELECT COUNT(*) FROM checklist")
print("Filas en checklist:", cur.fetchone()[0])
conn.close()
