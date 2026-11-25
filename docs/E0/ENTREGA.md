# Entrega E0 · Observatorio de clima para eventos al aire libre en Colima

Equipo: Jaidy Ximena Álvarez Rocha (equipo de una persona) · Etiqueta: `e0` · Tablero: aún no aplica (E1)

## Resumen en tres líneas

El observatorio captura clima diario de los 10 municipios de Colima desde dos fuentes (Open-Meteo y NASA POWER) hacia la capa Bronce, con un extractor ético programado cada 6 horas en GitHub Actions (en la práctica GitHub lo ejecutó cerca de 2 veces al día). La propuesta define la pregunta, el cliente y las tres preguntas analíticas para E1, E2 y E3. Se abrieron los registros de tiempo y defectos y tres objetivos de calidad medibles.

## Ingeniería de Datos

| Criterio de la rúbrica | Evidencia | Nota del equipo |
|---|---|---|
| Plan de recopilación (estructura, formato, frecuencia, `robots.txt`, términos) | [propuesta.md, sección 5](propuesta.md) y [evidencia robots](evidencia/) | `robots.txt` bloqueaba las rutas de API; hallazgo y excepción autorizada por escrito por el docente: propuesta, sección 5.2.1. Términos de uso consultados el 18-nov-2026 |
| Captura y serie histórica (2 fuentes, 1 programada, 36+ periodos) | [captura.yml](../../.github/workflows/captura.yml), [data/bronce](../../data/bronce/) | Serie desde 2021 (más de 60 meses). Evidencia: salida de `python -m pipeline.verificar_bronce` |

## Análisis Estadístico

| Criterio de la rúbrica | Evidencia | Nota del equipo |
|---|---|---|
| Pregunta y cliente | [propuesta.md, secciones 2 y 3](propuesta.md) | Entrevista a un proveedor de mobiliario y toldos de Coquimatlán (7 años): por mensaje (17 y 18-nov) y llamada de seguimiento de unos 20 min (24-nov) |
| Preguntas analíticas (E1, E2, E3) | [propuesta.md, sección 4](propuesta.md) | Factores de E2 ajustables en E1 |

## Calidad en los Sistemas de Información

| Criterio de la rúbrica | Evidencia | Nota del equipo |
|---|---|---|
| Registros de tiempo y defectos individuales | [tiempo-ximena.csv](../../calidad/tiempo-ximena.csv), [defectos-ximena.csv](../../calidad/defectos-ximena.csv) | Equipo de una persona: no hay revisión de pares (*Quality Lead*) |
| Bitácora de captura activa | [bitacora_captura.csv](../../calidad/bitacora_captura.csv) | Se genera en cada corrida |
| Tres objetivos medibles | [objetivos.md](../../calidad/objetivos.md) | Disponibilidad ≥ 95 %, completitud ≥ 36 meses, ética 100 % |

## Resultados de calidad a la fecha (18-nov-2026, según `bitacora_captura.csv`)

| Medida | Resultado |
|---|---|
| Corridas completamente exitosas, todo el periodo (11 al 18 nov) | 12 de 19 (63.2 %) |
| Peticiones exitosas desde la recuperación (14 nov, 05:24 UTC) | 221 de 221 (100 %) en 111 horas |
| Corridas incrementales exitosas | 11 de 11 (100 %) |
| Carga histórica | 60 de 60 archivos por fuente (2021 a nov 2026) |
| Defectos registrados | 3 (bloqueo por `robots.txt`, error de cabecera del User-Agent, una petición sin respuesta); ver `defectos-ximena.csv` |

El objetivo de disponibilidad ≥ 95 % no se cumple si se cuenta desde la primera corrida, por los dos defectos iniciales (54.8 horas de caída); se cumple desde la primera versión estable. Se reportan ambas cifras.

## Relatoría de etapa

No se pide en E0 (empieza en E1).

## Issues de la entrega anterior

No aplica (primera entrega).
