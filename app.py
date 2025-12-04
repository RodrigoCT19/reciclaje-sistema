# app.py
import streamlit as st
from datetime import date
import pandas as pd

from src import db
from src.kpi import get_kpis
from src.utils_export import kpi_pdf_bytes, to_csv_bytes


st.set_page_config(page_title="Sistema de Reciclaje Interno", layout="wide")

# ---------- helpers dataframe desde tu db ----------
COLS_RES = ["fecha","proceso","lote","kg_totales","kg_reciclados","destino","responsable","periodo"]
COLS_COS = ["mes","ingresos","costos_evitados","costos_gestion","periodo"]
COLS_CHK = ["fecha","area","responsable","item1","item2","item3","item4","item5","item6","item7","item8","item9","item10","periodo"]

def df_residuos(periodo: str | None = None, limit: int = 1000) -> pd.DataFrame:
    rows = db.list_residuos(periodo=periodo, limit=limit, with_id=False)
    return pd.DataFrame(rows, columns=COLS_RES)

def df_costos(periodo: str | None = None, limit: int = 1000) -> pd.DataFrame:
    rows = db.list_costos(periodo=periodo, limit=limit, with_id=False)
    return pd.DataFrame(rows, columns=COLS_COS)

def df_checklist(periodo: str | None = None, limit: int = 1000) -> pd.DataFrame:
    rows = db.list_checklist(periodo=periodo, limit=limit, with_id=False)
    return pd.DataFrame(rows, columns=COLS_CHK)

# ---------- UI ----------
st.sidebar.title("Menú")
page = st.sidebar.radio("Ir a:", ["Dashboard", "Registro de Residuos", "Registro de Costos", "Checklist de Cumplimiento"])
st.sidebar.info("Proyecto: Sistema de Recilaje")

def periodo_selectbox(label="Periodo"):
    return st.selectbox(label, ["PRE", "POST"])

# =================== DASHBOARD ===================
# =================== DASHBOARD ===================
if page == "Dashboard":
    st.title("Dashboard de KPIs")

    # Filtro de periodo
    periodo_sel = st.selectbox("Ver periodo", ["(Todos)", "PRE", "POST"])
    periodo_arg = None if periodo_sel == "(Todos)" else periodo_sel

    # KPI globales
    kpis = get_kpis(periodo=periodo_arg)

    c1, c2, c3 = st.columns(3)
    c1.metric("% Reciclados", f"{kpis['porc_reciclados']} %")
    c2.metric("Ahorro Neto (S/.)", f"{kpis['ahorro_neto']}")
    c3.metric("% Cumplimiento", f"{kpis['porc_cumplimiento']} %")

    st.caption(
        "Tip: llena registros por periodo y usa el selector para comparar PRE vs POST."
    )

    # ---------- Exportar KPI (PDF / CSV) ----------
    st.markdown("### Exportar indicadores")
    colA, colB = st.columns(2)

    with colA:
        pdf_bytes = kpi_pdf_bytes(
            "Reporte de KPI",
            "TODOS" if periodo_sel == "(Todos)" else periodo_sel,
            kpis["porc_reciclados"],
            kpis["ahorro_neto"],
            kpis["porc_cumplimiento"],
        )
        st.download_button(
            "⬇️ Exportar KPI (PDF)",
            data=pdf_bytes,
            file_name=f"kpi_{'todos' if periodo_sel == '(Todos)' else periodo_sel}.pdf",
            mime="application/pdf",
        )

    with colB:
        df_kpi = pd.DataFrame(
            [
                {
                    "periodo": "TODOS" if periodo_sel == "(Todos)" else periodo_sel,
                    "% reciclados": float(kpis["porc_reciclados"]),
                    "ahorro_neto": float(kpis["ahorro_neto"]),
                    "% cumplimiento": float(kpis["porc_cumplimiento"]),
                }
            ]
        )
        st.download_button(
            "⬇️ Exportar KPI (CSV)",
            data=to_csv_bytes(df_kpi),
            file_name=f"kpi_{'todos' if periodo_sel == '(Todos)' else periodo_sel}.csv",
            mime="text/csv",
        )

    st.markdown("---")
    st.markdown("### Visualizaciones por periodo")

    # Preparamos los 3 dataframes una sola vez
    df_r = df_residuos(periodo_arg)
    df_c = df_costos(periodo_arg)
    df_x = df_checklist(periodo_arg)

    tab1, tab2, tab3 = st.tabs(
        [
            "% Reciclados por mes",
            "Ahorro neto mensual (S/.)",
            "% Cumplimiento en checklist",
        ]
    )

    # ---------- Gráfico 1: tendencia % reciclado por mes ----------
    with tab1:
        if not df_r.empty:
            df_r["fecha"] = pd.to_datetime(df_r["fecha"])
            grp = df_r.groupby(pd.Grouper(key="fecha", freq="MS")).agg(
                kg_tot=("kg_totales", "sum"),
                kg_rec=("kg_reciclados", "sum"),
            )
            grp["% reciclado"] = grp.apply(
                lambda r: 0.0 if r["kg_tot"] == 0 else (r["kg_rec"] / r["kg_tot"]) * 100,
                axis=1,
            )
            st.line_chart(
                grp["% reciclado"],
                height=260,
            )
            st.caption(
                "Muestra la evolución mensual del porcentaje de residuos reciclados "
                "respecto al total generado."
            )
        else:
            st.info("No hay datos de residuos para graficar.")

    # ---------- Gráfico 2: ahorro neto por mes ----------
    with tab2:
        if not df_c.empty:
            df_c["mes"] = pd.to_datetime(df_c["mes"] + "-01", errors="coerce")
            df_c["ahorro_neto"] = (
                df_c["ingresos"] + df_c["costos_evitados"] - df_c["costos_gestion"]
            )
            ahorro = df_c.groupby(pd.Grouper(key="mes", freq="MS"))["ahorro_neto"].sum()
            st.bar_chart(
                ahorro,
                height=260,
            )
            st.caption(
                "Suma mensual del ahorro neto considerando ingresos por venta, "
                "costos evitados y costos de gestión."
            )
        else:
            st.info("No hay datos de costos para graficar.")

    # ---------- Gráfico 3: % cumplimiento checklist ----------
    with tab3:
        if not df_x.empty:
            df_x["fecha"] = pd.to_datetime(df_x["fecha"])
            items = [f"item{i}" for i in range(1, 11)]
            # convertir Sí/No a 1/0
            df_x[items] = df_x[items].applymap(
                lambda v: 1 if str(v).strip().lower() in ("si", "sí", "1", "true") else 0
            )
            df_x["% cumplimiento"] = (df_x[items].sum(axis=1) / 10) * 100
            cump = df_x.groupby(pd.Grouper(key="fecha", freq="MS"))[
                "% cumplimiento"
            ].mean()
            st.line_chart(
                cump,
                height=260,
            )
            st.caption(
                "Promedio mensual del porcentaje de ítems cumplidos en el checklist."
            )
        else:
            st.info("No hay datos de checklist para graficar.")


# =================== RESIDUOS ===================
if page == "Registro de Residuos":
    st.title("Registro de Residuos")
    tab1, tab2, tab3 = st.tabs(["Registrar", "Administrar (Editar/Eliminar)", "Exportar"])

    # ---- Registrar ----
    with tab1:
        with st.form("form_residuos", clear_on_submit=True):
            fecha = st.date_input("Fecha", date.today())
            proceso = st.selectbox("Proceso", ["Corte", "Soldadura", "Ensamble"])
            lote = st.text_input("Lote")
            kg_totales = st.number_input("Kg Totales", min_value=0.0, step=0.1)
            kg_reciclados = st.number_input("Kg Reciclados", min_value=0.0, step=0.1)
            destino = st.selectbox("Destino", ["Reúso", "Reciclaje", "Venta"])
            responsable = st.text_input("Responsable")
            periodo = periodo_selectbox()
            submitted = st.form_submit_button("Guardar")
        if submitted:
            if kg_reciclados > kg_totales:
                st.error("Los Kg reciclados no pueden ser mayores que los Kg totales.")
            else:
                db.insert_residuo(str(fecha), proceso, lote, float(kg_totales), float(kg_reciclados), destino, responsable, periodo)
                st.success("Registro guardado ✅")


        st.subheader("Últimos registros")
        cant = st.selectbox("Mostrar registros", [20, 50, 100, 200, 500, 1000], index=1)  # por defecto 50
        rows = db.list_residuos(limit=cant, with_id=False)
        st.dataframe(pd.DataFrame(rows, columns=COLS_RES), use_container_width=True, hide_index=True)


        

    # ---- Administrar ----
    with tab2:
        st.subheader("Editar o eliminar")
        rows = db.list_residuos(limit=100, with_id=True)
        if not rows:
            st.info("No hay registros.")
        else:
            opciones = {f"ID {r[0]} • {r[1]} • {r[2]} • {r[3]}kg": r[0] for r in rows}
            rid = st.selectbox("Selecciona un registro", list(opciones.keys()))
            sel_id = opciones[rid]
            rec = db.get_residuo_by_id(sel_id)
            if rec:
                _id, fecha, proceso, lote, kg_totales, kg_reciclados, destino, responsable, periodo = rec
                from datetime import date as _d
                with st.form("edit_residuo"):
                    fecha = st.date_input("Fecha", _d.fromisoformat(fecha))
                    proceso = st.selectbox("Proceso", ["Corte", "Soldadura", "Ensamble"], index=["Corte","Soldadura","Ensamble"].index(proceso))
                    lote = st.text_input("Lote", value=lote or "")
                    kg_totales = st.number_input("Kg Totales", min_value=0.0, step=0.1, value=float(kg_totales))
                    kg_reciclados = st.number_input("Kg Reciclados", min_value=0.0, step=0.1, value=float(kg_reciclados))
                    destino = st.selectbox("Destino", ["Reúso","Reciclaje","Venta"], index=["Reúso","Reciclaje","Venta"].index(destino))
                    responsable = st.text_input("Responsable", value=responsable or "")
                    periodo = st.selectbox("Periodo", ["PRE","POST"], index=["PRE","POST"].index(periodo or "PRE"))
                    c1, c2 = st.columns(2)
                    with c1:
                        upd = st.form_submit_button("Actualizar ✅")
                    with c2:
                        delb = st.form_submit_button("Eliminar 🗑️")
                if upd:
                    if kg_reciclados > kg_totales:
                        st.error("Los Kg reciclados no pueden ser mayores que los Kg totales.")
                    else:
                        db.update_residuo(sel_id, str(fecha), proceso, lote, float(kg_totales), float(kg_reciclados), destino, responsable, periodo)
                        st.success("Registro actualizado")
                if delb:
                    db.delete_residuo(sel_id)
                    st.success("Registro eliminado. Refresca la pestaña.")

    # ---- Exportar ----
    with tab3:
        st.subheader("Exportar Registros de Residuos")
        filtro = st.selectbox("Filtrar por periodo", ["(Todos)","PRE","POST"])
        per = None if filtro == "(Todos)" else filtro
        df = df_residuos(per)
        st.dataframe(df, use_container_width=True)
        st.download_button(
            "⬇️ Exportar Residuos (CSV)",
            data=to_csv_bytes(df),
            file_name=f"residuos_{'todos' if per is None else per}.csv",
            mime="text/csv",
        )

# =================== COSTOS ===================
if page == "Registro de Costos":
    st.title("Registro de Costos de Valorización")
    tab1, tab2, tab3 = st.tabs(["Registrar", "Administrar (Editar/Eliminar)", "Exportar"])

    # ---- Registrar ----
    with tab1:
        with st.form("form_costos", clear_on_submit=True):
            mes = st.text_input("Mes (YYYY-MM)")
            ingresos = st.number_input("Ingresos por venta (S/.)", min_value=0.0, step=0.1)
            evitados = st.number_input("Costos evitados (S/.)", min_value=0.0, step=0.1)
            gestion = st.number_input("Costos de gestión (S/.)", min_value=0.0, step=0.1)
            periodo = periodo_selectbox()
            submitted = st.form_submit_button("Guardar")
        if submitted:
            db.insert_costos(mes, float(ingresos), float(evitados), float(gestion), periodo)
            st.success("Registro de costos guardado ✅")

        st.subheader("Últimos registros")
        rows = db.list_costos(limit=20, with_id=False)
        st.dataframe(pd.DataFrame(rows, columns=COLS_COS), use_container_width=True, hide_index=True)

    # ---- Administrar ----
    with tab2:
        st.subheader("Editar o eliminar")
        rows = db.list_costos(limit=100, with_id=True)
        if not rows:
            st.info("No hay registros.")
        else:
            opciones = {f"ID {r[0]} • {r[1]}": r[0] for r in rows}
            cid = st.selectbox("Selecciona un registro", list(opciones.keys()))
            sel_id = opciones[cid]
            rec = db.get_costo_by_id(sel_id)
            if rec:
                _id, mes, ingresos, evitados, gestion, periodo = rec
                with st.form("edit_costos"):
                    mes = st.text_input("Mes (YYYY-MM)", value=mes or "")
                    ingresos = st.number_input("Ingresos por venta (S/.)", min_value=0.0, step=0.1, value=float(ingresos))
                    evitados = st.number_input("Costos evitados (S/.)", min_value=0.0, step=0.1, value=float(evitados))
                    gestion = st.number_input("Costos de gestión (S/.)", min_value=0.0, step=0.1, value=float(gestion))
                    periodo = st.selectbox("Periodo", ["PRE","POST"], index=["PRE","POST"].index(periodo or "PRE"))
                    c1, c2 = st.columns(2)
                    with c1:
                        upd = st.form_submit_button("Actualizar ✅")
                    with c2:
                        delb = st.form_submit_button("Eliminar 🗑️")
                if upd:
                    db.update_costos(sel_id, mes, float(ingresos), float(evitados), float(gestion), periodo)
                    st.success("Registro actualizado")
                if delb:
                    db.delete_costos(sel_id)
                    st.success("Registro eliminado. Refresca la pestaña.")

    # ---- Exportar ----
    with tab3:
        st.subheader("Exportar Registros de Costos")
        filtro = st.selectbox("Filtrar por periodo", ["(Todos)","PRE","POST"])
        per = None if filtro == "(Todos)" else filtro
        df = df_costos(per)
        st.dataframe(df, use_container_width=True)
        st.download_button(
            "⬇️ Exportar Costos (CSV)",
            data=to_csv_bytes(df),
            file_name=f"costos_{'todos' if per is None else per}.csv",
            mime="text/csv",
        )

# =================== CHECKLIST ===================
if page == "Checklist de Cumplimiento":
    st.title("Checklist de Cumplimiento (10 ítems)")
    tab1, tab2, tab3 = st.tabs(["Registrar", "Administrar (Editar/Eliminar)", "Exportar"])
    opciones_SN = ["Sí","No"]

    # ---- Registrar ----
    with tab1:
        with st.form("form_checklist", clear_on_submit=True):
            fecha = st.date_input("Fecha", date.today())
            area = st.selectbox("Área/Proceso", ["Corte","Soldadura","Ensamble","Almacén"])
            responsable = st.text_input("Responsable")
            st.markdown("Marca **Sí** o **No** para cada ítem:")
            items = [st.selectbox(f"Ítem {i}", opciones_SN, key=f"i{i}") for i in range(1,11)]
            periodo = periodo_selectbox()
            submitted = st.form_submit_button("Guardar")
        if submitted:
            db.insert_checklist(str(fecha), area, responsable, items, periodo)
            st.success("Checklist guardado ✅")

        st.subheader("Últimos registros")
        rows = db.list_checklist(limit=20, with_id=False)
        st.dataframe(pd.DataFrame(rows, columns=COLS_CHK), use_container_width=True, hide_index=True)

    # ---- Administrar ----
    with tab2:
        st.subheader("Editar o eliminar")
        rows = db.list_checklist(limit=100, with_id=True)
        if not rows:
            st.info("No hay registros.")
        else:
            opciones = {f"ID {r[0]} • {r[1]} • {r[2]}": r[0] for r in rows}
            cid = st.selectbox("Selecciona un registro", list(opciones.keys()))
            sel_id = opciones[cid]
            rec = db.get_checklist_by_id(sel_id)
            if rec:
                (_id, fecha, area, responsable, *items, periodo) = rec
                from datetime import date as _d
                with st.form("edit_checklist"):
                    fecha = st.date_input("Fecha", _d.fromisoformat(fecha))
                    area = st.selectbox("Área/Proceso", ["Corte","Soldadura","Ensamble","Almacén"], index=["Corte","Soldadura","Ensamble","Almacén"].index(area))
                    responsable = st.text_input("Responsable", value=responsable or "")
                    st.markdown("Marca **Sí** o **No** para cada ítem:")
                    items = [st.selectbox(
                        f"Ítem {i}", opciones_SN, key=f"e{i}",
                        index=0 if str(items[i-1]).strip().lower() in ("si","sí") else 1
                    ) for i in range(1,11)]
                    periodo = st.selectbox("Periodo", ["PRE","POST"], index=["PRE","POST"].index(periodo or "PRE"))
                    c1, c2 = st.columns(2)
                    with c1:
                        upd = st.form_submit_button("Actualizar ✅")
                    with c2:
                        delb = st.form_submit_button("Eliminar 🗑️")
                if upd:
                    db.update_checklist(sel_id, str(fecha), area, responsable, items, periodo)
                    st.success("Registro actualizado")
                if delb:
                    db.delete_checklist(sel_id)
                    st.success("Registro eliminado. Refresca la pestaña.")

    # ---- Exportar ----
    with tab3:
        st.subheader("Exportar Registros de Checklist")
        filtro = st.selectbox("Filtrar por periodo", ["(Todos)","PRE","POST"])
        per = None if filtro == "(Todos)" else filtro
        df = df_checklist(per)
        st.dataframe(df, use_container_width=True)
        st.download_button(
            "⬇️ Exportar Checklist (CSV)",
            data=to_csv_bytes(df),
            file_name=f"checklist_{'todos' if per is None else per}.csv",
            mime="text/csv",
        )
