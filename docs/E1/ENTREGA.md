# Entrega E1 · Observatorio de clima para eventos al aire libre en Colima

Equipo: Jaidy Ximena Álvarez Rocha (equipo de una persona) · Etiqueta: `e1` · Tablero: [COMPLETAR: URL de Streamlit]

La Mtra. Isis no tiene cuenta de GitHub, así que no se pudo agregar como colaboradora; el repositorio es público y se revisa con el enlace.

## Resumen en tres líneas
Los datos de Open-Meteo y NASA POWER viajan solos de Bronce a Oro después de cada captura, pasan por una puerta de calidad de 7 reglas más un esquema pandera (0 registros en cuarentena; las pruebas demuestran que sí rechaza con su motivo) y quedan con linaje hasta su archivo de Bronce. El pronóstico de lluvia mensual del municipio de Colima se eligió entre 8 candidatos por su error en los 12 meses de prueba: SARIMA(0,0,0)x(0,1,1,12), MAE 44.1 mm; es reproducible y se publica a 12 meses con intervalo del 95 %. La captura tuvo 99.9 % de disponibilidad desde su corrección (82.4 % en el periodo completo; 53.5 % sobre los horarios del cron), con seguridad, plan SQA e integración continua.

## Ingeniería de Datos
| Criterio de la rúbrica | Evidencia | Nota del equipo |
|---|---|---|
| Valores faltantes (MCAR/MAR/MNAR y tratamiento) | [limpieza.ipynb §2](limpieza.ipynb), [reporte_pipeline.md](reporte_pipeline.md) | Open-Meteo sin faltantes; NASA con faltantes MAR (dependen de la fecha), no se rellenan |
| Atípicos y ruido | [limpieza.ipynb §6](limpieza.ipynb), [puerta_calidad.py](../../pipeline/puerta_calidad.py) | Z-score robusto por municipio y mes; se marcan sin borrarse; lo imposible va a cuarentena |
| Normalización, discretización y reducción | [limpieza.ipynb §7–9](limpieza.ipynb), [plata_a_oro.py](../../pipeline/plata_a_oro.py) | Min-max contra z-score (se usará z-score en E3); 5 categorías de lluvia; jerarquías municipio → zona → estado y día → mes → temporada → año; reducción del 96.7 % |
| Integración de fuentes | [limpieza.ipynb §3–4](limpieza.ipynb), [bronce_a_plata.py](../../pipeline/bronce_a_plata.py) | Nombres, fechas `AAAAMMDD`, viento m/s → km/h, -999 → vacío, duplicados (se conserva la captura más reciente) |
| Puerta de calidad automática con cuarentena | [puerta_calidad.py](../../pipeline/puerta_calidad.py), [cuarentena.csv](../../data/cuarentena/cuarentena.csv), [ci.yml](../../.github/workflows/ci.yml) | 7 reglas + esquema pandera; corre en cada captura y en cada *push* |
| Capas Plata y Oro automáticas con diccionario | [captura.yml](../../.github/workflows/captura.yml), [data/oro](../../data/oro/), [diccionario_datos.md](../../data/oro/diccionario_datos.md) | Desde el 25-nov la captura también actualiza la serie principal (AC-05, defecto 9) |

## Análisis Estadístico
| Criterio de la rúbrica | Evidencia | Nota del equipo |
|---|---|---|
| Caracterización y descomposición | [pronostico.md §1](pronostico.md) | Aditiva (hay meses con 0 mm); la estacionalidad explica ≈ 79 % de la variación |
| Estacionariedad, ACF/PACF y correlación cruzada | [pronostico.md §2](pronostico.md) | ADF p ≈ 0 → d = 0; D = 1 (s = 12); radiación solar 4 meses antes: r = 0.79 |
| Cuatro modelos con parámetros justificados | [pronostico.md §3](pronostico.md), [pronostico.py](../../laboratorio/pronostico.py) | SES, Holt, Holt-Winters y SARIMA (órdenes por AIC), en escala mm y log |
| Selección por error en prueba (MAE, RMSE, MAPE) | [pronostico.md §3](pronostico.md) | Gana el menor MAE en mm: SARIMA 44.1 mm; reproducible (§6) |
| Pronóstico en el tablero con intervalo, frase y residuos | [tablero/app.py](../../tablero/app.py), [pronostico.md §4–5](pronostico.md) | Ljung-Box p = 0.83, Levene p = 0.35; residuos no normales (se informa que el intervalo de la temporada seca es muy amplio) |

## Calidad en los Sistemas de Información
| Criterio de la rúbrica | Evidencia | Nota del equipo |
|---|---|---|
| Fiabilidad y disponibilidad medidas | [fiabilidad.md](fiabilidad.md), [fiabilidad.py](../../calidad/fiabilidad.py) | Desde el 14-nov: MTBF 257 h, MTTR 0.18 h, A = 99.9 %. Periodo completo: 82.4 %. Sobre horarios del cron: 53.5 % (AC-03 abierta) |
| Seguridad | [seguridad/README.md](seguridad/README.md), [seguridad.yml](../../.github/workflows/seguridad.yml) | 0 secretos (gitleaks), 0 vulnerabilidades (pip-audit), tokens con mínimo permiso, respaldo de Bronce restaurado idéntico |
| Requerimientos verificables | [requerimientos.md](requerimientos.md) | 11 RF y 9 RNF, cada uno con su prueba o demostración |
| Plan SQA (IEEE 730) | [plan-sqa.md](../plan-sqa.md) | Equipo de una persona: sin *Quality Lead*; se compensa con integración continua e issues de los docentes |
| Integración continua | [ci.yml](../../.github/workflows/ci.yml), [cobertura.txt](seguridad/cobertura.txt) | ruff + 33 pruebas + puerta pandera + gitleaks en cada *push*; cobertura del 65 % |

## Relatoría de etapa
[docs/relatoria-E1.md](../relatoria-E1.md)

## Issues de la entrega anterior
[COMPLETAR: issues abiertos por los docentes sobre E0 y el commit que cierra cada uno; si no hubo, escribir "No se recibieron issues sobre E0".]
