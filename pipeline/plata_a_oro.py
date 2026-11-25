"""Plata -> Oro: discretizacion, jerarquias, agregacion mensual (reduccion) y normalizacion.

- Discretizacion de la lluvia diaria (definicion del proyecto; un "dia de lluvia" es >= 1 mm, criterio OMM).
- Jerarquias: dia -> mes -> temporada -> ano y municipio -> zona -> estado.
- Reduccion: de registros diarios a mensuales (se pierde la variacion dentro del mes).
- Normalizacion min-max y z-score (para comparar variables en escalas distintas en E3).
"""
import pandas as pd

from extractores.municipios import MUNICIPIOS

ZONA = {m["clave"]: m["zona"] for m in MUNICIPIOS}
NOMBRE = {m["clave"]: m["nombre"] for m in MUNICIPIOS}

CORTES_LLUVIA = [-0.01, 1, 10, 30, 60, float("inf")]
ETIQUETAS_LLUVIA = ["sin lluvia", "ligera", "moderada", "fuerte", "muy fuerte"]
MESES_LLUVIAS = {6, 7, 8, 9, 10}


def discretizar(plata):
    plata = plata.copy()
    plata["categoria_lluvia"] = pd.cut(plata["lluvia_mm"], CORTES_LLUVIA, labels=ETIQUETAS_LLUVIA).astype(str)
    plata["zona"] = plata["municipio"].map(ZONA)
    plata["mes"] = plata["fecha"].dt.to_period("M").astype(str)
    plata["temporada"] = plata["fecha"].dt.month.map(lambda m: "lluvias" if m in MESES_LLUVIAS else "secas")
    plata["anio"] = plata["fecha"].dt.year
    return plata


def a_mensual(plata, por=("municipio",)):
    """Agrega por mes. por=('municipio',) o ('zona',). Marca si el mes esta completo."""
    claves = list(por) + ["mes"]
    g = plata.groupby(claves)
    oro = g.agg(
        lluvia_total_mm=("lluvia_mm", "sum"),
        dias_lluvia=("lluvia_mm", lambda s: int((s >= 1).sum())),
        lluvia_max_dia_mm=("lluvia_mm", "max"),
        tmax_media_c=("tmax_c", "mean"),
        tmin_media_c=("tmin_c", "mean"),
        tmed_media_c=("tmed_c", "mean"),
        viento_max_medio_kmh=("viento_max_kmh", "mean"),
        radiacion_media_mj_m2=("radiacion_mj_m2", "mean"),
        et0_total_mm=("et0_mm", "sum"),
        nasa_lluvia_total_mm=("nasa_lluvia_mm", lambda s: s.sum(min_count=1)),
        dias_con_dato=("fecha", "nunique"),
        dias_atipicos_lluvia=("atipico_lluvia_mm", "sum"),
    ).reset_index()
    if por == ("zona",):  # promedio de los municipios de la zona por dia ya sumado: se divide
        n_mun = plata.groupby(claves)["municipio"].nunique().values
        for c in ["lluvia_total_mm", "et0_total_mm", "nasa_lluvia_total_mm", "dias_lluvia", "dias_atipicos_lluvia"]:
            oro[c] = oro[c] / n_mun
        oro["dias_con_dato"] = plata.groupby(claves)["fecha"].nunique().values
    dias_mes = pd.PeriodIndex(oro["mes"], freq="M").days_in_month
    oro["mes_completo"] = oro["dias_con_dato"] == dias_mes
    oro["temporada"] = pd.PeriodIndex(oro["mes"], freq="M").month.map(
        lambda m: "lluvias" if m in MESES_LLUVIAS else "secas")
    if "municipio" in por:
        oro.insert(1, "zona", oro["municipio"].map(ZONA))
    return oro.round(2)


def normalizar(df, columnas):
    """Agrega columnas <col>_minmax (0 a 1) y <col>_z (media 0, desv. 1)."""
    df = df.copy()
    for c in columnas:
        rango = df[c].max() - df[c].min()
        df[f"{c}_minmax"] = (df[c] - df[c].min()) / rango if rango else 0.0
        df[f"{c}_z"] = (df[c] - df[c].mean()) / df[c].std(ddof=0) if df[c].std(ddof=0) else 0.0
    return df


DICCIONARIO = """# Diccionario de datos · Capa Oro

Generado automaticamente por `pipeline/ejecutar.py`. Fuente principal: Open-Meteo (Historical Weather API); comparacion: NASA POWER.

## clima_municipio_mes.csv (una fila por municipio y mes)

| Columna | Tipo | Unidad | Descripcion |
|---|---|---|---|
| municipio | texto | - | Clave del municipio (10 municipios de Colima) |
| zona | texto | - | costa, valle o sierra (agrupacion del proyecto para E3) |
| mes | texto AAAA-MM | - | Mes calendario |
| lluvia_total_mm | decimal | mm | Suma de la lluvia diaria del mes (Open-Meteo, precipitation_sum) |
| dias_lluvia | entero | dias | Dias con lluvia >= 1 mm |
| lluvia_max_dia_mm | decimal | mm | Lluvia del dia mas lluvioso del mes |
| tmax_media_c / tmin_media_c / tmed_media_c | decimal | C | Promedio mensual de la temperatura maxima, minima y media diaria |
| viento_max_medio_kmh | decimal | km/h | Promedio mensual del viento maximo diario a 10 m |
| radiacion_media_mj_m2 | decimal | MJ/m2 | Promedio mensual de la radiacion solar diaria |
| et0_total_mm | decimal | mm | Evapotranspiracion de referencia acumulada (FAO) |
| nasa_lluvia_total_mm | decimal | mm | Lluvia del mes segun NASA POWER (vacio si NASA no tiene dato) |
| dias_con_dato | entero | dias | Dias del mes presentes en Plata |
| dias_atipicos_lluvia | entero | dias | Dias marcados como lluvia atipica (Z robusto > 3.5); no se eliminaron |
| mes_completo | si/no | - | True si el mes tiene todos sus dias (el mes en curso normalmente es False) |
| temporada | texto | - | lluvias (junio a octubre) o secas |

## clima_zona_mes.csv (una fila por zona y mes)

Mismas columnas, promediando los municipios de cada zona (la lluvia es el promedio de la lluvia mensual de sus municipios).

## Linaje

Cada registro diario de Plata (`data/plata/clima_diario.csv.gz`) conserva `archivo_bronce` y `captura_utc`, que apuntan al JSON original de Bronce y a la fecha de captura.
"""
