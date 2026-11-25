"""Pipeline completo: Bronce -> Plata (con puerta de calidad y cuarentena) -> Oro.

Uso:  python -m pipeline.ejecutar
Escribe:
  data/plata/clima_diario.csv.gz       (comprimido; pandas lo lee directo)
  data/cuarentena/cuarentena.csv       (registros rechazados con su motivo)
  data/oro/clima_municipio_mes.csv, data/oro/clima_zona_mes.csv, data/oro/diccionario_datos.md
  docs/E1/reporte_pipeline.md          (numeros de cada corrida, para la evidencia)
"""
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from pipeline import bronce_a_plata as bp
from pipeline import plata_a_oro as po
from pipeline import puerta_calidad as pc

RAIZ = Path(__file__).resolve().parent.parent


def correr(raiz=RAIZ):
    raiz = Path(raiz)
    r = {"inicio": datetime.now(timezone.utc).isoformat(timespec="seconds")}

    om = bp.leer_openmeteo("openmeteo_archive", raiz)
    nasa = bp.leer_nasa(raiz)
    r["om_leidos"], r["nasa_leidos"] = len(om), len(nasa)
    r["nasa_faltantes_crudos"] = int(nasa["nasa_lluvia_mm"].isna().sum())
    om, r["om_duplicados"] = bp.quitar_duplicados(om)
    nasa, r["nasa_duplicados"] = bp.quitar_duplicados(nasa)
    r["nasa_faltantes"] = {c: int(nasa[c].isna().sum()) for c in bp.COLUMNAS_NASA.values()}
    r["nasa_registros"] = len(nasa)

    integrada = bp.integrar(om, nasa)
    r["integrados"] = len(integrada)
    r["sin_pareja_nasa"] = int(integrada["nasa_lluvia_mm"].isna().sum())

    aprobados, cuarentena = pc.aplicar_reglas(integrada)
    r["aprobados"], r["cuarentena"] = len(aprobados), len(cuarentena)
    r["motivos"] = cuarentena["motivo"].value_counts().to_dict() if len(cuarentena) else {}

    plata = pc.marcar_atipicos(aprobados)
    plata = po.discretizar(plata)
    r["atipicos"] = {c: int(plata[c].sum()) for c in plata.columns if c.startswith("atipico_")}
    r["esquema_pandera"] = pc.validar_esquema(plata)

    oro_mun = po.a_mensual(plata, por=("municipio",))
    oro_zona = po.a_mensual(plata, por=("zona",))
    r["oro_municipio_mes"], r["oro_zona_mes"] = len(oro_mun), len(oro_zona)

    for carpeta in ["plata", "cuarentena", "oro"]:
        (raiz / "data" / carpeta).mkdir(parents=True, exist_ok=True)
    plata.to_csv(raiz / "data/plata/clima_diario.csv.gz", index=False, date_format="%Y-%m-%d")
    cuarentena.to_csv(raiz / "data/cuarentena/cuarentena.csv", index=False, date_format="%Y-%m-%d")
    oro_mun.to_csv(raiz / "data/oro/clima_municipio_mes.csv", index=False)
    oro_zona.to_csv(raiz / "data/oro/clima_zona_mes.csv", index=False)
    (raiz / "data/oro/diccionario_datos.md").write_text(po.DICCIONARIO, encoding="utf-8")
    escribir_reporte(raiz, r, plata, nasa, oro_mun)
    return r


def escribir_reporte(raiz, r, plata, nasa, oro_mun):
    # Faltantes de NASA segun antiguedad del dato (para diagnosticar el mecanismo)
    hoy = plata["fecha"].max()
    reciente = nasa["fecha"] > hoy - pd.Timedelta(days=30)
    pct_rec = nasa.loc[reciente, "nasa_lluvia_mm"].isna().mean() * 100 if reciente.any() else 0
    pct_ant = nasa.loc[~reciente, "nasa_lluvia_mm"].isna().mean() * 100
    norm = po.normalizar(oro_mun[oro_mun["mes_completo"]], ["lluvia_total_mm", "tmax_media_c"])
    reduccion = (1 - len(oro_mun) / len(plata)) * 100
    cat = plata["categoria_lluvia"].value_counts().to_dict()
    pandera = {True: "aprobado (100 %)", False: "FALLO", None: "no se ejecuto (pandera no instalado)"}

    texto = f"""# Reporte del pipeline Bronce -> Plata -> Oro

Generado automaticamente el {r['inicio']} por `python -m pipeline.ejecutar`.

## Lectura y duplicados
| Fuente | Registros leidos | Duplicados eliminados (se conserva la captura mas reciente) | Registros unicos |
|---|---|---|---|
| Open-Meteo (principal) | {r['om_leidos']} | {r['om_duplicados']} | {r['om_leidos'] - r['om_duplicados']} |
| NASA POWER (comparacion) | {r['nasa_leidos']} | {r['nasa_duplicados']} | {r['nasa_registros']} |

## Valores faltantes
Open-Meteo: 0 faltantes en las variables principales.
NASA POWER marca con -999 los dias que aun no procesa. En los archivos crudos hay {r['nasa_faltantes_crudos']} dias con -999 en lluvia; al conservar solo la captura mas reciente de cada dia quedan {r['nasa_faltantes']['nasa_lluvia_mm']} (las capturas posteriores ya traen el dato). Faltantes finales por variable: {r['nasa_faltantes']}.
De los dias de NASA de los ultimos 30 dias falta el {pct_rec:.1f} %; de los anteriores, el {pct_ant:.1f} %.
El faltante depende de la fecha (NASA publica con retraso), por lo que se clasifica como **MAR** (falta por una variable observada, la antiguedad).
Tratamiento: **no se rellena**; la serie principal (Open-Meteo) esta completa y NASA solo se usa para comparar.

## Integracion
Union por municipio y fecha (Open-Meteo manda). Registros integrados: {r['integrados']}. Dias sin dato de NASA: {r['sin_pareja_nasa']}.
Conflictos resueltos: nombres de variables distintos, fechas `AAAAMMDD` vs `AAAA-MM-DD`, viento de NASA en m/s convertido a km/h (x 3.6) y duplicados por capturas repetidas.

## Puerta de calidad
Aprobados: {r['aprobados']} · En cuarentena: {r['cuarentena']} · Motivos: {r['motivos'] or 'ninguno'}
Esquema pandera de Plata: {pandera[r['esquema_pandera']]}.

## Atipicos (marcados, no eliminados)
Z-score robusto por municipio y mes del ano, umbral 3.5: {r['atipicos']}

## Discretizacion de la lluvia diaria
{cat}

## Reduccion
De {len(plata)} registros diarios a {len(oro_mun)} registros mensuales: reduccion del {reduccion:.1f} %.
Se pierde la variacion dentro del mes (dias exactos e intensidad diaria); se conservan dias de lluvia y lluvia maxima diaria.

## Normalizacion (meses completos, municipio-mes)
| Columna | min-max: minimo a maximo | z-score: media y desviacion |
|---|---|---|
| lluvia_total_mm | {norm['lluvia_total_mm_minmax'].min():.2f} a {norm['lluvia_total_mm_minmax'].max():.2f} (mediana {norm['lluvia_total_mm_minmax'].median():.3f}) | {norm['lluvia_total_mm_z'].mean():.2f} y {norm['lluvia_total_mm_z'].std(ddof=0):.2f} (max {norm['lluvia_total_mm_z'].max():.2f}) |
| tmax_media_c | {norm['tmax_media_c_minmax'].min():.2f} a {norm['tmax_media_c_minmax'].max():.2f} (mediana {norm['tmax_media_c_minmax'].median():.3f}) | {norm['tmax_media_c_z'].mean():.2f} y {norm['tmax_media_c_z'].std(ddof=0):.2f} (max {norm['tmax_media_c_z'].max():.2f}) |

Interpretacion: con min-max, un solo mes extremo fija el maximo y la mayoria de los meses quedan apretados cerca de 0 (mediana de la lluvia {norm['lluvia_total_mm_minmax'].median():.3f}); el z-score conserva la forma y deja ver que hay meses a mas de 4 desviaciones. Para comparar variables en PCA (E3) se usara z-score.

## Salidas
Plata: {len(plata)} registros · Oro municipio-mes: {r['oro_municipio_mes']} · Oro zona-mes: {r['oro_zona_mes']}
"""
    (raiz / "docs" / "E1").mkdir(parents=True, exist_ok=True)
    (raiz / "docs/E1/reporte_pipeline.md").write_text(texto, encoding="utf-8")


if __name__ == "__main__":
    resultado = correr()
    print(resultado)
    sys.exit(1 if resultado["esquema_pandera"] is False else 0)
