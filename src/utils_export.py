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

# src/utils_export.py
import pandas as pd

# Intentar importar FPDF (de fpdf2)
try:
    from fpdf import FPDF
    HAS_FPDF = True
except ImportError:
    HAS_FPDF = False


def kpi_pdf_bytes(title: str,
                  periodo: str,
                  porc_reciclados: float,
                  ahorro_neto: float,
                  porc_cumplimiento: float) -> bytes | None:
    """Genera el PDF de KPIs. Si no hay FPDF, devuelve None."""
    if not HAS_FPDF:
        return None

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, title, ln=True)

    pdf.set_font("Helvetica", "", 12)
    pdf.ln(5)
    pdf.cell(0, 8, f"Periodo: {periodo}", ln=True)
    pdf.cell(0, 8, f"% Reciclados: {porc_reciclados} %", ln=True)
    pdf.cell(0, 8, f"Ahorro Neto (S/.): {ahorro_neto}", ln=True)
    pdf.cell(0, 8, f"% Cumplimiento: {porc_cumplimiento} %", ln=True)

    # Devolver bytes del PDF
    pdf_bytes = pdf.output(dest="S").encode("latin-1")
    return pdf_bytes


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Convierte un DataFrame a CSV en bytes (UTF-8)."""
    return df.to_csv(index=False).encode("utf-8")
