import pandas as pd
import plotly.express as px
import streamlit as st

from data_utils import build_kpis, clean_citas, clean_despachos, clean_registros, load_workbook

st.set_page_config(
    page_title="Reporte de Pedidos",
    layout="wide",
)

st.title(" Reporte de operación — Bodega Murano")
st.caption("Sube el archivo Excel más reciente para actualizar el reporte.")

uploaded_file = st.file_uploader(
    "Archivo de pedidos (.xlsx)", type=["xlsx"], accept_multiple_files=False
)

if uploaded_file is None:
    st.info("Sube un archivo `.xlsx` con las hojas: Registros, Despachos, Descargues, Citas, Resumen.")
    st.stop()

sheets = load_workbook(uploaded_file)

registros = clean_registros(sheets.get("Registros", pd.DataFrame()))
citas = clean_citas(sheets.get("Citas", pd.DataFrame()))
despachos = clean_despachos(sheets.get("Despachos", pd.DataFrame()))

# ---------- Filtros ----------
with st.sidebar:
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            background: #ffffff;
            border-right: 1px solid #ececef;
        }
        [data-testid="stSidebar"] > div:first-child {
            padding-top: 1.5rem;
        }
        [data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] {
            background: #fafafb;
            border: 1px solid #ebebee;
            border-radius: 10px;
        }
        [data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] > div {
            padding: 0.75rem 0.9rem;
        }
        .sidebar-brand {
            font-size: 0.95rem;
            font-weight: 600;
            letter-spacing: 0.01em;
            color: #111827;
        }
        .sidebar-sub {
            font-size: 0.72rem;
            color: #9ca3af;
            margin-top: 0.15rem;
            margin-bottom: 0.4rem;
        }
        .card-title {
            font-size: 0.66rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #6b7280;
            margin-bottom: 0.35rem;
        }
        [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
            font-size: 0.82rem;
            font-weight: 500;
            color: #374151;
        }
        [data-testid="stSidebar"] [data-testid="stDateInput"] input,
        [data-testid="stSidebar"] [data-testid="stMultiSelect"] [data-baseweb="select"] {
            border-radius: 7px;
            border-color: #e3e3e8;
        }
        [data-testid="stSidebar"] .sidebar-count {
            font-size: 0.75rem;
            color: #6b7280;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-brand">Reporte de Pedidos</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sidebar-sub">Bodega Murano</div>',
        unsafe_allow_html=True,
    )

    def card_title(texto: str) -> None:
        st.markdown(f'<div class="card-title">{texto}</div>', unsafe_allow_html=True)

    if "Fecha" in registros.columns and registros["Fecha"].notna().any():
        min_date = registros["Fecha"].min().date()
        max_date = registros["Fecha"].max().date()
        with st.container(border=True):
            card_title("Periodo")
            date_range = st.date_input(
                "Rango de fechas",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                label_visibility="collapsed",
            )
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start, end = date_range
            registros = registros[
                (registros["Fecha"].dt.date >= start) & (registros["Fecha"].dt.date <= end)
            ]

    if "Operario" in registros.columns:
        operarios = sorted(registros["Operario"].dropna().unique())
        with st.container(border=True):
            card_title("Equipo")
            selected = st.multiselect(
                "Operario",
                operarios,
                default=operarios,
                label_visibility="collapsed",
                placeholder="Todos los operarios",
            )
        registros = registros[registros["Operario"].isin(selected)]

    st.markdown(
        f'<div class="sidebar-count">{len(registros):,} pedidos en el reporte</div>',
        unsafe_allow_html=True,
    )
    if st.button("Restablecer filtros", type="tertiary"):
        st.session_state.clear()
        st.rerun()

# ---------- KPIs ----------
kpis = build_kpis(registros)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total pedidos", f"{kpis['total_pedidos']:,}")
col2.metric("Total kg", f"{kpis['total_kg']:,.0f} kg")
col3.metric(
    "Eficiencia promedio",
    f"{kpis['eficiencia_prom']:.1f}%" if kpis["eficiencia_prom"] is not None else "—",
)
col4.metric("Devolución", f"{kpis['pct_devolucion']:.2f}%")

st.divider()

tab_productividad, tab_clientes, tab_rutas, tab_tendencia, tab_cumplimiento, tab_novedades, tab_datos = st.tabs(
    ["Productividad", "Clientes", "Rutas y vehículos", "Tendencia", "Cumplimiento", "Novedades", "Datos"]
)

# ---------- Productividad por operario ----------
with tab_productividad:
    if not registros.empty and "Operario" in registros.columns:
        by_operario = (
            registros.groupby("Operario")
            .agg(
                Kg=("Kg", "sum"),
                Pedidos=("Kg", "count"),
                Eficiencia=("Eficiencia_num", "mean"),
            )
            .reset_index()
            .sort_values("Kg", ascending=False)
        )

        c1, c2 = st.columns(2)
        with c1:
            fig_kg = px.bar(
                by_operario, x="Operario", y="Kg", title="Kg despachados por operario"
            )
            st.plotly_chart(fig_kg, use_container_width=True)
        with c2:
            fig_ef = px.bar(
                by_operario,
                x="Operario",
                y="Eficiencia",
                title="Eficiencia promedio por operario (%)",
            )
            st.plotly_chart(fig_ef, use_container_width=True)

        st.dataframe(by_operario, use_container_width=True, hide_index=True)
    else:
        st.info("No hay datos de operarios en el rango/filtro seleccionado.")

# ---------- Clientes ----------
with tab_clientes:
    if not registros.empty and "Cliente" in registros.columns:
        by_cliente = (
            registros.groupby("Cliente")
            .agg(
                Kg=("Kg", "sum"),
                Pedidos=("Kg", "count"),
                Devolucion_kg=("Devolución kg", "sum") if "Devolución kg" in registros.columns else ("Kg", "sum"),
            )
            .reset_index()
            .sort_values("Kg", ascending=False)
        )

        top_n = st.slider("Mostrar top N clientes", 5, min(30, len(by_cliente)), min(10, len(by_cliente)))
        top_clientes = by_cliente.head(top_n)

        fig_top = px.bar(
            top_clientes, x="Cliente", y="Kg", title=f"Top {top_n} clientes por kg"
        )
        fig_top.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_top, use_container_width=True)

        if "Novedad cargue" in registros.columns:
            novedades_cliente = (
                registros[registros["Novedad cargue"].astype(str).str.strip().str.lower() == "sí"]
                .groupby("Cliente")
                .size()
                .reset_index(name="Novedades")
                .sort_values("Novedades", ascending=False)
                .head(10)
            )
            if not novedades_cliente.empty:
                st.subheader("Clientes con más novedades de cargue")
                st.dataframe(novedades_cliente, use_container_width=True, hide_index=True)

        st.subheader("Detalle por cliente")
        st.dataframe(by_cliente, use_container_width=True, hide_index=True)
    else:
        st.info("No hay datos de clientes en el rango/filtro seleccionado.")

# ---------- Rutas y vehículos ----------
with tab_rutas:
    if not despachos.empty and "Ruta" in despachos.columns:
        by_ruta = (
            despachos.groupby("Ruta")
            .agg(
                Kg=("Kg", "sum"),
                Viajes=("Kg", "count"),
                Tiempo_cargue_prom_min=("Tiempo cargue_min", "mean"),
            )
            .reset_index()
            .sort_values("Kg", ascending=False)
        )

        c1, c2 = st.columns(2)
        with c1:
            fig_kg_ruta = px.bar(
                by_ruta.head(15), x="Ruta", y="Kg", title="Kg despachados por ruta (top 15)"
            )
            fig_kg_ruta.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_kg_ruta, use_container_width=True)
        with c2:
            fig_tiempo_ruta = px.bar(
                by_ruta.sort_values("Tiempo_cargue_prom_min", ascending=False).head(15),
                x="Ruta",
                y="Tiempo_cargue_prom_min",
                title="Tiempo de cargue promedio por ruta (min, top 15)",
            )
            fig_tiempo_ruta.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_tiempo_ruta, use_container_width=True)

        if "Placa" in despachos.columns:
            by_placa = (
                despachos.groupby("Placa")
                .agg(Kg=("Kg", "sum"), Viajes=("Kg", "count"))
                .reset_index()
                .sort_values("Kg", ascending=False)
            )
            st.subheader("Kg despachados por vehículo (placa)")
            st.dataframe(by_placa, use_container_width=True, hide_index=True)

        st.subheader("Detalle por ruta")
        st.dataframe(by_ruta, use_container_width=True, hide_index=True)
    else:
        st.info("La hoja 'Despachos' no tiene datos suficientes para este reporte.")

# ---------- Tendencia semanal ----------
with tab_tendencia:
    if not registros.empty and "Semana" in registros.columns:
        by_semana = (
            registros.groupby("Semana")
            .agg(
                Kg=("Kg", "sum"),
                Pedidos=("Kg", "count"),
                Eficiencia=("Eficiencia_num", "mean"),
            )
            .reset_index()
            .sort_values("Semana")
        )

        c1, c2 = st.columns(2)
        with c1:
            fig_kg_semana = px.line(
                by_semana, x="Semana", y="Kg", markers=True, title="Kg despachados por semana"
            )
            st.plotly_chart(fig_kg_semana, use_container_width=True)
        with c2:
            fig_ef_semana = px.line(
                by_semana,
                x="Semana",
                y="Eficiencia",
                markers=True,
                title="Eficiencia promedio por semana (%)",
            )
            st.plotly_chart(fig_ef_semana, use_container_width=True)

        st.dataframe(by_semana, use_container_width=True, hide_index=True)
    else:
        st.info("No hay columna 'Semana' disponible para calcular la tendencia.")

# ---------- Cumplimiento ----------
with tab_cumplimiento:
    if not citas.empty and "Cumplió" in citas.columns:
        pct_cumplio = (citas["Cumplió"].astype(str).str.strip().str.lower() == "sí").mean() * 100
        st.metric("Citas cumplidas a tiempo", f"{pct_cumplio:.1f}%")

        fig_retraso = px.histogram(
            citas, x="Retraso (min)", title="Distribución de retraso en citas (min)"
        )
        st.plotly_chart(fig_retraso, use_container_width=True)
        st.dataframe(citas, use_container_width=True, hide_index=True)
    else:
        st.info("La hoja 'Citas' no tiene datos suficientes para este reporte.")

    if not registros.empty and "Días retraso" in registros.columns:
        fig_dias = px.histogram(
            registros, x="Días retraso", title="Días de retraso en pedidos (Registros)"
        )
        st.plotly_chart(fig_dias, use_container_width=True)

# ---------- Novedades ----------
with tab_novedades:
    if not registros.empty and "Novedad cargue" in registros.columns:
        novedades = registros[
            registros["Novedad cargue"].astype(str).str.strip().str.lower() == "sí"
        ]
        st.metric("Pedidos con novedad de cargue", len(novedades))
        cols_mostrar = [
            c
            for c in [
                "Fecha",
                "Cliente",
                "Operario",
                "Kg",
                "Devolución kg",
                "Novedad cargue",
                "Cantidad referencias novedad",
            ]
            if c in novedades.columns
        ]
        st.dataframe(novedades[cols_mostrar], use_container_width=True, hide_index=True)
    else:
        st.info("No se encontraron columnas de novedades en los datos.")

# ---------- Datos crudos ----------
with tab_datos:
    st.dataframe(registros, use_container_width=True, hide_index=True)
    st.download_button(
        "Descargar datos filtrados (CSV)",
        registros.to_csv(index=False).encode("utf-8"),
        file_name="registros_filtrados.csv",
        mime="text/csv",
    )

