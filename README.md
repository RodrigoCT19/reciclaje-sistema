# Sistema de Reciclaje Interno (Streamlit + SQLite)

## Requisitos
- Python 3.11+
- Visual Studio Code
- (Opcional) DB Browser for SQLite

## Instalación rápida
```bash
# 1) Crear y activar entorno
python -m venv .venv
# Windows
.venv\Scripts\Activate
# macOS/Linux
# source .venv/bin/activate

# 2) Instalar dependencias
pip install -r requirements.txt

# 3) Inicializar base de datos
python init_db.py

# 4) Ejecutar app
streamlit run app.py
```

## Estructura
- `app.py`: App principal (navegación, formularios y vistas).
- `init_db.py`: Crea la base SQLite y tablas.
- `src/db.py`: Utilidades para conexión y operaciones con SQLite.
- `src/kpi.py`: Funciones para calcular KPI.
- `check_db.py`: Verificación rápida de tablas y conteos.
- `db/reciclaje.db`: Base de datos local (se crea tras ejecutar `init_db.py`).

## KPI
- % Reciclados = Σ kg_reciclados / Σ kg_totales
- Ahorro neto (S/.) = Σ ingresos + Σ costos_evitados − Σ costos_gestion
- % Cumplimiento = (ítems "Sí" / total ítems) × 100
