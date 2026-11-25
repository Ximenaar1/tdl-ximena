# Reporte del pipeline Bronce -> Plata -> Oro

Generado automaticamente el 2026-11-25T01:36:07+00:00 por `python -m pipeline.ejecutar`.

## Lectura y duplicados
| Fuente | Registros leidos | Duplicados eliminados (se conserva la captura mas reciente) | Registros unicos |
|---|---|---|---|
| Open-Meteo (principal) | 21370 | 0 | 21370 |
| NASA POWER (comparacion) | 23670 | 2140 | 21530 |

## Valores faltantes
Open-Meteo: 0 faltantes en las variables principales.
NASA POWER marca con -999 los dias que aun no procesa. En los archivos crudos hay 460 dias con -999 en lluvia; al conservar solo la captura mas reciente de cada dia quedan 20 (las capturas posteriores ya traen el dato). Faltantes finales por variable: {'nasa_tmax_c': 20, 'nasa_tmin_c': 20, 'nasa_lluvia_mm': 20, 'nasa_viento_max_kmh': 20, 'nasa_radiacion_mj_m2': 80}.
De los dias de NASA de los ultimos 30 dias falta el 4.3 %; de los anteriores, el 0.0 %.
El faltante depende de la fecha (NASA publica con retraso), por lo que se clasifica como **MAR** (falta por una variable observada, la antiguedad).
Tratamiento: **no se rellena**; la serie principal (Open-Meteo) esta completa y NASA solo se usa para comparar.

## Integracion
Union por municipio y fecha (Open-Meteo manda). Registros integrados: 21370. Dias sin dato de NASA: 0.
Conflictos resueltos: nombres de variables distintos, fechas `AAAAMMDD` vs `AAAA-MM-DD`, viento de NASA en m/s convertido a km/h (x 3.6) y duplicados por capturas repetidas.

## Puerta de calidad
Aprobados: 21370 · En cuarentena: 0 · Motivos: ninguno
Esquema pandera de Plata: no se ejecuto (pandera no instalado).

## Atipicos (marcados, no eliminados)
Z-score robusto por municipio y mes del ano, umbral 3.5: {'atipico_tmax_c': 201, 'atipico_tmin_c': 66, 'atipico_viento_max_kmh': 283, 'atipico_lluvia_mm': 39}

## Discretizacion de la lluvia diaria
{'sin lluvia': 14773, 'ligera': 4616, 'moderada': 1640, 'fuerte': 266, 'muy fuerte': 75}

## Reduccion
De 21370 registros diarios a 710 registros mensuales: reduccion del 96.7 %.
Se pierde la variacion dentro del mes (dias exactos e intensidad diaria); se conservan dias de lluvia y lluvia maxima diaria.

## Normalizacion (meses completos, municipio-mes)
| Columna | min-max: minimo a maximo | z-score: media y desviacion |
|---|---|---|
| lluvia_total_mm | 0.00 a 1.00 (mediana 0.033) | 0.00 y 1.00 (max 4.16) |
| tmax_media_c | 0.00 a 1.00 (mediana 0.493) | -0.00 y 1.00 (max 2.64) |

Interpretacion: con min-max, un solo mes extremo fija el maximo y la mayoria de los meses quedan apretados cerca de 0 (mediana de la lluvia 0.033); el z-score conserva la forma y deja ver que hay meses a mas de 4 desviaciones. Para comparar variables en PCA (E3) se usara z-score.

## Salidas
Plata: 21370 registros · Oro municipio-mes: 710 · Oro zona-mes: 213
