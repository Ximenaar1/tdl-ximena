"""Bronce -> Plata: lee los JSON crudos, los deja en tablas diarias y une las dos fuentes.

Decisiones (consultadas con la estudiante el 24-nov-2026):
- Open-Meteo es la serie principal; NASA POWER queda al lado para comparar (prefijo nasa_).
- El valor -999 de NASA significa "sin dato": se convierte en vacio (NaN) y no se rellena.
- Duplicados: si un mismo municipio-dia-fuente se capturo varias veces, se conserva la captura mas reciente.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
BRONCE = RAIZ / "data" / "bronce"

# Nombres comunes del proyecto (Open-Meteo -> nombre en Plata)
COLUMNAS_OM = {
    "temperature_2m_max": "tmax_c",
    "temperature_2m_min": "tmin_c",
    "temperature_2m_mean": "tmed_c",
    "precipitation_sum": "lluvia_mm",
    "rain_sum": "lluvia_liquida_mm",
    "wind_speed_10m_max": "viento_max_kmh",
    "shortwave_radiation_sum": "radiacion_mj_m2",
    "et0_fao_evapotranspiration": "et0_mm",
}
# NASA POWER -> nombre en Plata (con prefijo nasa_). Viento: NASA lo da en m/s.
COLUMNAS_NASA = {
    "T2M_MAX": "nasa_tmax_c",
    "T2M_MIN": "nasa_tmin_c",
    "PRECTOTCORR": "nasa_lluvia_mm",
    "WS10M_MAX": "nasa_viento_max_kmh",
    "ALLSKY_SFC_SW_DWN": "nasa_radiacion_mj_m2",
}
VALOR_FALTANTE_NASA = -999.0
MS_A_KMH = 3.6


def _sobres(fuente, raiz=RAIZ):
    for ruta in sorted((Path(raiz) / "data" / "bronce" / fuente).rglob("*.json")):
        sobre = json.loads(ruta.read_text(encoding="utf-8"))
        yield ruta, sobre["meta"], sobre["respuesta"]


def leer_openmeteo(fuente="openmeteo_archive", raiz=RAIZ):
    """Una fila por municipio-dia-captura con las variables de Open-Meteo."""
    partes = []
    for ruta, meta, resp in _sobres(fuente, raiz):
        diario = resp.get("daily", {})
        if not diario.get("time"):
            continue
        df = pd.DataFrame(diario).rename(columns={"time": "fecha", **COLUMNAS_OM})
        df["municipio"] = meta["municipio"]
        df["captura_utc"] = meta["fecha_captura_utc"]
        df["archivo_bronce"] = str(ruta.relative_to(raiz))
        partes.append(df)
    if not partes:
        return pd.DataFrame()
    df = pd.concat(partes, ignore_index=True)
    df["fecha"] = pd.to_datetime(df["fecha"], format="%Y-%m-%d")
    return df


def leer_nasa(raiz=RAIZ):
    """Una fila por municipio-dia-captura. Convierte -999 a NaN, fechas AAAAMMDD y viento m/s a km/h."""
    partes = []
    for ruta, meta, resp in _sobres("nasa_power", raiz):
        param = resp.get("properties", {}).get("parameter", {})
        if not param:
            continue
        df = pd.DataFrame(param)  # indice = fechas AAAAMMDD
        df.index.name = "fecha"
        df = df.reset_index().rename(columns=COLUMNAS_NASA)
        df["municipio"] = meta["municipio"]
        df["captura_utc"] = meta["fecha_captura_utc"]
        df["archivo_bronce_nasa"] = str(ruta.relative_to(raiz))
        partes.append(df)
    if not partes:
        return pd.DataFrame()
    df = pd.concat(partes, ignore_index=True)
    df["fecha"] = pd.to_datetime(df["fecha"], format="%Y%m%d")
    valores = list(COLUMNAS_NASA.values())
    df[valores] = df[valores].replace(VALOR_FALTANTE_NASA, np.nan)
    df["nasa_viento_max_kmh"] = df["nasa_viento_max_kmh"] * MS_A_KMH
    return df


def quitar_duplicados(df):
    """Conserva la captura mas reciente de cada municipio-dia. Devuelve (df, n_duplicados)."""
    if df.empty:
        return df, 0
    df = df.sort_values("captura_utc")
    sin_dup = df.drop_duplicates(subset=["municipio", "fecha"], keep="last")
    return sin_dup.sort_values(["municipio", "fecha"]).reset_index(drop=True), len(df) - len(sin_dup)


def integrar(om, nasa):
    """Une ambas fuentes por municipio y fecha (Open-Meteo manda: left join)."""
    nasa = nasa.drop(columns=["captura_utc"])
    plata = om.merge(nasa, on=["municipio", "fecha"], how="left", validate="one_to_one")
    plata["dif_lluvia_mm"] = plata["lluvia_mm"] - plata["nasa_lluvia_mm"]
    plata["dif_tmax_c"] = plata["tmax_c"] - plata["nasa_tmax_c"]
    return plata
