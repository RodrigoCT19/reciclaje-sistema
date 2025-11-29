# seed_demo.py
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "db" / "reciclaje.db"
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Residuos (3 filas)
cur.executemany(
    "INSERT INTO residuos (fecha, proceso, lote, kg_totales, kg_reciclados, destino, responsable) VALUES (?, ?, ?, ?, ?, ?, ?)",
    [
        ("2025-01-10", "Corte", "L-001", 5.0, 2.0, "Reciclaje", "Oper1"),
        ("2025-01-11", "Soldadura", "L-002", 3.0, 1.5, "Venta", "Oper2"),
        ("2025-01-12", "Ensamble", "L-003", 4.0, 0.0, "Reúso", "Oper3"),
    ],
)

# Costos (1 fila)
cur.execute(
    "INSERT INTO costos (mes, ingresos, costos_evitados, costos_gestion) VALUES (?, ?, ?, ?)",
    ("2025-01", 350.0, 200.0, 80.0),
)

# Checklist (1 fila con 7 Sí)
cur.execute(
    "INSERT INTO checklist (fecha, area, responsable, item1,item2,item3,item4,item5,item6,item7,item8,item9,item10) "
    "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
    ("2025-01-12", "Corte", "Supervisor",
     "Sí","Sí","Sí","Sí","Sí","Sí","Sí","No","No","No")
)

conn.commit()
conn.close()
print("Datos de demo insertados ✅")
