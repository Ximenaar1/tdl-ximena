"""Definicion de peticiones de cada fuente. Funciones puras: no hacen red."""
from datetime import date, timedelta
from urllib.parse import urlencode

from .municipios import MUNICIPIOS

INICIO_HISTORICO = date(2021, 1, 1)   # >= 36 meses
REZAGO_DIAS = 7                       # la historia reciente tarda unos dias en consolidarse

OM_ARCHIVE = "https://archive-api.open-meteo.com/v1/archive"
OM_FORECAST = "https://api.open-meteo.com/v1/forecast"
OM_DIARIAS = ("temperature_2m_max,temperature_2m_min,temperature_2m_mean,precipitation_sum,"
              "rain_sum,wind_speed_10m_max,shortwave_radiation_sum,et0_fao_evapotranspiration")
NASA = "https://power.larc.nasa.gov/api/temporal/daily/point"
# Nombres de parametros de NASA POWER: confirmar en la primera corrida (ver bitacora de captura).
NASA_PARAMS = "T2M_MAX,T2M_MIN,PRECTOTCORR,WS10M_MAX,ALLSKY_SFC_SW_DWN"


def rangos_anuales(inicio, fin):
    """Divide [inicio, fin] en tramos por anio calendario."""
    tramos, actual = [], inicio
    while actual <= fin:
        cierre = min(date(actual.year, 12, 31), fin)
        tramos.append((actual, cierre))
        actual = cierre + timedelta(days=1)
    return tramos


def peticiones(modo, hoy):
    """Genera dicts con fuente, municipio, url, inicio y fin. modo: 'historico' o 'incremental'."""
    for m in MUNICIPIOS:
        if modo == "historico":
            for ini, fin in rangos_anuales(INICIO_HISTORICO, hoy - timedelta(days=REZAGO_DIAS)):
                q = dict(latitude=m["lat"], longitude=m["lon"], start_date=ini.isoformat(),
                         end_date=fin.isoformat(), daily=OM_DIARIAS, timezone="America/Mexico_City")
                yield dict(fuente="openmeteo_archive", municipio=m["clave"], inicio=ini, fin=fin,
                           url=f"{OM_ARCHIVE}?{urlencode(q)}")
                q = dict(parameters=NASA_PARAMS, community="AG", longitude=m["lon"], latitude=m["lat"],
                         start=ini.strftime("%Y%m%d"), end=fin.strftime("%Y%m%d"), format="JSON")
                yield dict(fuente="nasa_power", municipio=m["clave"], inicio=ini, fin=fin,
                           url=f"{NASA}?{urlencode(q)}")
        else:
            q = dict(latitude=m["lat"], longitude=m["lon"], daily=OM_DIARIAS,
                     forecast_days=7, timezone="America/Mexico_City")
            yield dict(fuente="openmeteo_forecast", municipio=m["clave"], inicio=hoy,
                       fin=hoy + timedelta(days=6), url=f"{OM_FORECAST}?{urlencode(q)}")
            ini = hoy - timedelta(days=10)
            q = dict(parameters=NASA_PARAMS, community="AG", longitude=m["lon"], latitude=m["lat"],
                     start=ini.strftime("%Y%m%d"), end=(hoy - timedelta(days=1)).strftime("%Y%m%d"),
                     format="JSON")
            yield dict(fuente="nasa_power", municipio=m["clave"], inicio=ini,
                       fin=hoy - timedelta(days=1), url=f"{NASA}?{urlencode(q)}")
