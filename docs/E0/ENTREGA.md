# Entrega E0 · Observatorio de clima para eventos al aire libre en Colima

Equipo: Jaidy Ximena Álvarez Rocha (equipo de una persona) · Etiqueta: `e0` · Tablero: aún no aplica (E1)

## Resumen en tres líneas

El observatorio captura clima diario de los 10 municipios de Colima desde dos fuentes (Open-Meteo y NASA POWER) hacia la capa Bronce, con un extractor ético programado cada 6 horas en GitHub Actions. La propuesta define la pregunta, el cliente y las tres preguntas analíticas para E1, E2 y E3. Se abrieron los registros de tiempo y defectos y tres objetivos de calidad medibles.

## Ingeniería de Datos

| Criterio de la rúbrica | Evidencia | Nota del equipo |
|---|---|---|
| Plan de recopilación (estructura, formato, frecuencia, `robots.txt`, términos) | [propuesta.md, sección 5](propuesta.md) y [evidencia robots](evidencia/) | Resultado de `robots.txt` y fecha de consulta de términos: ver `[COMPLETAR]` en la propuesta |
| Captura y serie histórica (2 fuentes, 1 programada, 36+ periodos) | [captura.yml](../../.github/workflows/captura.yml), [data/bronce](../../data/bronce/) | Serie desde 2021 (más de 60 meses). Evidencia: salida de `python -m pipeline.verificar_bronce` |

## Análisis Estadístico

| Criterio de la rúbrica | Evidencia | Nota del equipo |
|---|---|---|
| Pregunta y cliente | [propuesta.md, secciones 2 y 3](propuesta.md) | Entrevista con persona del sector |
| Preguntas analíticas (E1, E2, E3) | [propuesta.md, sección 4](propuesta.md) | Factores de E2 ajustables en E1 |

## Calidad en los Sistemas de Información

| Criterio de la rúbrica | Evidencia | Nota del equipo |
|---|---|---|
| Registros de tiempo y defectos individuales | [tiempo-ximena.csv](../../calidad/tiempo-ximena.csv), [defectos-ximena.csv](../../calidad/defectos-ximena.csv) | Equipo de una persona: no hay revisión de pares (*Quality Lead*) |
| Bitácora de captura activa | [bitacora_captura.csv](../../calidad/bitacora_captura.csv) | Se genera en cada corrida |
| Tres objetivos medibles | [objetivos.md](../../calidad/objetivos.md) | Disponibilidad ≥ 95 %, completitud ≥ 36 meses, ética 100 % |

## Relatoría de etapa

No se pide en E0 (empieza en E1).

## Issues de la entrega anterior

No aplica (primera entrega).
