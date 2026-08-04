import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data_utils import (
    build_kpis,
    build_tipo_analysis,
    clean_citas,
    clean_despachos,
    clean_registros,
    load_workbook,
)

# Paleta corporativa Italcol Mascotas (extraída de italcolmascotas.com)
ORANGE = "#FF5C00"
VIOLET = "#5636D1"
PINK = "#E2498A"
GOLD = "#F4AA19"
DARK = "#474747"
TEXT = "#1F2430"
BG_SOFT = "#FFF6F0"
GRID = "#EFEFF3"

TYPE_COLORS = {"MASIVO": ORANGE, "VENTA DIRECTA": VIOLET}
TYPE_ACCENT = {"MASIVO": GOLD, "VENTA DIRECTA": PINK}

CHART_LAYOUT = dict(
    font=dict(family="Poppins, Segoe UI, sans-serif", size=12, color=TEXT),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=50, b=10),
    colorway=[ORANGE, VIOLET, PINK, GOLD],
    hoverlabel=dict(bgcolor="white", font=dict(color=TEXT, size=12)),
)


def style_fig(fig, title=None):
    fig.update_layout(**CHART_LAYOUT)
    if title:
        fig.update_layout(title=dict(text=title, font=dict(size=15, color=TEXT)))
    fig.update_xaxes(showgrid=False, linecolor=GRID, tickfont=dict(color="#6B7280"))
    fig.update_yaxes(gridcolor=GRID, zeroline=False, tickfont=dict(color="#6B7280"))
    return fig


st.set_page_config(
    page_title="Italcol Mascotas — Reporte de Pedidos",
    page_icon="🐾",
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
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Poppins', 'Segoe UI', sans-serif;
        }}

        /* Títulos y enlaces siempre visibles (aunque el navegador use tema oscuro) */
        h1, h2, h3, h4, h5, h6,
        [data-testid="stMarkdownContainer"] h1,
        [data-testid="stMarkdownContainer"] h2,
        [data-testid="stMarkdownContainer"] h3,
        [data-testid="stMarkdownContainer"] h4,
        [data-testid="stMarkdownContainer"] h5,
        [data-testid="stMarkdownContainer"] h6 {{
            color: #1F2430 !important;
        }}
        [data-testid="stCaptionContainer"],
        [data-testid="stCaptionContainer"] p {{
            color: #6B7280 !important;
        }}
        a {{
            color: {ORANGE} !important;
        }}
        a:hover {{
            color: {PINK} !important;
        }}
        label, [data-testid="stWidgetLabel"] p {{
            color: #374151 !important;
        }}
        [data-testid="stAlert"] p {{
            color: #1F2430 !important;
        }}

        .stApp {{
            background: linear-gradient(180deg, #FFFCFA 0%, #FFFFFF 260px);
        }}

        [data-testid="stSidebar"] {{
            background: #ffffff;
            border-right: 1px solid #ececef;
        }}
        [data-testid="stSidebar"] > div:first-child {{
            padding-top: 1.5rem;
        }}
        [data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] {{
            background: #FAFAFB;
            border: 1px solid #EBEBEE;
            border-radius: 12px;
        }}
        [data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] > div {{
            padding: 0.75rem 0.9rem;
        }}
        .sidebar-brand {{
            font-size: 0.95rem;
            font-weight: 700;
            letter-spacing: 0.01em;
            color: {DARK};
        }}
        .sidebar-sub {{
            font-size: 0.72rem;
            color: #9ca3af;
            margin-top: 0.15rem;
            margin-bottom: 0.4rem;
        }}
        .card-title {{
            font-size: 0.66rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #6b7280;
            margin-bottom: 0.35rem;
        }}
        [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {{
            font-size: 0.82rem;
            font-weight: 500;
            color: #374151;
        }}
        [data-testid="stSidebar"] [data-testid="stDateInput"] input,
        [data-testid="stSidebar"] [data-testid="stMultiSelect"] [data-baseweb="select"] {{
            border-radius: 7px;
            border-color: #e3e3e8;
        }}
        [data-testid="stSidebar"] .sidebar-count {{
            font-size: 0.75rem;
            color: #6b7280;
        }}

        /* Tabs con la identidad de marca */
        [data-testid="stTabs"] [data-baseweb="tab-list"] {{
            gap: 0.25rem;
            border-bottom: 1px solid #ECECEF;
        }}
        [data-testid="stTabs"] [data-baseweb="tab"] {{
            border-radius: 999px 999px 0 0;
            padding: 0.55rem 1.1rem;
            font-weight: 500;
            color: #6B7280;
        }}
        [data-testid="stTabs"] [data-baseweb="tab"]:hover {{
            color: {ORANGE};
        }}
        [data-testid="stTabs"] [aria-selected="true"] {{
            background: {BG_SOFT};
            color: {ORANGE} !important;
            font-weight: 600;
        }}

        /* Métricas con acento de marca */
        [data-testid="stMetric"] {{
            background: #ffffff;
            border: 1px solid #ECECEF;
            border-radius: 12px;
            padding: 0.85rem 1rem;
            box-shadow: 0 1px 2px rgba(31,36,48,0.04);
        }}
        [data-testid="stMetricValue"] {{
            font-size: 1.65rem;
            font-weight: 700;
            color: {DARK};
        }}
        [data-testid="stMetricLabel"] p {{
            font-size: 0.72rem;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            color: #6B7280;
        }}
        [data-testid="stMetricDelta"] {{
            font-size: 0.8rem;
        }}

        /* Tablas de datos con la línea visual de la página */
        [data-testid="stDataFrame"] {{
            border: 1px solid #ECECEF;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 1px 2px rgba(31,36,48,0.04);
        }}
        [data-testid="stDataFrame"] [data-testid="stElementToolbar"] {{
            border-bottom: 1px solid #ECECEF;
            background: #FAFAFB;
            border-radius: 12px 12px 0 0;
        }}
        [data-testid="stDataFrame"] [data-testid="stColumnHeader"] {{
            background: #FAFAFB;
            font-weight: 600;
            color: #1F2430;
        }}

        /* Botones */
        .stButton > button[kind="primary"],
        .stDownloadButton > button {{
            background: {ORANGE};
            border: none;
            border-radius: 999px;
            font-weight: 600;
        }}
        .stButton > button[kind="primary"]:hover,
        .stDownloadButton > button:hover {{
            background: {PINK};
            border: none;
        }}
        .stButton > button[kind="secondary"],
        .stButton > button[kind="tertiary"] {{
            border-radius: 999px;
        }}
        .stButton > button:hover {{
            border-color: {ORANGE};
            color: {ORANGE};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-brand">🐾 Reporte de Pedidos</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sidebar-sub">Italcol Mascotas · Bodega Murano</div>',
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

    if "Tipo" in registros.columns and registros["Tipo"].notna().any():
        tipos = sorted(registros["Tipo"].dropna().unique())
        with st.container(border=True):
            card_title("Tipo de pedido")
            selected = st.multiselect(
                "Tipo de pedido",
                tipos,
                default=tipos,
                label_visibility="collapsed",
                placeholder="Masivo / Venta Directa",
            )
        registros = registros[registros["Tipo"].isin(selected)]

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

tab_tipos, tab_productividad, tab_clientes, tab_rutas, tab_tendencia, tab_cumplimiento, tab_novedades, tab_datos = st.tabs(
    [
        "Tipos de pedido",
        "Productividad",
        "Clientes",
        "Rutas y vehículos",
        "Tendencia",
        "Cumplimiento",
        "Novedades",
        "Datos",
    ]
)

# ---------- Tipos de pedido (Masivo vs Venta Directa) ----------
with tab_tipos:
    tipo = build_tipo_analysis(registros)
    if tipo is None:
        st.info("El archivo no tiene la columna 'Tipo' para comparar Masivo vs Venta Directa.")
    else:
        tipos = tipo["tipos"]
        stats = tipo["stats"]

        st.markdown(
            """
            <style>
            .exec-box {
                background: linear-gradient(120deg, #FFF6F0, #FFFFFF);
                border: 1px solid #FFE0CE;
                border-left: 5px solid #FF5C00;
                border-radius: 12px;
                padding: 1.1rem 1.3rem;
                margin-bottom: 1rem;
            }
            .exec-box h4 {
                margin: 0 0 0.5rem 0;
                font-size: 0.78rem;
                text-transform: uppercase;
                letter-spacing: 0.1em;
                color: #FF5C00;
            }
            .exec-box ul { margin: 0; padding-left: 1.2rem; }
            .exec-box li {
                font-size: 0.86rem;
                color: #1F2430;
                line-height: 1.65;
                margin-bottom: 0.2rem;
            }
            .tipo-card {
                border: 1px solid #ECECEF;
                border-radius: 14px;
                padding: 0.95rem 1.1rem;
                background: #ffffff;
                box-shadow: 0 1px 3px rgba(31,36,48,0.05);
                margin-bottom: 0.6rem;
            }
            .tipo-card .tc-head {
                display: flex; align-items: center; gap: 0.5rem;
                margin-bottom: 0.6rem;
            }
            .tipo-card .tc-dot {
                width: 11px; height: 11px; border-radius: 50%;
            }
            .tipo-card .tc-name {
                font-weight: 700; font-size: 0.92rem; color: #1F2430;
            }
            .tipo-card .tc-badge {
                margin-left: auto;
                font-size: 0.7rem; font-weight: 600;
                padding: 0.15rem 0.55rem;
                border-radius: 999px;
            }
            .tipo-card .tc-grid {
                display: grid; grid-template-columns: 1fr 1fr; gap: 0.55rem;
            }
            .tipo-card .tc-kpi .k-label {
                font-size: 0.62rem; text-transform: uppercase;
                letter-spacing: 0.06em; color: #9CA3AF;
            }
            .tipo-card .tc-kpi .k-val {
                font-size: 1.15rem; font-weight: 700; color: #1F2430;
            }
            .tipo-card .tc-kpi .k-val small { font-size: 0.7rem; color: #9CA3AF; font-weight: 500; }
            </style>
            """,
            unsafe_allow_html=True,
        )

        # --- Resumen ejecutivo ---
        bullets = "".join(f"<li>{i}</li>" for i in tipo["insights"])
        st.markdown(
            f'<div class="exec-box"><h4>Resumen ejecutivo</h4><ul>{bullets}</ul></div>',
            unsafe_allow_html=True,
        )

        # --- Tarjetas comparativas por tipo ---
        st.markdown("### Comparativa Masivo vs Venta Directa")
        cols = st.columns(len(tipos))
        for col, t in zip(cols, tipos):
            row = stats.loc[t]
            share = tipo["distribucion_pedidos"].get(t, 0)
            with col:
                dev_pct = f"{row['Devolución %']:.1f}%" if "Devolución %" in stats else "—"
                ef_pct = f"{row['Eficiencia %']:.0f}%" if "Eficiencia %" in stats else "—"
                nov = int(row["Novedades"]) if "Novedades" in stats else 0
                st.markdown(
                    f"""
                    <div class="tipo-card">
                        <div class="tc-head">
                            <span class="tc-dot" style="background:{TYPE_COLORS[t]};"></span>
                            <span class="tc-name">{t.title()}</span>
                            <span class="tc-badge" style="background:{TYPE_COLORS[t]}22; color:{TYPE_COLORS[t]};">
                                {share:.0f}%
                            </span>
                        </div>
                        <div class="tc-grid">
                            <div class="tc-kpi">
                                <div class="k-label">Pedidos</div>
                                <div class="k-val">{row['Pedidos']:,.0f}</div>
                            </div>
                            <div class="tc-kpi">
                                <div class="k-label">Kg totales</div>
                                <div class="k-val">{row['Kg total']:,.0f} <small>kg</small></div>
                            </div>
                            <div class="tc-kpi">
                                <div class="k-label">Kg / pedido</div>
                                <div class="k-val">{row['Kg promedio']:,.0f} <small>kg</small></div>
                            </div>
                            <div class="tc-kpi">
                                <div class="k-label">Devolución</div>
                                <div class="k-val">{dev_pct}</div>
                            </div>
                            <div class="tc-kpi">
                                <div class="k-label">Eficiencia</div>
                                <div class="k-val">{ef_pct}</div>
                            </div>
                            <div class="tc-kpi">
                                <div class="k-label">Novedades</div>
                                <div class="k-val">{nov:,.0f}</div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # --- Gráficos: distribución y volumen ---
        c1, c2 = st.columns([1, 2])
        with c1:
            dist = stats["Pedidos"].reset_index(name="Pedidos")
            fig_donut = px.pie(
                dist, names="Tipo", values="Pedidos", hole=0.55,
                title="Distribución de pedidos por tipo",
            )
            fig_donut.update_traces(
                textinfo="label+percent",
                textfont=dict(color="white", size=12),
                marker=dict(colors=[TYPE_COLORS[t] for t in tipos], line=dict(color="white", width=2)),
            )
            st.plotly_chart(style_fig(fig_donut), width="stretch")

        with c2:
            kg_total = stats.reset_index().rename(columns={"index": "Tipo"})
            fig_kg = px.bar(
                kg_total, x="Tipo", y="Kg total",
                color="Tipo", color_discrete_map=TYPE_COLORS,
                text="Kg total", title="Kg totales despachados por tipo",
            )
            fig_kg.update_traces(
                texttemplate="%{text:,.0f} kg", textposition="outside",
                marker_line_width=0, width=0.5,
            )
            fig_kg.update_layout(
                yaxis_title="Kg",
                showlegend=False,
                yaxis=dict(range=[0, stats["Kg total"].max() * 1.18]),
            )
            st.plotly_chart(style_fig(fig_kg), width="stretch")

        # --- Segunda fila: tamaño promedio, eficiencia y devolución ---
        c1, c2, c3 = st.columns(3)
        with c1:
            fig_prom = px.bar(
                kg_total, x="Tipo", y="Kg promedio",
                color="Tipo", color_discrete_map=TYPE_COLORS,
                text="Kg promedio", title="Tamaño promedio del pedido",
            )
            fig_prom.update_traces(
                texttemplate="%{text:,.0f} kg", textposition="outside",
                marker_line_width=0, width=0.5, showlegend=False,
            )
            fig_prom.update_layout(yaxis_title="Kg", showlegend=False)
            st.plotly_chart(style_fig(fig_prom), width="stretch")

        with c2:
            if "Eficiencia %" in stats:
                fig_ef = px.bar(
                    kg_total, x="Tipo", y="Eficiencia %",
                    color="Tipo", color_discrete_map=TYPE_COLORS,
                    text="Eficiencia %", title="Eficiencia promedio por tipo",
                )
                fig_ef.update_traces(
                    texttemplate="%{text:.0f}%", textposition="outside",
                    marker_line_width=0, width=0.5, showlegend=False,
                )
                fig_ef.update_layout(yaxis_title="%", showlegend=False)
                st.plotly_chart(style_fig(fig_ef), width="stretch")

        with c3:
            if "Devolución %" in stats:
                fig_dev = px.bar(
                    kg_total, x="Tipo", y="Devolución %",
                    color="Tipo", color_discrete_map=TYPE_COLORS,
                    text="Devolución %", title="% del peso devuelto por tipo",
                )
                fig_dev.update_traces(
                    texttemplate="%{text:.1f}%", textposition="outside",
                    marker_line_width=0, width=0.5, showlegend=False,
                )
                fig_dev.update_layout(yaxis_title="%", showlegend=False)
                st.plotly_chart(style_fig(fig_dev), width="stretch")

        # --- Tendencia semanal apilada por tipo ---
        if "trend_kg" in tipo:
            trend = tipo["trend_kg"]
            fig_trend = go.Figure()
            for t in trend.columns:
                fig_trend.add_bar(
                    x=trend.index, y=trend[t], name=t.title(),
                    marker_color=TYPE_COLORS[t],
                    text=[f"{v:,.0f}" for v in trend[t]],
                    textposition="inside", textfont=dict(color="white", size=10),
                )
            fig_trend.update_layout(
                barmode="stack",
                title="Kg despachados por semana, por tipo de pedido",
                xaxis_title="Semana",
                yaxis_title="Kg",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            )
            st.plotly_chart(style_fig(fig_trend), width="stretch")

        # --- Top clientes por tipo ---
        if "top_clientes" in tipo:
            st.markdown("### Top clientes por tipo de pedido")
            top_tipo = tipo["top_clientes"]
            cc = st.columns(len(tipos))
            for col, t in zip(cc, tipos):
                top = top_tipo[top_tipo["Tipo"] == t].head(10).reset_index(drop=True)
                top["Kg"] = top["Kg"].map(lambda v: f"{v:,.0f} kg")
                top.index = top.index + 1
                with col:
                    st.markdown(
                        f'<div class="tipo-card" style="padding:0.6rem 0.9rem;">'
                        f'<span class="tc-dot" style="display:inline-block;background:{TYPE_COLORS[t]};'
                        f'width:9px;height:9px;border-radius:50%;"></span> '
                        f'<b style="font-size:0.85rem;">{t.title()}</b></div>',
                        unsafe_allow_html=True,
                    )
                    st.dataframe(top, width="stretch", hide_index=True)

        # --- Tabla comparativa completa y descarga ---
        st.markdown("### Tabla comparativa completa")
        tabla = stats.copy()
        for col in ["Kg total", "Kg promedio", "Devolución kg"]:
            if col in tabla.columns:
                tabla[col] = tabla[col].map(lambda v: f"{v:,.1f}")
        if "Devolución %" in tabla.columns:
            tabla["Devolución %"] = tabla["Devolución %"].map(lambda v: f"{v:.2f}%")
        if "Eficiencia %" in tabla.columns:
            tabla["Eficiencia %"] = tabla["Eficiencia %"].map(lambda v: f"{v:.1f}%")
        if "Alistamiento (min)" in tabla.columns:
            tabla["Alistamiento (min)"] = tabla["Alistamiento (min)"].map(lambda v: f"{v:.1f} min")
        if "Cargue (min)" in tabla.columns:
            tabla["Cargue (min)"] = tabla["Cargue (min)"].map(lambda v: f"{v:.1f} min")
        if "Días retraso prom" in tabla.columns:
            tabla["Días retraso prom"] = tabla["Días retraso prom"].map(lambda v: f"{v:.1f} días")

        st.dataframe(tabla, width="stretch")
        st.download_button(
            "Descargar comparativa (CSV)",
            tipo["stats"].to_csv(sep=";").encode("utf-8-sig"),
            file_name="comparativa_masivo_vs_venta_directa.csv",
            mime="text/csv",
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
            st.plotly_chart(style_fig(fig_kg), width="stretch")
        with c2:
            fig_ef = px.bar(
                by_operario,
                x="Operario",
                y="Eficiencia",
                title="Eficiencia promedio por operario (%)",
            )
            st.plotly_chart(style_fig(fig_ef), width="stretch")

        st.dataframe(by_operario, width="stretch", hide_index=True)
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
        st.plotly_chart(style_fig(fig_top), width="stretch")

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
                st.dataframe(novedades_cliente, width="stretch", hide_index=True)

        st.subheader("Detalle por cliente")
        st.dataframe(by_cliente, width="stretch", hide_index=True)
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
            st.plotly_chart(style_fig(fig_kg_ruta), width="stretch")
        with c2:
            fig_tiempo_ruta = px.bar(
                by_ruta.sort_values("Tiempo_cargue_prom_min", ascending=False).head(15),
                x="Ruta",
                y="Tiempo_cargue_prom_min",
                title="Tiempo de cargue promedio por ruta (min, top 15)",
            )
            fig_tiempo_ruta.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(style_fig(fig_tiempo_ruta), width="stretch")

        if "Placa" in despachos.columns:
            by_placa = (
                despachos.groupby("Placa")
                .agg(Kg=("Kg", "sum"), Viajes=("Kg", "count"))
                .reset_index()
                .sort_values("Kg", ascending=False)
            )
            st.subheader("Kg despachados por vehículo (placa)")
            st.dataframe(by_placa, width="stretch", hide_index=True)

        st.subheader("Detalle por ruta")
        st.dataframe(by_ruta, width="stretch", hide_index=True)
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
            st.plotly_chart(style_fig(fig_kg_semana), width="stretch")
        with c2:
            fig_ef_semana = px.line(
                by_semana,
                x="Semana",
                y="Eficiencia",
                markers=True,
                title="Eficiencia promedio por semana (%)",
            )
            st.plotly_chart(style_fig(fig_ef_semana), width="stretch")

        st.dataframe(by_semana, width="stretch", hide_index=True)
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
        st.plotly_chart(style_fig(fig_retraso), width="stretch")
        st.dataframe(citas, width="stretch", hide_index=True)
    else:
        st.info("La hoja 'Citas' no tiene datos suficientes para este reporte.")

    if not registros.empty and "Días retraso" in registros.columns:
        fig_dias = px.histogram(
            registros, x="Días retraso", title="Días de retraso en pedidos (Registros)"
        )
        st.plotly_chart(style_fig(fig_dias), width="stretch")

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
        st.dataframe(novedades[cols_mostrar], width="stretch", hide_index=True)
    else:
        st.info("No se encontraron columnas de novedades en los datos.")

# ---------- Datos crudos ----------
with tab_datos:
    st.dataframe(registros, width="stretch", hide_index=True)
    st.download_button(
        "Descargar datos filtrados (CSV)",
        registros.to_csv(index=False).encode("utf-8"),
        file_name="registros_filtrados.csv",
        mime="text/csv",
    )

