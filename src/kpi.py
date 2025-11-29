# src/kpi.py
from .db import get_connection

def get_kpis(periodo=None):
    conn = get_connection()
    cur = conn.cursor()

    # % reciclados
    if periodo:
        cur.execute("SELECT COALESCE(SUM(kg_reciclados),0), COALESCE(SUM(kg_totales),0) FROM residuos WHERE periodo=?", (periodo,))
    else:
        cur.execute("SELECT COALESCE(SUM(kg_reciclados),0), COALESCE(SUM(kg_totales),0) FROM residuos")
    sum_rec, sum_tot = cur.fetchone()
    porc_reciclados = (sum_rec / sum_tot * 100.0) if sum_tot else 0.0

    # ahorro neto
    if periodo:
        cur.execute("SELECT COALESCE(SUM(ingresos + costos_evitados - costos_gestion),0) FROM costos WHERE periodo=?", (periodo,))
    else:
        cur.execute("SELECT COALESCE(SUM(ingresos + costos_evitados - costos_gestion),0) FROM costos")
    ahorro_neto = cur.fetchone()[0] or 0.0

    # % cumplimiento
    if periodo:
        cur.execute("SELECT item1,item2,item3,item4,item5,item6,item7,item8,item9,item10 FROM checklist WHERE periodo=?", (periodo,))
    else:
        cur.execute("SELECT item1,item2,item3,item4,item5,item6,item7,item8,item9,item10 FROM checklist")
    rows = cur.fetchall()
    if rows:
        total = 0
        for r in rows:
            sies = sum(1 for v in r if (v or '').strip().lower() == 'sí')
            total += (sies / 10) * 100.0
        porc_cumplimiento = total / len(rows)
    else:
        porc_cumplimiento = 0.0

    conn.close()
    return {
        "porc_reciclados": round(porc_reciclados, 2),
        "ahorro_neto": round(ahorro_neto, 2),
        "porc_cumplimiento": round(porc_cumplimiento, 2),
    }
