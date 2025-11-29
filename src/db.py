# --- al inicio del archivo:
import sqlite3
from pathlib import Path
import pandas as pd
from contextlib import contextmanager

DB_PATH = Path(__file__).resolve().parent.parent / "db" / "reciclaje.db"

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

@contextmanager
def db_cursor():
    conn = get_connection()
    try:
        yield conn.cursor()
        conn.commit()
    finally:
        conn.close()

# ---------- CRUD RESIDUOS ----------
def insert_residuo(fecha, proceso, lote, kg_totales, kg_reciclados, destino, responsable, periodo):
    with db_cursor() as cur:
        cur.execute("""
            INSERT INTO residuos (fecha, proceso, lote, kg_totales, kg_reciclados, destino, responsable, periodo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (fecha, proceso, lote, kg_totales, kg_reciclados, destino, responsable, periodo))

def list_residuos(periodo=None, limit=50, with_id=False):
    sql = f"SELECT {'id, ' if with_id else ''}fecha, proceso, lote, kg_totales, kg_reciclados, destino, responsable, periodo FROM residuos"
    params = []
    if periodo:
        sql += " WHERE periodo = ?"
        params.append(periodo)
    sql += " ORDER BY id DESC LIMIT ?"
    params.append(limit)
    with db_cursor() as cur:
        cur.execute(sql, tuple(params))
        return cur.fetchall()

def get_residuo_by_id(rid):
    with db_cursor() as cur:
        cur.execute("""
            SELECT id, fecha, proceso, lote, kg_totales, kg_reciclados, destino, responsable, periodo
            FROM residuos WHERE id = ?
        """, (rid,))
        return cur.fetchone()

def update_residuo(rid, fecha, proceso, lote, kg_totales, kg_reciclados, destino, responsable, periodo):
    with db_cursor() as cur:
        cur.execute("""
            UPDATE residuos
            SET fecha=?, proceso=?, lote=?, kg_totales=?, kg_reciclados=?, destino=?, responsable=?, periodo=?
            WHERE id=?
        """, (fecha, proceso, lote, kg_totales, kg_reciclados, destino, responsable, periodo, rid))

def delete_residuo(rid):
    with db_cursor() as cur:
        cur.execute("DELETE FROM residuos WHERE id=?", (rid,))

# ---------- CRUD COSTOS ----------
def insert_costos(mes, ingresos, evitados, gestion, periodo):
    with db_cursor() as cur:
        cur.execute("""
            INSERT INTO costos (mes, ingresos, costos_evitados, costos_gestion, periodo)
            VALUES (?, ?, ?, ?, ?)
        """, (mes, ingresos, evitados, gestion, periodo))

def list_costos(periodo=None, limit=50, with_id=False):
    sql = f"SELECT {'id, ' if with_id else ''}mes, ingresos, costos_evitados, costos_gestion, periodo FROM costos"
    params = []
    if periodo:
        sql += " WHERE periodo = ?"
        params.append(periodo)
    sql += " ORDER BY id DESC LIMIT ?"
    params.append(limit)
    with db_cursor() as cur:
        cur.execute(sql, tuple(params))
        return cur.fetchall()

def get_costo_by_id(cid):
    with db_cursor() as cur:
        cur.execute("""
            SELECT id, mes, ingresos, costos_evitados, costos_gestion, periodo
            FROM costos WHERE id=?
        """, (cid,))
        return cur.fetchone()

def update_costos(cid, mes, ingresos, evitados, gestion, periodo):
    with db_cursor() as cur:
        cur.execute("""
            UPDATE costos
            SET mes=?, ingresos=?, costos_evitados=?, costos_gestion=?, periodo=?
            WHERE id=?
        """, (mes, ingresos, evitados, gestion, periodo, cid))

def delete_costos(cid):
    with db_cursor() as cur:
        cur.execute("DELETE FROM costos WHERE id=?", (cid,))

# ---------- CRUD CHECKLIST ----------
def insert_checklist(fecha, area, responsable, items, periodo):
    with db_cursor() as cur:
        cur.execute("""
            INSERT INTO checklist (fecha, area, responsable, item1,item2,item3,item4,item5,item6,item7,item8,item9,item10, periodo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (fecha, area, responsable, *items, periodo))

def list_checklist(periodo=None, limit=50, with_id=False):
    sql = f"SELECT {'id, ' if with_id else ''}fecha, area, responsable, item1,item2,item3,item4,item5,item6,item7,item8,item9,item10, periodo FROM checklist"
    params = []
    if periodo:
        sql += " WHERE periodo = ?"
        params.append(periodo)
    sql += " ORDER BY id DESC LIMIT ?"
    params.append(limit)
    with db_cursor() as cur:
        cur.execute(sql, tuple(params))
        return cur.fetchall()

def get_checklist_by_id(cid):
    with db_cursor() as cur:
        cur.execute("""
            SELECT id, fecha, area, responsable, item1,item2,item3,item4,item5,item6,item7,item8,item9,item10, periodo
            FROM checklist WHERE id=?
        """, (cid,))
        return cur.fetchone()

def update_checklist(cid, fecha, area, responsable, items, periodo):
    with db_cursor() as cur:
        cur.execute("""
            UPDATE checklist
            SET fecha=?, area=?, responsable=?, item1=?,item2=?,item3=?,item4=?,item5=?,item6=?,item7=?,item8=?,item9=?,item10=?, periodo=?
            WHERE id=?
        """, (fecha, area, responsable, *items, periodo, cid))

def delete_checklist(cid):
    with db_cursor() as cur:
        cur.execute("DELETE FROM checklist WHERE id=?", (cid,))

# ---------- DATAFRAMES PARA EXPORTAR ----------
def df_residuos(periodo: str | None = None) -> pd.DataFrame:
    cols = ["fecha","proceso","lote","kg_totales","kg_reciclados","destino","responsable","periodo"]
    q = "SELECT " + ",".join(cols) + " FROM residuos"
    params = ()
    if periodo in ("PRE","POST"):
        q += " WHERE periodo=?"
        params = (periodo,)
    q += " ORDER BY fecha"
    with get_connection() as c:
        return pd.read_sql_query(q, c, params=params)

def df_costos(periodo: str | None = None) -> pd.DataFrame:
    cols = ["mes","ingresos","costos_evitados","costos_gestion","periodo"]
    q = "SELECT " + ",".join(cols) + " FROM costos"
    params = ()
    if periodo in ("PRE","POST"):
        q += " WHERE periodo=?"
        params = (periodo,)
    q += " ORDER BY mes"
    with get_connection() as c:
        return pd.read_sql_query(q, c, params=params)

def df_checklist(periodo: str | None = None) -> pd.DataFrame:
    cols = ["fecha","area","responsable","item1","item2","item3","item4","item5","item6","item7","item8","item9","item10","periodo"]
    q = "SELECT " + ",".join(cols) + " FROM checklist"
    params = ()
    if periodo in ("PRE","POST"):
        q += " WHERE periodo=?"
        params = (periodo,)
    q += " ORDER BY fecha"
    with get_connection() as c:
        return pd.read_sql_query(q, c, params=params)

def df_residuos(periodo: str | None = None) -> pd.DataFrame:
    cols = ["fecha","proceso","lote","kg_totales","kg_reciclados","destino","responsable","periodo"]
    q = "SELECT " + ",".join(cols) + " FROM residuos"
    params = ()
    if periodo in ("PRE","POST"):
        q += " WHERE periodo=?"
        params = (periodo,)
    q += " ORDER BY fecha"
    with get_connection() as c:
        return pd.read_sql_query(q, c, params=params)

def df_costos(periodo: str | None = None) -> pd.DataFrame:
    cols = ["mes","ingresos","costos_evitados","costos_gestion","periodo"]
    q = "SELECT " + ",".join(cols) + " FROM costos"
    params = ()
    if periodo in ("PRE","POST"):
        q += " WHERE periodo=?"
        params = (periodo,)
    q += " ORDER BY mes"
    with get_connection() as c:
        return pd.read_sql_query(q, c, params=params)

def df_checklist(periodo: str | None = None) -> pd.DataFrame:
    cols = ["fecha","area","responsable",
            "item1","item2","item3","item4","item5","item6","item7","item8","item9","item10",
            "periodo"]
    q = "SELECT " + ",".join(cols) + " FROM checklist"
    params = ()
    if periodo in ("PRE","POST"):
        q += " WHERE periodo=?"
        params = (periodo,)
    q += " ORDER BY fecha"
    with get_connection() as c:
        return pd.read_sql_query(q, c, params=params)