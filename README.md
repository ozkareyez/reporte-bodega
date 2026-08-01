# Reporte de Pedidos — Dashboard

Dashboard interactivo en Streamlit para reportar la operación de pedidos
(kg despachados, eficiencia por operario, cumplimiento de citas, novedades)
a partir del Excel de pedidos.

## Correr localmente

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Se abre en `http://localhost:8501`. Sube el archivo `.xlsx` desde la
interfaz (debe tener las hojas: `Registros`, `Despachos`, `Descargues`,
`Citas`, `Resumen`).

## Estructura del proyecto

```
reporte-pedidos/
├── app.py            # App de Streamlit (UI, filtros, gráficos)
├── data_utils.py      # Carga y limpieza de datos (tiempos, %, texto)
├── requirements.txt
├── .gitignore
└── README.md
```

## Subir a GitHub

```bash
git init
git add .
git commit -m "Dashboard inicial de reporte de pedidos"
git branch -M main
git remote add origin <URL_DE_TU_REPO>
git push -u origin main
```

> El `.gitignore` ya excluye los archivos `.xlsx` reales para que no subas
> datos de la empresa al repo. Cada quien sube su propio archivo desde la
> interfaz al usar la app.

## Desplegar para que tu jefe lo vea (gratis)

1. Sube este proyecto a un repo de GitHub (público o privado).
2. Entra a [share.streamlit.io](https://share.streamlit.io) con tu cuenta de GitHub.
3. "New app" → selecciona el repo, la rama `main` y el archivo `app.py`.
4. Deploy. Te da un link público (ej. `https://tu-app.streamlit.app`) que
   podés compartir con tu jefe — cada vez que subas un Excel nuevo desde
   ese link, el reporte se actualiza sin tocar código.

## Secciones del dashboard

- **Productividad**: kg y eficiencia por operario.
- **Clientes**: ranking de clientes por volumen, clientes con más novedades.
- **Rutas y vehículos**: kg y tiempo de cargue por ruta, kg por placa.
- **Tendencia**: evolución semanal de kg despachados y eficiencia.
- **Cumplimiento**: % de citas a tiempo, distribución de retrasos.
- **Novedades**: pedidos con devoluciones/novedades de cargue.
- **Datos**: tabla cruda filtrada, descargable en CSV.

## Próximos pasos (ver PRD)

- Sincronización automática con la fuente del Excel (OneDrive/Sheets) en
  vez de subida manual.
- Autenticación simple (`streamlit-authenticator`) si el link va a
  circular más allá de tu jefe.
- Comparativas semana a semana.
