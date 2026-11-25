# Diccionario de datos · Capa Oro

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
