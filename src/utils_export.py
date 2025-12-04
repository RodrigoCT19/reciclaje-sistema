# src/utils_export.py
from io import BytesIO
from fpdf import FPDF
import pandas as pd

# ---- CSV genérico para todos tus listados ----
def to_csv_bytes(df: pd.DataFrame) -> bytes:
    """
    Convierte un DataFrame a CSV (UTF-8 con BOM) listo para descargar.
    """
    return df.to_csv(index=False, sep=";").encode("utf-8")

# ---- PDF para el KPI del dashboard ----
def kpi_pdf_bytes(titulo: str, periodo: str, porc, ahorro, cump) -> bytes:
    """
    Genera un PDF simple con el resumen de KPI y devuelve los bytes.
    """
    pdf = FPDF()
    pdf.add_page()

    # Título
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, titulo, ln=True, align="C")

    # Subtítulo
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"Periodo: {periodo}", ln=True)
    pdf.ln(4)

    # Tabla de KPI
    pdf.set_font("Arial", "B", 12)
    pdf.cell(80, 10, "% Reciclados", 1, 0, "C")
    pdf.cell(60, 10, "Ahorro Neto (S/.)", 1, 0, "C")
    pdf.cell(50, 10, "% Cumplimiento", 1, 1, "C")

    pdf.set_font("Arial", "", 12)
    pdf.cell(80, 10, f"{float(porc):.2f} %", 1, 0, "C")
    pdf.cell(60, 10, f"{float(ahorro):.2f}", 1, 0, "C")
    pdf.cell(50, 10, f"{float(cump):.2f} %", 1, 1, "C")

    pdf.ln(6)
    pdf.set_font("Arial", "", 9)

    # Importante: SOLO caracteres ASCII para evitar errores de Unicode en fpdf
    pie = (
        "Reporte generado por el Sistema de Informacion Web "
        "de Reciclaje Interno (UCV - Rodrigo)."
    )
    pdf.multi_cell(0, 6, pie)

    # Obtener contenido como string o bytearray según la versión de fpdf2
    data = pdf.output(dest="S")

    if isinstance(data, str):
        # Versiones antiguas devuelven str
        return data.encode("latin1")
    else:
        # Versiones nuevas devuelven bytearray/bytes
        return bytes(data)

try:
    from fpdf import FPDF
    HAS_FPDF = True
except Exception:
    FPDF = None
    HAS_FPDF = False
