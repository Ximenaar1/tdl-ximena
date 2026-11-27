# Fiabilidad y disponibilidad de la captura (E1 · Calidad)

Generado por `python -m calidad.fiabilidad` a partir de `calidad/bitacora_captura.csv` (una fila por peticion).
Horas en UTC. Meta (objetivo 1 de E0): disponibilidad >= 95 %.

## Definiciones
- **Corrida exitosa:** todas sus peticiones terminaron "ok".
- **Falla:** paso de funcionando a fallando; varias corridas fallidas seguidas cuentan como una sola falla.
- **Reparacion:** termina con la siguiente corrida exitosa.
  Tiempo caido = de la primera corrida fallida a esa reparacion.
- **MTBF** = horas funcionando / fallas · **MTTR** = horas caido / fallas · **A** = MTBF / (MTBF + MTTR).
  Cuando no hay fallas, MTBF y MTTR no estan definidos; la disponibilidad es 100 % del tiempo observado.

## Resultados
| Periodo | Ventana (UTC) | Corridas exitosas | Peticiones ok | Fallas | MTBF | MTTR | Disponibilidad (cumple meta) |
|---|---|---|---|---|---|---|---|
| Periodo completo | 2026-11-11 22:34 a 2026-11-27 08:24 | 29/37 (78.4 %) | 759/1081 (70.2 %) | 2 | 150.9 h | 34.01 h | 81.61 % (no) |
| Desde la correccion (14-nov) | 2026-11-14 05:13 a 2026-11-27 08:24 | 29/31 (93.5 %) | 759/761 (99.7 %) | 2 | 150.9 h | 6.68 h | 95.76 % (si) |
| Ultimos 14 dias | 2026-11-13 19:39 a 2026-11-27 08:24 | 29/32 (90.6 %) | 759/781 (97.2 %) | 2 | 150.9 h | 11.47 h | 92.94 % (no) |
| Antes de la entrega E1 (hasta 13-nov 17:59) | 2026-11-11 22:34 a 2026-11-13 19:39 | 0/6 (0.0 %) | 0/320 (0.0 %) | 1 | 0.0 h | 45.08 h | 0.0 % (no) |

Episodios de falla en el periodo completo:
- 2026-11-11 22:34 -> 2026-11-14 05:24: 54.84 h
- 2026-11-25 08:29 -> 2026-11-25 21:40: 13.18 h

Programacion: el cron pide una corrida cada 6 h
(60 horarios desde la primera corrida incremental), pero GitHub ejecuto
33 corridas incrementales: GitHub Actions no garantiza las ejecuciones
programadas y omite o retrasa algunas cuando tiene alta demanda.
Desde la correccion: 28 corridas incrementales exitosas de
53 horarios del cron
(52.8 %).
Todas las corridas que GitHub si ejecuto desde entonces terminaron bien; las faltantes nunca se iniciaron.
