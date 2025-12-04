import pandas as pd

def to_csv_bytes(df: pd.DataFrame) -> bytes:
    """
    Convierte un DataFrame a CSV en bytes (UTF-8 con BOM)
    para que Excel lo abra en columnas separadas.
    """
    csv_str = df.to_csv(index=False)
    return csv_str.encode("utf-8-sig")
