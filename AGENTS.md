# AGENTS.md

Streamlit dashboard ("Reporte de Pedidos") for reporting warehouse order operations from an uploaded Excel file. UI text, code identifiers, and column names are in Spanish.

## Run

```bash
source venv/bin/activate
pip install -r requirements.txt   # streamlit, pandas, plotly, openpyxl
streamlit run app.py              # http://localhost:8501
```

## Data model

- The app is useless without a real `.xlsx`. There is **no sample data in the repo** — `.gitignore` blocks all `*.xlsx` (even private data; don't add company data or commit an Excel).
- The uploaded workbook must contain these sheets (case-sensitive names): `Registros`, `Despachos`, `Descargues`, `Citas`, `Resumen`. Only these are read (see `SHEETS` in `data_utils.py`).
- Data cleaning/normalization lives in `data_utils.py`; `app.py` only builds UI, filters, and charts. Keep it that way.

## Quirks that matter when editing

- Column names are accented Spanish strings and must match **exactly** (e.g. `Devolución kg`, `Novedad cargue`, `Días retraso`, `Tiempo cargue_min`, `Eficiencia_num`). Code guards column presence with `if "X" in df.columns` before use — keep that pattern.
- `Registros` may contain a `Tipo` column whose values are `MASIVO` / `VENTA DIRECTA` (normalized by `clean_registros`). The comparison report lives in `build_tipo_analysis` (data) and the `tab_tipos` section of `app.py` (UI). Not all workbooks have this column; every code path must handle its absence.
- Brand colors (from italcolmascotas.com) are defined as constants at the top of `app.py` (`ORANGE`, `VIOLET`, `PINK`, `GOLD`, `DARK`) and reused by charts via `style_fig`. Keep all UI styling in `app.py`.
- `clean_registros` adds derived numeric columns (`Eficiencia_num`, `<col>_min`) parsed from messy formats: `"174.84%"` and `"1h 19m"`. Don't rename these.
- Text columns are normalized via `normalize_text` (uppercase, collapsed spaces); aggregations rely on that.
- `load_workbook` is wrapped in `@st.cache_data`, so it returns a fresh dict each call but cached by file — don't mutate the returned DataFrames in place.

## Verification

No test suite, linter, or CI exists. Verify with:

```bash
python -m py_compile app.py data_utils.py
```

and manually run the app (`streamlit run app.py`). The app's only real runtime check requires uploading an Excel.
