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
