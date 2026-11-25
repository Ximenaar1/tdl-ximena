"""Tablero del observatorio · Clima para eventos al aire libre en Colima.

Local:   streamlit run tablero/app.py
Publico: Streamlit Community Cloud (archivo principal: tablero/app.py). Lee los archivos del repositorio, que la
captura y el analisis de GitHub Actions actualizan solos.
"""
import sys
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tablero import datos  # noqa: E402

st.set_page_config(page_title="Clima para eventos · Colima", layout="wide")
st.title("Clima para eventos al aire libre en Colima")
st.caption("Observatorio Trusted Data Lab · datos de Open-Meteo (CC BY 4.0) y NASA LaRC POWER · "
           "proyecto académico del TecNM Campus Colima")

# ---------- 1. Proximos 7 dias ----------
st.header("Próximos 7 días por municipio")
siete, captura = datos.pronostico_7_dias()
if siete.empty:
    st.info("Todavía no hay pronóstico de 7 días capturado.")
else:
    st.caption(f"Pronóstico de Open-Meteo capturado el {captura[:16].replace('T', ' ')} UTC.")
    tabla = siete.pivot(index="municipio", columns="fecha", values="lluvia_mm").round(1)
    st.write("Lluvia esperada (mm por día). Un día con 1 mm o más se considera día con lluvia.")
    st.dataframe(tabla.style.background_gradient(cmap="Blues", vmin=0, vmax=30), use_container_width=True)

# ---------- 2. Pronostico mensual (E1) ----------
st.header("Pronóstico de lluvia mensual · municipio de Colima")
pron = datos.cargar_pronostico()
hist = datos.cargar_historia("colima")
hist = hist[hist["mes_completo"]].tail(36)

for frase in datos.frases_cliente(pron):
    st.markdown(f"- {frase}")

real = pd.DataFrame({"mes": pd.to_datetime(hist["mes"]), "mm": hist["lluvia_total_mm"], "serie": "observado"})
futuro = pron.assign(mes=pd.to_datetime(pron["mes"]))
banda = alt.Chart(futuro).mark_area(opacity=0.25).encode(
    x=alt.X("mes:T", title="mes"), y=alt.Y("minimo_95_mm:Q", title="lluvia mensual (mm)"), y2="maximo_95_mm:Q")
linea_futuro = alt.Chart(futuro).mark_line(point=True).encode(
    x="mes:T", y="pronostico_mm:Q",
    tooltip=[alt.Tooltip("mes:T", format="%Y-%m"), "pronostico_mm", "minimo_95_mm", "maximo_95_mm"])
linea_real = alt.Chart(real).mark_line(color="black").encode(x="mes:T", y="mm:Q",
                                                              tooltip=[alt.Tooltip("mes:T", format="%Y-%m"), "mm"])
st.altair_chart(banda + linea_futuro + linea_real, use_container_width=True)
st.caption(f"Negro: lluvia observada. Línea con puntos: pronóstico; banda: intervalo de predicción del 95 %. "
           f"Modelo: {pron['modelo'].iloc[0]}, elegido por el menor error medio (MAE) en los 12 meses de prueba. "
           "En la temporada seca el intervalo es muy amplio: el pronóstico sirve sobre todo para planear la "
           "temporada de lluvias.")
with st.expander("Ver tabla del pronóstico"):
    st.dataframe(pron[["mes", "pronostico_mm", "minimo_95_mm", "maximo_95_mm"]], use_container_width=True)

# ---------- 3. Por que confiar en estos datos ----------
st.header("¿Por qué confiar en estos datos?")
ind = datos.indicadores_calidad()
c1, c2, c3 = st.columns(3)
c1.metric("Disponibilidad de la captura", f"{ind['disponibilidad_desde_correccion']} %",
          help="Desde la corrección del 14-nov-2026 (ver docs/E1/fiabilidad.md)")
c2.metric("Registros rechazados por la puerta de calidad", ind["registros_cuarentena"],
          help="Se guardan en data/cuarentena con su motivo; nunca se borran en silencio")
c3.metric("Último día con dato consolidado", ind["ultimo_dia_con_dato"])
st.caption(f"{ind['registros_plata']:,} días-municipio validados en la capa Plata. Código y evidencia: "
           "github.com/Ximenaar1/tdl-ximena")
