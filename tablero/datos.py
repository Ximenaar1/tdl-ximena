"""Lectura de datos para el tablero (funciones puras de pandas, se prueban sin Streamlit)."""
import json
from pathlib import Path

import pandas as pd

from extractores.municipios import MUNICIPIOS

RAIZ = Path(__file__).resolve().parent.parent
NOMBRE = {m["clave"]: m["nombre"] for m in MUNICIPIOS}
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
         "noviembre", "diciembre"]
UMBRAL_LLUVIA_EVENTO_MM = 1.0  # un dia "con lluvia" (criterio OMM, el mismo que en el pipeline)


def nombre_mes(periodo):
    """'2027-09' -> 'septiembre de 2027'."""
    anio, mes = str(periodo).split("-")
    return f"{MESES[int(mes) - 1]} de {anio}"


def cargar_pronostico(raiz=RAIZ):
    return pd.read_csv(Path(raiz) / "data" / "oro" / "pronostico_lluvia_colima.csv")


def cargar_historia(municipio="colima", raiz=RAIZ):
    oro = pd.read_csv(Path(raiz) / "data" / "oro" / "clima_municipio_mes.csv")
    return oro[oro["municipio"] == municipio].reset_index(drop=True)


def frases_cliente(pron):
    """Frases para el cliente a partir del pronostico mensual (temporada de lluvias y temporada seca)."""
    pico = pron.loc[pron["pronostico_mm"].idxmax()]
    lluvioso = pron[pron["pronostico_mm"] >= 100]
    seco = pron[pron["pronostico_mm"] < 100]
    frases = [
        f"El mes más lluvioso del pronóstico es {nombre_mes(pico['mes'])}: se esperan alrededor de "
        f"{pico['pronostico_mm']:.0f} mm en el municipio de Colima (rango probable de {pico['minimo_95_mm']:.0f} a "
        f"{pico['maximo_95_mm']:.0f} mm). Conviene reservar toldos y personal con anticipación para esa temporada."
    ]
    if len(lluvioso):
        frases.append(
            f"De {nombre_mes(lluvioso['mes'].iloc[0])} a {nombre_mes(lluvioso['mes'].iloc[-1])} se esperan más de "
            f"100 mm al mes: es la temporada de mayor riesgo para eventos al aire libre.")
    if len(seco):
        frases.append(
            f"En los meses secos ({nombre_mes(seco['mes'].iloc[0])} a {nombre_mes(seco['mes'].iloc[-1])}) se espera "
            f"poca lluvia (hasta {seco['pronostico_mm'].max():.0f} mm al mes), pero el rango es amplio y no descarta "
            f"lluvias aisladas: para una fecha concreta, revise el pronóstico de 7 días.")
    return frases


def pronostico_7_dias(raiz=RAIZ):
    """Ultimo pronostico de 7 dias de Open-Meteo guardado en Bronce, una fila por municipio y dia."""
    carpetas = sorted((Path(raiz) / "data" / "bronce" / "openmeteo_forecast").glob("fecha_captura=*"))
    if not carpetas:
        return pd.DataFrame(), None
    filas, captura = [], None
    for ruta in sorted(carpetas[-1].glob("*.json")):
        sobre = json.loads(ruta.read_text(encoding="utf-8"))
        diario = sobre["respuesta"].get("daily", {})
        captura = max(captura or "", sobre["meta"]["fecha_captura_utc"])
        for i, dia in enumerate(diario.get("time", [])):
            filas.append({"municipio": NOMBRE.get(sobre["meta"]["municipio"], sobre["meta"]["municipio"]),
                          "fecha": dia,
                          "lluvia_mm": diario["precipitation_sum"][i],
                          "tmax_c": diario["temperature_2m_max"][i],
                          "viento_max_kmh": diario["wind_speed_10m_max"][i]})
    df = pd.DataFrame(filas)
    if not df.empty:
        df = df.drop_duplicates(subset=["municipio", "fecha"], keep="last")
    return df, captura


def indicadores_calidad(raiz=RAIZ):
    """Numeros de confianza para el cliente: disponibilidad, cuarentena y ultimo dato."""
    raiz = Path(raiz)
    fiab = json.loads((raiz / "docs" / "E1" / "fiabilidad.json").read_text(encoding="utf-8"))
    cuarentena = pd.read_csv(raiz / "data" / "cuarentena" / "cuarentena.csv")
    plata = pd.read_csv(raiz / "data" / "plata" / "clima_diario.csv.gz", usecols=["fecha"])
    return {
        "disponibilidad_desde_correccion": fiab["desde_correccion"]["disponibilidad"],
        "ultima_corrida_utc": fiab["desde_correccion"]["hasta"],
        "registros_cuarentena": len(cuarentena),
        "registros_plata": len(plata),
        "ultimo_dia_con_dato": str(plata["fecha"].max())[:10],
    }
