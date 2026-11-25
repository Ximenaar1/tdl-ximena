# Relatoría E1 · Observatorio de clima para eventos al aire libre en Colima

**Equipo y periodo:** Jaidy Ximena Álvarez Rocha (equipo de una persona; roles de Data Engineer y Data Statistician). Periodo de la etapa: 11 al 24 de noviembre de 2026. La fecha de entrega era el 13-nov; se entrega tarde.

## 1. Qué nos propusimos
Que los datos viajaran solos de Bronce a Oro pasando por una puerta de calidad con cuarentena; publicar un pronóstico de la lluvia mensual del municipio de Colima elegido por su error en datos de prueba; y demostrar con la bitácora qué tan disponible estuvo la captura, con un plan SQA, seguridad e integración continua.

## 2. Qué hicimos (cronología; responsable en todo: Ximena)
| Fecha | Actividad | Evidencia | Horas |
|---|---|---|---|
| 11 al 14-nov | Primeras corridas de la captura; fallan por `robots.txt` y por la cabecera User-Agent; autorización del Mtro. Román (12-nov) y corrección; captura estable desde el 14-nov 05:24 UTC | commits `564154e`, `cc00782`, `5d9a143` · defectos 1 a 3 | 13-nov: 0.75 h (14:45–15:30). Resto: [COMPLETAR] |
| 24-nov, 15:26–20:50 | Entrevista final (E0); pipeline Bronce → Plata → Oro, puerta de calidad y cuarentena; pronóstico con 4 modelos y 2 escalas | commits `1da76bc`, `cebfe91`, `6db1a6b`, `b04b6c0` | 4.8 h (5.4 h menos 37 min de interrupción estimada) |
| 24-nov, 21:12–23:10 | Reproducibilidad del pronóstico; fiabilidad (MTBF, MTTR); seguridad; requerimientos; plan SQA; corrección de la captura incremental; tablero, notebook, relatoría y ficha | commits `64512d8` a este commit | 1.35 h (2 h menos 37 min de interrupción estimada) |

## 3. Qué decidimos y por qué
- **Open-Meteo como serie principal y NASA POWER para comparar.** Open-Meteo no tiene huecos; NASA publica con retraso. Descartado: promediar ambas fuentes, porque mezclaría dos métodos de medición distintos.
- **Faltantes de NASA sin rellenar (MAR).** Faltan los días recientes (dependen de la fecha). Descartado: imputar con media o con KNN, porque se inventarían datos que solo sirven para comparar.
- **Atípicos marcados, no borrados** (Z-score robusto por municipio y mes, umbral 3.5). Un día extremo de lluvia es justo lo que le importa al cliente. Solo lo físicamente imposible va a cuarentena.
- **Formato CSV** por legibilidad; la comparación CSV contra Parquet queda como factor del experimento de E2.
- **Pronóstico a 12 meses** (la propuesta decía 6) para cubrir la temporada de lluvias completa; **dos escalas** (mm y log) porque la lluvia es muy asimétrica. Gana el **menor MAE en mm**: SARIMA(0,0,0)x(0,1,1,12) con 44.1 mm. Descartado: elegir por AIC, porque no es comparable entre familias de modelos ni entre escalas.
- **Disponibilidad reportada de dos formas**: 99.9 % sobre corridas ejecutadas desde el 14-nov y 53.5 % sobre los horarios del cron, porque GitHub no ejecutó 20 de 43 horarios. Descartado: reportar solo la cifra favorable.
- **Tablero en Streamlit Community Cloud**, porque es gratuito, queda con URL pública y lee los datos que los flujos actualizan solos.

## 4. Qué salió mal y cómo lo corregimos
- **Defectos 1 y 2** (`robots.txt` y cabecera User-Agent): 54.8 h de caída de la captura entre el 11 y el 14-nov. Corregidos con la excepción autorizada y la limpieza del contacto (AC-01 y AC-02).
- **Defectos 4 a 7** (Git, 11-nov): comandos sin `git init`, errata en un commit, *push* sin conexión y repositorio no creado; de 5 a 6 min cada uno.
- **Defecto 8:** Holt-Winters daba resultados distintos con datos idénticos (AIC 697.1 contra 700.1). Se corrigió con inicialización heurística, un solo hilo de cálculo y versiones exactas; dos corridas posteriores salieron idénticas (33 min).
- **Defecto 9:** la captura incremental no actualizaba la serie principal; Oro solo llegaba al 7-nov. Se agregó una ventana móvil de 14 días; la corrida `45548559868` trajo 30/30 peticiones y Plata llegó al 18-nov (14 min).
- **Hallazgo abierto (AC-03):** GitHub omite cerca de la mitad de las corridas programadas. Se propone ajustar el cron a 12 h y medir de nuevo en E3.
- La entrega salió tarde: E1 vencía el 13-nov.

## 5. Qué aprendimos
**Ingeniería de Datos.** Una captura que "corre en verde" no garantiza que lleguen datos nuevos: hasta el 24-nov, la serie principal llevaba 10 días sin actualizarse aunque todas las corridas eran exitosas (defecto 9). Revisar qué fechas trae cada capa es tan importante como revisar que el flujo no falle.

**Análisis Estadístico.** El modelo más sofisticado no siempre gana: Holt-Winters parecía mejor en una corrida (MAE 43.7) solo por dónde terminó el optimizador; con un ajuste reproducible quedó en 50.0 y ganó SARIMA (44.1). También aprendí a reportar con honestidad la limitación de los residuos no normales (Shapiro p ≈ 0): en la temporada seca el intervalo de predicción va de 0 a casi 200 mm.

**Calidad.** Medir con la bitácora en lugar de suponer cambia la conclusión: la misma captura tiene 82.4 %, 99.9 % o 53.5 % de disponibilidad según el periodo y el denominador. Por eso la definición de la métrica tiene que quedar escrita antes de medir (objetivo 1 de E0).

## 6. Evidencias
Pipeline: `pipeline/`, `docs/E1/reporte_pipeline.md`, `docs/E1/limpieza.ipynb` · Pronóstico: `docs/E1/pronostico.md` · Tablero: https://clima-eventos-colima.streamlit.app/ · Fiabilidad: `docs/E1/fiabilidad.md` · Seguridad y cobertura: `docs/E1/seguridad/README.md` · Requerimientos: `docs/E1/requerimientos.md` · Plan SQA: `docs/plan-sqa.md` · PSP: `calidad/tiempo-ximena.csv`, `calidad/defectos-ximena.csv`.

## Uso de IA generativa
Claude (Anthropic): guía de Git y GitHub, diagnóstico de las corridas, código del pipeline, de la puerta de calidad, del pronóstico, de la fiabilidad, de la seguridad y del tablero, redacción de borradores de documentos y explicación de los resultados. Las decisiones de método y datos las tomé yo después de revisar las opciones. Los archivos subidos el 18-nov se hicieron con otra herramienta de IA. Todos los números salen de ejecutar el código del repositorio.
