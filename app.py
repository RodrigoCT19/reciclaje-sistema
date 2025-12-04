# app.py
import streamlit as st
from datetime import date
import pandas as pd

from src import db
from src.kpi import get_kpis
from src.utils_export import to_csv_bytes

import altair as alt


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
st.sidebar.info("Proyecto: Sistema de Reciclaje")

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

    # ---------- Exportar KPI (solo CSV por ahora) ----------
    st.markdown("### Exportar indicadores")
    
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
    
    st.caption("La exportación a PDF está desactivada temporalmente en esta versión.")



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
            grp["porc_reciclado"] = grp.apply(
                lambda r: 0.0 if r["kg_tot"] == 0 else (r["kg_rec"] / r["kg_tot"]) * 100,
                axis=1,
            ).round(2)

            # Pasamos el índice a columna para Altair
            grp = grp.reset_index()
            grp["mes"] = grp["fecha"].dt.strftime("%Y-%m")

            chart1 = (
                alt.Chart(grp)
                .mark_line(point=True)
                .encode(
                    x=alt.X("fecha:T", title="Mes", axis=alt.Axis(format="%b %y")),
                    y=alt.Y("porc_reciclado:Q", title="% reciclado"),
                    tooltip=[
                        alt.Tooltip("mes:N", title="Mes"),
                        alt.Tooltip("kg_tot:Q", title="Kg totales", format=".1f"),
                        alt.Tooltip("kg_rec:Q", title="Kg reciclados", format=".1f"),
                        alt.Tooltip("porc_reciclado:Q", title="% reciclado", format=".1f"),
                    ],
                )
                .properties(height=260)
                .interactive()
            )

            st.altair_chart(chart1, use_container_width=True)
            st.caption(
                "Muestra la evolución mensual del porcentaje de residuos reciclados "
                "respecto al total generado."
            )
        else:
            st.info("No hay datos de residuos para graficar.")

    # ---------- Gráfico 2: ahorro neto por mes ----------
    with tab2:
        if not df_c.empty:
            df_c["mes_dt"] = pd.to_datetime(df_c["mes"] + "-01", errors="coerce")
            df_c["ahorro_neto"] = (
                df_c["ingresos"] + df_c["costos_evitados"] - df_c["costos_gestion"]
            )
            ahorro = (
                df_c.groupby(pd.Grouper(key="mes_dt", freq="MS"))["ahorro_neto"]
                .sum()
                .reset_index()
            )
            ahorro["mes"] = ahorro["mes_dt"].dt.strftime("%Y-%m")

            chart2 = (
                alt.Chart(ahorro)
                .mark_bar()
                .encode(
                    x=alt.X("mes_dt:T", title="Mes", axis=alt.Axis(format="%b %y")),
                    y=alt.Y("ahorro_neto:Q", title="Ahorro neto (S/.)"),
                    tooltip=[
                        alt.Tooltip("mes:N", title="Mes"),
                        alt.Tooltip("ahorro_neto:Q", title="Ahorro neto (S/.)", format=".2f"),
                    ],
                )
                .properties(height=260)
                .interactive()
            )

            st.altair_chart(chart2, use_container_width=True)
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

            # Convertimos Sí / No a 1 / 0
            df_x[items] = df_x[items].applymap(
                lambda v: 1 if str(v).strip().lower() in ("si", "sí", "1", "true") else 0
            )

            df_x["porc_cumplimiento"] = (df_x[items].sum(axis=1) / 10) * 100
            cump = (
                df_x.groupby(pd.Grouper(key="fecha", freq="MS"))["porc_cumplimiento"]
                .mean()
                .reset_index()
            )
            cump["mes"] = cump["fecha"].dt.strftime("%Y-%m")

            chart3 = (
                alt.Chart(cump)
                .mark_line(point=True)
                .encode(
                    x=alt.X("fecha:T", title="Mes", axis=alt.Axis(format="%b %y")),
                    y=alt.Y("porc_cumplimiento:Q", title="% cumplimiento"),
                    tooltip=[
                        alt.Tooltip("mes:N", title="Mes"),
                        alt.Tooltip(
                            "porc_cumplimiento:Q", title="% cumplimiento", format=".1f"
                        ),
                    ],
                )
                .properties(height=260)
                .interactive()
            )

            st.altair_chart(chart3, use_container_width=True)
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
                # Fila 1: Fecha / Periodo
                col1, col2 = st.columns(2)
                with col1:
                    fecha = st.date_input("Fecha", date.today())
                with col2:
                    periodo = periodo_selectbox()

                # Fila 2: Proceso / Lote
                col3, col4 = st.columns(2)
                with col3:
                    proceso = st.selectbox("Proceso", ["Corte", "Soldadura", "Ensamble"])
                with col4:
                    lote = st.text_input("Lote")

                # Fila 3: Kg Totales / Kg Reciclados
                col5, col6 = st.columns(2)
                with col5:
                    kg_totales = st.number_input(
                        "Kg Totales", min_value=0.0, step=0.1
                    )
                with col6:
                    kg_reciclados = st.number_input(
                        "Kg Reciclados", min_value=0.0, step=0.1
                    )

                # Fila 4: Destino / Responsable
                col7, col8 = st.columns(2)
                with col7:
                    destino = st.selectbox("Destino", ["Reúso", "Reciclaje", "Venta"])
                with col8:
                    responsable = st.text_input("Responsable")

                submitted = st.form_submit_button("Guardar")

            if submitted:
                if kg_reciclados > kg_totales:
                    st.error("Los Kg reciclados no pueden ser mayores que los Kg totales.")
                else:
                    db.insert_residuo(
                        str(fecha),
                        proceso,
                        lote,
                        float(kg_totales),
                        float(kg_reciclados),
                        destino,
                        responsable,
                        periodo,
                    )
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
            c1, c2 = st.columns(2)
            with c1:
                mes = st.text_input("Mes (YYYY-MM)")
            with c2:
                periodo = periodo_selectbox()

            c3, c4 = st.columns(2)
            with c3:
                ingresos = st.number_input("Ingresos por venta (S/.)", min_value=0.0, step=0.1)
            with c4:
                evitados = st.number_input("Costos evitados (S/.)", min_value=0.0, step=0.1)

            c5, _ = st.columns([1, 1])
            with c5:
                gestion = st.number_input("Costos de gestión (S/.)", min_value=0.0, step=0.1)

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
            c1, c2 = st.columns(2)
            with c1:
                fecha = st.date_input("Fecha", date.today())
                area = st.selectbox("Área/Proceso", ["Corte", "Soldadura", "Ensamble", "Almacén"])
            with c2:
                responsable = st.text_input("Responsable")
                periodo = periodo_selectbox()

            st.markdown("Marca **Sí** o **No** para cada ítem:")

            opciones_SN = ["Sí", "No"]
            col_izq, col_der = st.columns(2)
            items = []

            # Ítems 1 al 5 en la columna izquierda
            for i in range(1, 6):
                with col_izq:
                    items.append(
                        st.selectbox(f"Ítem {i}", opciones_SN, key=f"i{i}")
                    )

            # Ítems 6 al 10 en la columna derecha
            for i in range(6, 11):
                with col_der:
                    items.append(
                        st.selectbox(f"Ítem {i}", opciones_SN, key=f"i{i}")
                    )

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
