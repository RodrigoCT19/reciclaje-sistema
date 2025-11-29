# src/utils_export.py
from pathlib import Path
from fpdf import FPDF
import pandas as pd

# --- Localizar la fuente Unicode (DejaVuSans.ttf) ---
# Probamos dos ubicaciones:
#   a) dentro de src/assets/fonts/
#   b) en la raíz del proyecto assets/fonts/
HERE = Path(__file__).resolve().parent
CANDIDATES = [
    HERE / "assets" / "fonts" / "DejaVuSans.ttf",
    HERE.parent / "assets" / "fonts" / "DejaVuSans.ttf",
]
ASSETS_FONT = next((p for p in CANDIDATES if p.exists()), None)


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    """CSV con UTF-8 BOM para que Excel abra bien tildes y columnas separadas."""
    return df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")


def kpi_pdf_bytes(titulo: str, periodo: str, porc, ahorro, cump) -> bytes:
    """Genera PDF de KPI en bytes usando fuente Unicode."""
    pdf = FPDF()
    pdf.add_page()

    # Cargar fuente Unicode si existe
    if ASSETS_FONT is not None:
        pdf.add_font("DejaVu", "", ASSETS_FONT.as_posix(), uni=True)
        pdf.add_font("DejaVu", "B", ASSETS_FONT.as_posix(), uni=True)
        family_b = ("DejaVu", "B")
        family   = ("DejaVu", "")
    else:
        # Fallback: core fonts (sin Unicode). Evita caracteres especiales si llegas aquí.
        family_b = ("Arial", "B")
        family   = ("Arial", "")

    # Título
    pdf.set_font(*family_b, size=14)
    pdf.cell(0, 10, titulo, ln=True, align="C")

    # Subtítulo
    pdf.set_font(*family, size=11)
    pdf.cell(0, 8, f"Periodo: {periodo}", ln=True)
    pdf.ln(4)

    # Encabezados de tabla
    pdf.set_font(*family_b, size=12)
    pdf.cell(80, 10, "% Reciclados",    1, 0, "C")
    pdf.cell(60, 10, "Ahorro Neto (S/.)", 1, 0, "C")
    pdf.cell(50, 10, "% Cumplimiento",  1, 1, "C")

    # Valores
    pdf.set_font(*family, size=12)
    pdf.cell(80, 10, f"{float(porc):.2f} %", 1, 0, "C")
    pdf.cell(60, 10, f"{float(ahorro):.2f}", 1, 0, "C")
    pdf.cell(50, 10, f"{float(cump):.2f} %", 1, 1, "C")

    pdf.ln(6)
    pdf.set_font(*family, size=9)
    pie = "Reporte generado por el Sistema de Información Web de Reciclaje Interno (UCV – Rodrigo)."
    pdf.multi_cell(0, 6, pie)

    # fpdf2 -> bytearray; convertir a bytes para Streamlit
    raw = pdf.output(dest="S")  # <- bytearray
    return bytes(raw)
