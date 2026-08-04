"""
Funciones de carga y limpieza de datos del archivo de pedidos.

El Excel fuente trae varios formatos "sucios" para gráficos:
- Eficiencia como texto porcentual: "174.84%"
- Tiempos como texto: "1h 19m"
Este módulo los normaliza a tipos numéricos.
"""

import re
import pandas as pd
import streamlit as st

SHEETS = ["Registros", "Despachos", "Descargues", "Citas", "Resumen"]

TIPO_ORDER = ["MASIVO", "VENTA DIRECTA"]

TIME_PATTERN = re.compile(r"(?:(\d+)h)?\s*(?:(\d+)m)?")


def parse_time_to_minutes(value):
    """Convierte '1h 19m' -> 79.0 (minutos). Devuelve None si no hay match."""
    if pd.isna(value) or value == "":
        return None
    match = TIME_PATTERN.match(str(value).strip())
    if not match:
        return None
    hours = int(match.group(1)) if match.group(1) else 0
    minutes = int(match.group(2)) if match.group(2) else 0
    if hours == 0 and minutes == 0 and "h" not in str(value) and "m" not in str(value):
        return None
    return hours * 60 + minutes


def parse_percent(value):
    """Convierte '174.84%' -> 174.84 (float)."""
    if pd.isna(value) or value == "":
        return None
    try:
        return float(str(value).replace("%", "").strip())
    except ValueError:
        return None


def normalize_text(value):
    """Uniforma nombres: mayúsculas, sin espacios extra."""
    if pd.isna(value):
        return value
    return " ".join(str(value).strip().upper().split())


@st.cache_data(show_spinner="Leyendo y limpiando el archivo...")
def load_workbook(file) -> dict[str, pd.DataFrame]:
    """Lee todas las hojas relevantes del Excel en un dict de DataFrames."""
    raw = pd.read_excel(file, sheet_name=None, engine="openpyxl")
    sheets = {name: df for name, df in raw.items() if name in SHEETS}
    return sheets


def clean_registros(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if "Cliente" in df.columns:
        df["Cliente"] = df["Cliente"].apply(normalize_text)
    if "Operario" in df.columns:
        df["Operario"] = df["Operario"].apply(normalize_text)
    if "Tipo" in df.columns:
        df["Tipo"] = df["Tipo"].apply(normalize_text)

    if "Eficiencia" in df.columns:
        df["Eficiencia_num"] = df["Eficiencia"].apply(parse_percent)

    for col in ["Tiempo alistamiento", "Tiempo cargue"]:
        if col in df.columns:
            df[f"{col}_min"] = df[col].apply(parse_time_to_minutes)

    if "Kg despachados" in df.columns:
        df["Kg"] = df["Kg despachados"]

    if "Fecha" in df.columns:
        df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")

    for col in ["Kg", "Kg despachados", "Devolución kg", "Días retraso"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def clean_citas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "Retraso (min)" in df.columns:
        df["Retraso (min)"] = pd.to_numeric(df["Retraso (min)"], errors="coerce")
    return df


def clean_despachos(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if "Ruta" in df.columns:
        df["Ruta"] = df["Ruta"].apply(normalize_text)
    if "Placa" in df.columns:
        df["Placa"] = df["Placa"].apply(normalize_text)

    if "Tiempo cargue" in df.columns:
        df["Tiempo cargue_min"] = df["Tiempo cargue"].apply(parse_time_to_minutes)

    if "Fecha" in df.columns:
        df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")

    if "Kg" in df.columns:
        df["Kg"] = pd.to_numeric(df["Kg"], errors="coerce")

    return df


def build_kpis(registros: pd.DataFrame) -> dict:
    total_pedidos = len(registros)
    total_kg = registros["Kg"].sum() if "Kg" in registros else 0
    eficiencia_prom = (
        registros["Eficiencia_num"].mean() if "Eficiencia_num" in registros else None
    )
    devolucion_total = (
        registros["Devolución kg"].sum() if "Devolución kg" in registros else 0
    )
    pct_devolucion = (devolucion_total / total_kg * 100) if total_kg else 0

    return {
        "total_pedidos": total_pedidos,
        "total_kg": total_kg,
        "eficiencia_prom": eficiencia_prom,
        "devolucion_total": devolucion_total,
        "pct_devolucion": pct_devolucion,
    }


def _es_novedad(series) -> pd.Series:
    return series.astype(str).str.strip().str.lower() == "sí"


def _tipo_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Métricas comparativas por tipo de pedido (Masivo / Venta Directa)."""
    g = df.groupby("Tipo")
    stats = pd.DataFrame(
        {
            "Pedidos": g.size(),
            "Kg total": g["Kg"].sum(),
            "Kg promedio": g["Kg"].mean(),
            "Devolución kg": g["Devolución kg"].sum(),
            "Devolución %": g.apply(
                lambda x: x["Devolución kg"].sum() / x["Kg"].sum() * 100
            ),
        }
    )
    if "Eficiencia_num" in df.columns:
        stats["Eficiencia %"] = g["Eficiencia_num"].mean()
    if "Tiempo alistamiento_min" in df.columns:
        stats["Alistamiento (min)"] = g["Tiempo alistamiento_min"].mean()
    if "Tiempo cargue_min" in df.columns:
        stats["Cargue (min)"] = g["Tiempo cargue_min"].mean()
    if "Novedad cargue" in df.columns:
        stats["Novedades"] = g["Novedad cargue"].apply(
            lambda s: _es_novedad(s).sum()
        )
    if "Días retraso" in df.columns:
        stats["Días retraso prom"] = g["Días retraso"].mean()
    return stats


def build_tipo_analysis(df: pd.DataFrame) -> dict | None:
    """Reporte comparativo Masivo vs Venta Directa. None si no hay columna Tipo."""
    if "Tipo" not in df.columns or df["Tipo"].dropna().empty:
        return None

    d = df.dropna(subset=["Tipo"]).copy()
    tipos = [t for t in TIPO_ORDER if t in d["Tipo"].unique()]
    if not tipos:
        return None

    stats = _tipo_stats(d).reindex(tipos).dropna(how="all")
    pedidos_total = len(d)

    resumen = {
        "tipos": tipos,
        "stats": stats,
        "distribucion_pedidos": (stats["Pedidos"] / pedidos_total * 100),
        "total_pedidos": pedidos_total,
        "total_kg": stats["Kg total"].sum(),
    }

    if "Semana" in d.columns and "Kg" in d.columns:
        trend = (
            d.groupby(["Semana", "Tipo"])["Kg"]
            .sum()
            .unstack(fill_value=0)
            .reindex(columns=tipos, fill_value=0)
        )
        resumen["trend_kg"] = trend

    if "Cliente" in d.columns:
        top = (
            d.groupby(["Cliente", "Tipo"])["Kg"]
            .sum()
            .reset_index()
            .sort_values("Kg", ascending=False)
        )
        resumen["top_clientes"] = top

    if "Operario" in d.columns:
        by_operario = (
            d.groupby(["Operario", "Tipo"])
            .agg(Kg=("Kg", "sum"), Pedidos=("Kg", "count"))
            .reset_index()
        )
        resumen["by_operario"] = by_operario

    resumen["insights"] = _tipo_insights(d, stats, tipos)
    return resumen


def _tipo_insights(df: pd.DataFrame, stats: pd.DataFrame, tipos: list) -> list[str]:
    """Observaciones en lenguaje natural para el informe ejecutivo."""
    insights = []

    mayor_vol = stats["Kg total"].idxmax()
    menor_vol = stats["Kg total"].idxmin()
    insights.append(
        f"{mayor_vol} concentra el mayor volumen de carga con "
        f"{stats.loc[mayor_vol, 'Kg total']:,.0f} kg, superando a {menor_vol} "
        f"({stats.loc[menor_vol, 'Kg total']:,.0f} kg)."
    )

    mayor_ped = stats["Pedidos"].idxmax()
    insights.append(
        f"{mayor_ped} genera más pedidos ({stats.loc[mayor_ped, 'Pedidos']:,.0f}), "
        f"mientras que {stats['Pedidos'].idxmin()} pedidos promedio "
        f"({stats.loc[stats['Pedidos'].idxmin(), 'Kg promedio']:,.0f} kg/pedido) "
        f"son de mayor tamaño."
    )

    if "Devolución %" in stats.columns:
        tipo_dev = stats["Devolución %"].idxmax()
        insights.append(
            f"{tipo_dev} concentra las devoluciones con "
            f"{stats.loc[tipo_dev, 'Devolución %']:.1f}% de su peso devuelto "
            f"({stats.loc[tipo_dev, 'Devolución kg']:,.0f} kg), frente a "
            f"{stats['Devolución %'].min():.1f}% de {stats['Devolución %'].idxmin()}."
        )

    if "Eficiencia %" in stats.columns:
        tipo_ef = stats["Eficiencia %"].idxmax()
        insights.append(
            f"{tipo_ef} alcanza una eficiencia promedio de "
            f"{stats.loc[tipo_ef, 'Eficiencia %']:.0f}% vs "
            f"{stats.loc[stats['Eficiencia %'].idxmin(), 'Eficiencia %']:.0f}% de "
            f"{stats['Eficiencia %'].idxmin()}."
        )

    if "Novedades" in stats.columns:
        tipo_nov = stats["Novedades"].idxmax()
        insights.append(
            f"Las novedades de cargue se concentran en {tipo_nov} "
            f"({stats.loc[tipo_nov, 'Novedades']:,.0f} casos) y representan el "
            f"{stats.loc[tipo_nov, 'Novedades'] / max(stats['Novedades'].sum(), 1) * 100:.0f}% "
            f"del total."
        )

    return insights
