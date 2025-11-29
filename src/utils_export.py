# src/utils_export.py
from io import BytesIO
from pathlib import Path

import pandas as pd

# Intentar importar FPDF desde fpdf / fpdf2
try:
    from fpdf import FPDF  # fpdf2 usa este mismo import
    HAS_FPDF = True
except ModuleNotFoundError:
    FPDF = None
    HAS_FPDF = False

# (si quieres, puedes usar esta ruta para otras cosas más adelante)
ASSETS_FONT = Path(__file__).resolve().parents[1] / "assets" / "fonts" / "DejaVuSans.ttf"


# -------------------- EXPORTACIÓN CSV --------------------
def to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Convierte un DataFrame a CSV (UTF-8 con BOM) para Excel."""
    return df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")


# -------------------- EXPORTACIÓN KPI A PDF --------------------
def kpi_pdf_bytes(titulo: str, periodo: str, porc, ahorro, cump) -> bytes:
    """
    Genera un PDF sencillo con los KPI.
    Si FPDF no está disponible (HAS_FPDF = False), devuelve un 'pseudo-PDF'
    en texto plano para que la app no reviente.
    """

    # --- MODO SIN FPDF: fallback seguro (por si falla en la nube) ---
    if not HAS_FPDF:
        # Texto simple que por lo menos se puede descargar y leer
        contenido = (
            f"{titulo}\n"
            f"Periodo: {periodo}\n\n"
            f"% Reciclados: {float(porc):.2f} %\n"
            f"Ahorro Neto (S/.): {float(ahorro):.2f}\n"
            f"% Cumplimiento: {float(cump):.2f} %\n"
            "\n*Nota:* La librería FPDF no está disponible en este entorno, "
            "por eso el archivo es un texto en lugar de un PDF con formato."
        )
        return contenido.encode("utf-8")

    # --- MODO CON FPDF: PDF normal usando fpdf2 ---
    pdf = FPDF()
    pdf.add_page()

    # Fuente básica (internas de FPDF)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, titulo, ln=True, align="C")

    pdf.set_font("Arial", size=11)
    pdf.cell(0, 8, f"Periodo: {periodo}", ln=True)

    pdf.ln(4)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(80, 10, "% Reciclados", 1, 0, "C")
    pdf.cell(60, 10, "Ahorro Neto (S/.)", 1, 0, "C")
    pdf.cell(50, 10, "% Cumplimiento", 1, 1, "C")

    pdf.set_font("Arial", size=12)
    pdf.cell(80, 10, f"{float(porc):.2f} %", 1, 0, "C")
    pdf.cell(60, 10, f"{float(ahorro):.2f}", 1, 0, "C")
    pdf.cell(50, 10, f"{float(cump):.2f} %", 1, 1, "C")

    pdf.ln(6)
    pdf.set_font("Arial", size=9)
    pie = "Reporte generado por el Sistema de Información Web de Reciclaje Interno (UCV – Rodrigo)."
    pdf.multi_cell(0, 6, pie)

    # Entregar bytes
    pdf_bytes = pdf.output(dest="S").encode("latin1")
    return pdf_bytes
