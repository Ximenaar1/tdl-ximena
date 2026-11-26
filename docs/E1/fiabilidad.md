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
| Periodo completo | 2026-11-11 22:34 a 2026-11-26 21:29 | 28/36 (77.8 %) | 729/1051 (69.4 %) | 2 | 145.4 h | 34.01 h | 81.05 % (no) |
| Desde la correccion (14-nov) | 2026-11-14 05:13 a 2026-11-26 21:29 | 28/30 (93.3 %) | 729/731 (99.7 %) | 2 | 145.4 h | 6.68 h | 95.61 % (si) |
| Ultimos 14 dias | 2026-11-12 22:06 a 2026-11-26 21:29 | 28/33 (84.8 %) | 729/891 (81.8 %) | 2 | 145.4 h | 22.24 h | 86.74 % (no) |
| Antes de la entrega E1 (hasta 13-nov 17:59) | 2026-11-11 22:34 a 2026-11-13 19:39 | 0/6 (0.0 %) | 0/320 (0.0 %) | 1 | 0.0 h | 45.08 h | 0.0 % (no) |

Episodios de falla en el periodo completo:
- 2026-11-11 22:34 -> 2026-11-14 05:24: 54.84 h
- 2026-11-25 08:29 -> 2026-11-25 21:40: 13.18 h

Programacion: el cron pide una corrida cada 6 h
(58 horarios desde la primera corrida incremental), pero GitHub ejecuto
32 corridas incrementales: GitHub Actions no garantiza las ejecuciones
programadas y omite o retrasa algunas cuando tiene alta demanda.
Desde la correccion: 27 corridas incrementales exitosas de
51 horarios del cron
(52.9 %).
Todas las corridas que GitHub si ejecuto desde entonces terminaron bien; las faltantes nunca se iniciaron.
