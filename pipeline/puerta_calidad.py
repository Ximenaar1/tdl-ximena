"""Puerta de calidad Bronce -> Plata.

1. Reglas de negocio y rangos fisicos: cada registro que falla se manda a cuarentena con su motivo.
   Nunca se borra en silencio.
2. Atipicos: se MARCAN (no se borran) con Z-score robusto por municipio y mes del ano.
3. Esquema final con pandera: lo que queda en Plata debe pasar el 100 % de las validaciones.
"""
import numpy as np
import pandas as pd


def _fuera(d, col, minimo, maximo):
    """True donde hay valor y esta fuera del rango (los vacios se revisan en otra regla)."""
    return d[col].notna() & ~d[col].between(minimo, maximo)


# (nombre de la regla, funcion que devuelve True donde el registro FALLA)
REGLAS = [
    ("fecha o municipio vacio", lambda d: d["fecha"].isna() | d["municipio"].isna()),
    ("variable principal vacia (Open-Meteo)",
     lambda d: d[["tmax_c", "tmin_c", "lluvia_mm"]].isna().any(axis=1)),
    ("tmin mayor que tmax", lambda d: d["tmin_c"] > d["tmax_c"]),
    ("temperatura fuera de rango fisico (-10 a 50 C)",
     lambda d: _fuera(d, "tmax_c", -10, 50) | _fuera(d, "tmin_c", -10, 50)),
    ("lluvia negativa o mayor a 500 mm en un dia", lambda d: _fuera(d, "lluvia_mm", 0, 500)),
    ("viento fuera de rango fisico (0 a 250 km/h)", lambda d: _fuera(d, "viento_max_kmh", 0, 250)),
    ("radiacion fuera de rango fisico (0 a 40 MJ/m2)", lambda d: _fuera(d, "radiacion_mj_m2", 0, 40)),
]

UMBRAL_Z = 3.5  # criterio de Iglewicz y Hoaglin para el Z-score robusto


def aplicar_reglas(df):
    """Devuelve (aprobados, cuarentena). La cuarentena lleva la columna 'motivo' (una o varias reglas)."""
    motivos = pd.Series("", index=df.index)
    for nombre, falla in REGLAS:
        mascara = falla(df).fillna(False).astype(bool)
        motivos[mascara] = motivos[mascara] + nombre + "; "
    en_cuarentena = motivos != ""
    cuarentena = df[en_cuarentena].copy()
    cuarentena["motivo"] = motivos[en_cuarentena].str.rstrip("; ")
    return df[~en_cuarentena].copy(), cuarentena


def z_robusto(serie):
    """Z-score robusto (Iglewicz y Hoaglin): 0.6745 * (x - mediana) / MAD.
    Si la MAD es 0 (mas de la mitad de los valores iguales), se usa la desviacion absoluta media:
    (x - mediana) / (1.253314 * MeanAD). Si ambas son 0, todos los valores son iguales y nada es atipico."""
    mediana = serie.median()
    desvio = (serie - mediana).abs()
    mad = desvio.median()
    if mad and not np.isnan(mad):
        return 0.6745 * (serie - mediana) / mad
    mean_ad = desvio.mean()
    if mean_ad and not np.isnan(mean_ad):
        return (serie - mediana) / (1.253314 * mean_ad)
    return pd.Series(0.0, index=serie.index)


def marcar_atipicos(df):
    """Agrega columnas atipico_* (True/False). Lluvia: solo dias con lluvia y en escala log1p."""
    df = df.copy()
    grupo = [df["municipio"], df["fecha"].dt.month]
    for col in ["tmax_c", "tmin_c", "viento_max_kmh"]:
        z = df.groupby(grupo)[col].transform(z_robusto)
        df[f"atipico_{col}"] = z.abs() > UMBRAL_Z
    lluviosos = df["lluvia_mm"] >= 1
    z_lluvia = pd.Series(0.0, index=df.index)
    sub = df[lluviosos]
    z_lluvia[lluviosos] = np.log1p(sub["lluvia_mm"]).groupby(
        [sub["municipio"], sub["fecha"].dt.month]).transform(z_robusto)
    df["atipico_lluvia_mm"] = z_lluvia > UMBRAL_Z  # solo lluvia extraordinariamente alta
    return df


def esquema_plata():
    """Esquema pandera de la capa Plata (se valida en CI y en el pipeline si pandera esta instalado)."""
    try:
        import pandera.pandas as pa
    except ImportError:  # versiones anteriores de pandera
        import pandera as pa

    return pa.DataFrameSchema(
        {
            "municipio": pa.Column(str, nullable=False),
            "fecha": pa.Column("datetime64[ns]", nullable=False),
            "tmax_c": pa.Column(float, pa.Check.in_range(-10, 50)),
            "tmin_c": pa.Column(float, pa.Check.in_range(-10, 50)),
            "lluvia_mm": pa.Column(float, pa.Check.in_range(0, 500)),
            "viento_max_kmh": pa.Column(float, pa.Check.in_range(0, 250)),
            "radiacion_mj_m2": pa.Column(float, pa.Check.in_range(0, 40), nullable=True),
            "nasa_lluvia_mm": pa.Column(float, pa.Check.ge(0), nullable=True),
        },
        checks=[pa.Check(lambda d: d["tmin_c"] <= d["tmax_c"], name="tmin <= tmax")],
        unique=["municipio", "fecha"],
        coerce=True,
        strict=False,
    )


def validar_esquema(plata):
    """Valida con pandera. Devuelve True/False, o None si pandera no esta instalado."""
    try:
        esquema = esquema_plata()
    except ImportError:
        return None
    import pandera.errors as pe

    try:
        esquema.validate(plata, lazy=True)
        return True
    except pe.SchemaErrors as e:
        print(e.failure_cases.head(20))
        return False
