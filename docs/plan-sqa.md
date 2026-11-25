# Plan de Aseguramiento de la Calidad del Software (SQA) · Observatorio de clima para eventos al aire libre en Colima

**Proyecto:** Trusted Data Lab · repositorio `Ximenaar1/tdl-ximena`
**Responsable:** Jaidy Ximena Álvarez Rocha (equipo de una persona)
**Estructura:** IEEE 730 (Software Quality Assurance Processes), adaptada a un observatorio de datos
**Versión:** 1.0 · 24-nov-2026 (E1)

## Introducción
Este plan describe cómo se asegura que el observatorio entregue datos y pronósticos confiables: qué se revisa, con qué herramientas, quién lo hace, qué se mide y qué pasa cuando algo falla. No es una plantilla genérica. Cada apartado indica el archivo, flujo o prueba del repositorio donde se cumple, para que cualquier revisor pueda comprobarlo. Como el proyecto lo desarrolla una sola persona, el plan se apoya sobre todo en controles **automáticos** (las tres puertas de calidad) y en revisiones **externas** (issues de los docentes y auditoría cruzada), que sustituyen a la revisión entre pares que no se puede hacer dentro del equipo.

## 1. Propósito y alcance
**Propósito:** asegurar que (a) la captura de datos sea ética, continua y medible, (b) los datos que llegan a la capa Oro sean válidos y rastreables, y (c) los hallazgos estadísticos que se publican cumplan sus supuestos y sean reproducibles.

**Alcance:** todo el código y los datos del repositorio: extractores (`extractores/`), pipeline Bronce → Plata → Oro y puerta de calidad (`pipeline/`), análisis estadístico (`laboratorio/`), métricas de calidad (`calidad/`), tablero (`tablero/`), flujos de GitHub Actions (`.github/workflows/`) y documentación de entregas (`docs/`).

**Fuera de alcance:** la exactitud de los datos de origen de Open-Meteo y NASA POWER. El proyecto mide y documenta sus diferencias, pero no puede corregirlas en la fuente.

## 2. Roles y responsabilidades
| Rol | Responsabilidad | Quién |
|---|---|---|
| Data Engineer | Captura, capas, limpieza, integración, puerta de calidad | Ximena Álvarez |
| Data Statistician | Pronóstico, experimento, análisis multivariado; verificar supuestos antes de publicar | Ximena Álvarez |
| Responsable de calidad | Mantener este plan, los registros PSP y las métricas; abrir y cerrar acciones correctivas | Ximena Álvarez |
| Quality Lead (revisión de pares) | Revisar el trabajo de otro integrante antes de integrarlo | **No aplicable**: equipo de una persona. Se compensa con la integración continua obligatoria y los issues de los docentes (§4) |
| Revisores externos | Retroalimentación por issues (máximo 3 días hábiles) | Mtro. Armando Román (`ing-datos`), Mtro. Mónico Joel Sánchez (`estadistica`), Mtra. Isis (`calidad`; no tiene cuenta de GitHub y revisa el repositorio público por enlace) |

## 3. Estándares, prácticas y métricas
**Estándares y convenciones aplicados**
- Código Python 3.11 con reglas de `ruff.toml` (líneas de 120 caracteres como máximo, sin importaciones sin usar).
- Calidad del producto con ISO/IEC 25010 y calidad de los datos con ISO/IEC 25012 (se evalúan en E2).
- Registro personal de tiempo y defectos con PSP: `calidad/tiempo-ximena.csv` y `calidad/defectos-ximena.csv`, con los tipos de defecto estándar de PSP.
- Captura ética: `robots.txt`, User-Agent con contacto y pausa mínima de 1 s por dominio (requerimientos RNF-01 y RNF-02).
- Cero datos personales (LFPDPPP).

**Métricas** (todas se calculan con datos del repositorio, ninguna se supone)
| Métrica | Meta | Cómo se mide | Valor al 24-nov-2026 |
|---|---|---|---|
| Disponibilidad de la captura | ≥ 95 % | `python -m calidad.fiabilidad` → `docs/E1/fiabilidad.md` | 99.9 % sobre corridas ejecutadas desde el 14-nov · 53.5 % sobre horarios del cron · 82.4 % en el periodo completo |
| MTBF / MTTR | — (se reportan) | mismo script | Desde el 14-nov: MTBF 257 h, MTTR 0.18 h |
| Completitud histórica | ≥ 36 meses por municipio | `python -m pipeline.verificar_bronce` | Cumple (desde 2021-01) |
| Registros en cuarentena | Cada uno con motivo | `data/cuarentena/cuarentena.csv` | 0 registros (7 reglas) |
| Pruebas automáticas | 100 % en verde | flujo `ci` | 30 pruebas, todas en verde |
| Cobertura de pruebas | ≥ 60 % (Sello TDL) | `pytest --cov` en `ci` y `seguridad` → `docs/E1/seguridad/cobertura.txt` | 65 % (punto débil: `laboratorio/pronostico.py` 23 %) |
| Secretos expuestos / vulnerabilidades | 0 / 0 | flujo `seguridad` → `docs/E1/seguridad/README.md` | 0 / 0 |
| Defectos registrados (PSP) | — (se analizan en E3) | `calidad/defectos-ximena.csv` | 9 defectos |
| Error del pronóstico (MAE en prueba) | El menor entre los candidatos | `docs/E1/pronostico.md` | 44.1 mm (SARIMA) |

## 4. Revisiones y auditorías
| Revisión | Cuándo | Qué se revisa | Evidencia |
|---|---|---|---|
| Autorrevisión antes de cada *push* | Siempre | `git pull` primero; correr `ruff check .` y `pytest`; revisar que no se suban datos personales ni secretos | Historial de commits y corridas de `ci` |
| Revisión automática (integración continua) | Cada *push* | Linter, pruebas, puerta de datos, secretos | Flujo `ci` |
| Revisión de supuestos estadísticos | Antes de publicar un hallazgo | Estacionariedad, residuos (Ljung-Box, Levene, Shapiro), supuestos de ANOVA y de normalidad multivariada | `docs/E1/pronostico.md` §5 y siguientes entregas |
| Issues de los docentes | Después de cada entrega | Hallazgos por materia; ninguno queda abierto sin respuesta antes de la siguiente entrega | Sección "Issues de la entrega anterior" en `docs/E<n>/ENTREGA.md` |
| Auditoría cruzada | 19 al 23-nov-2026 | Otro equipo audita este observatorio y viceversa; hallazgos por severidad | **No se realizó**: en ese periodo no se hizo auditoría cruzada con ningún equipo |
| Revisión de seguridad | Semanal y al cambiar dependencias | Secretos en todo el historial, vulnerabilidades, cobertura, respaldo | Flujo `seguridad` → `docs/E1/seguridad/README.md` |

## 5. Pruebas
Las pruebas son automáticas (pytest) y corren en cada *push*. No usan internet: los servidores se simulan, para que el resultado no dependa de que las APIs estén disponibles.

| Módulo | Qué se prueba | Archivo |
|---|---|---|
| Extractor ético | Bloqueo por `robots.txt`, excepción documentada, pausa mínima, User-Agent, errores HTTP | `tests/test_base.py` |
| Captura | Rangos de fechas, ≥ 36 meses, metadatos, bitácora, fallas que no detienen la captura, histórico idempotente, actualización incremental de la serie principal | `tests/test_captura.py` |
| Pipeline | Faltantes y unidades de NASA, duplicados, cuarentena con motivo, atípicos marcados, capas completas, esquema pandera | `tests/test_pipeline.py` |
| Pronóstico | Serie mensual y división entrenamiento/prueba, métricas de error, huella de reproducibilidad | `tests/test_pronostico.py` |
| Fiabilidad | Episodios de falla, MTBF/MTTR, falla abierta | `tests/test_fiabilidad.py` |
| Respaldo | Restauración idéntica y detección de archivos alterados | `tests/test_respaldo.py` |

Además de las pruebas unitarias, la puerta de datos se ejecuta sobre los **datos reales** en cada corrida de `ci` y de `captura`. Cada requerimiento de `docs/E1/requerimientos.md` está ligado a su prueba o demostración.

## 6. Reporte de problemas y acciones correctivas
**Sistema de reporte:** todo defecto encontrado se registra en `calidad/defectos-ximena.csv` (número, fecha, tipo PSP, fase en que se introdujo y fase en que se eliminó, minutos de corrección, origen y descripción con su evidencia). Los incidentes externos, como una falla de la API, se registran como tipo *entorno*. Los hallazgos de los docentes llegan como issues y se cierran con el commit que los atiende.

**Flujo:** detectar → registrar el defecto → corregir → verificar con una prueba o con una corrida → cerrar con el commit enlazado.

| Acción | Problema | Acción tomada | Evidencia | Estado |
|---|---|---|---|---|
| AC-01 | El extractor se bloqueaba por `robots.txt` en las APIs (defecto 1) | Autorización del docente del 12-nov y excepción limitada a 3 APIs documentadas | Defecto 1 · `tests/test_base.py` | Cerrada |
| AC-02 | Cabecera User-Agent inválida (defecto 2) | Limpieza del valor de contacto | Defecto 2 · `test_contacto_con_salto_de_linea_se_limpia` | Cerrada |
| AC-03 | GitHub ejecutó 23 de 43 horarios del cron desde el 14-nov; la disponibilidad sobre corridas programadas es 53.5 % | Propuesta: ajustar el cron a la frecuencia que GitHub realmente cumple (cada 12 h) y redefinir el objetivo 1 sobre esa frecuencia; medir de nuevo en E3 | `docs/E1/fiabilidad.md` | **Abierta** |
| AC-04 | Holt-Winters daba resultados distintos con datos idénticos (defecto 8) | Inicialización heurística, un solo hilo y versiones exactas | Commits `64512d8` y `7b417cf` · corridas `analisis` #3 y #4 idénticas | Cerrada |
| AC-05 | La captura incremental solo pide el pronóstico de Open-Meteo y los últimos 10 días de NASA; la serie histórica de Open-Meteo (la principal) no se ha actualizado desde la carga del 14-nov, así que Oro no incorpora meses nuevos | El modo incremental ahora pide también los últimos 14 días consolidados del histórico de Open-Meteo (de 20 a 30 peticiones por corrida); al repetir la ventana, una corrida omitida no deja huecos | `extractores/fuentes.py` · `test_incremental_actualiza_la_serie_principal` · commit `07b4fe9` · corrida de captura `45548559868` (30/30 peticiones ok; Plata actualizada hasta el 2026-11-18) · defecto 9 | Cerrada |

## 7. Herramientas
| Herramienta | Uso |
|---|---|
| GitHub y GitHub Actions | Control de versiones; flujos `captura` (cada 6 h), `analisis`, `ci` y `seguridad` |
| ruff | Linter |
| pytest, pytest-cov | Pruebas automáticas y cobertura |
| pandera | Validación de esquema de la capa Plata (puerta 1) |
| gitleaks | Búsqueda de secretos en el historial |
| pip-audit | Vulnerabilidades conocidas en dependencias |
| statsmodels, SciPy | Modelos de pronóstico y pruebas de supuestos (puerta 3) |
| Streamlit | Tablero (en construcción) |

## 8. Control de versiones y de configuración
- Rama única `main`. Cada entrega se congela con una etiqueta (`e0` … `e4`).
- Los bots de `captura` y `analisis` hacen commits automáticos; por eso, antes de cada cambio manual se ejecuta primero `git pull`.
- Las librerías que producen resultados numéricos tienen versión exacta en `requirements.txt`. Cada corrida del pronóstico guarda la huella SHA-256 de los datos y las versiones usadas.
- Bronce (la única capa que no se puede regenerar) se versiona en Git y además se respalda como artefacto de GitHub Actions durante 90 días, con prueba de restauración (`pipeline/respaldo_bronce.py`).
- Los tokens de los flujos tienen el mínimo permiso: lectura en `ci`; escritura solo en `captura`, `analisis` y `seguridad`, que guardan resultados en el repositorio.

## 9. Riesgos
| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Una API cambia su formato, sus límites o sus términos | Media | Alto | Bitácora por petición, pruebas con respuestas simuladas, términos revisados el 13 y 18-nov; segunda fuente para comparar |
| GitHub omite ejecuciones programadas | Alta (observada) | Medio | Medición en `docs/E1/fiabilidad.md`; acción AC-03; las consultas incrementales repiten los últimos 14 días (Open-Meteo) y 10 días (NASA), así que una corrida omitida no deja huecos |
| Equipo de una persona: sin revisión de pares | Cierta | Medio | Integración continua obligatoria e issues de los docentes (la auditoría cruzada del 19 al 23-nov no se realizó) |
| Atraso en las entregas (E0 a E2 entregadas tarde) | Alta | Alto | Priorizar los criterios de mayor peso de cada rúbrica; registrar el tiempo real en PSP |
| Resultados no reproducibles | Baja (corregido) | Alto | Versiones exactas, huella de datos, inicialización fija (AC-04) |
| Exposición de secretos o datos personales | Baja | Alto | No se usan llaves; gitleaks en cada *push*; diccionario de datos sin datos personales |
