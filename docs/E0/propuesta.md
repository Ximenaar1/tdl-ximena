# Propuesta del observatorio · Clima para eventos al aire libre en Colima

**Equipo:** Jaidy Ximena Álvarez Rocha · **Materias:** Ingeniería de Datos, Análisis Estadístico para Ciencia de Datos, Calidad en los Sistemas de Información · **Entrega:** E0 (etiqueta `e0`)

## 1. Introducción

Organizar un evento al aire libre implica decidir con días de anticipación cuántas mesas, sillas, toldos o ventiladores llevar, y esa decisión depende del clima: de si lloverá, de qué tan caliente estará y de si habrá viento. Los pronósticos que se consultan hoy son generales y no dicen cuánto varía el clima entre los municipios de Colima, que van del nivel del mar a zonas de sierra. Este observatorio captura de forma automática datos meteorológicos de los 10 municipios del estado, los limpia y los integra por capas, y con ellos busca responder qué tan predecible es el clima por municipio y en qué se diferencian las zonas del estado.

## 2. Ficha del observatorio

| Campo | Contenido |
|---|---|
| **Sector** | Servicios para eventos al aire libre (renta de mobiliario, salones de eventos, organizadores) |
| **Región** | Estado de Colima, México: sus 10 municipios |
| **Pregunta detonadora** | ¿Con qué anticipación y con qué margen de error se puede anticipar la lluvia y el calor que afectarán un evento al aire libre en cada municipio de Colima? |
| **Cliente potencial** | Negocios de renta de mobiliario y organizadores de eventos que deciden inventario, logística y fechas según el clima |
| **Por qué pagaría** | Una reprogramación, un toldo de más o material dañado por lluvia cuesta dinero; un reporte por zona y mes le permite decidir antes |
| **Serie histórica** | Datos diarios desde enero de 2021 (más de 36 meses) |
| **Grupos a comparar** | Tres zonas: costa, valle y sierra (ver sección 4) |

## 3. Entrevista de campo

> **Antes de entregar:** todo lo marcado `[COMPLETAR]` debe llenarse con lo que dijo la persona entrevistada. Esta sección no puede inventarse.

**Datos de la entrevista**

- Fecha y duración (mínimo 15 min): `[COMPLETAR]`
- Medio (presencial, llamada o videollamada): `[COMPLETAR]`
- Perfil de la persona (giro, años en el sector; sin nombre ni datos personales): `[COMPLETAR]`
- Autorizó que se use lo que dijo: `[COMPLETAR sí/no]`

**Las 5 preguntas y las respuestas**

1. *¿Qué decisiones de su negocio dependen del clima (lluvia, calor, viento) y con cuántos días de anticipación las toma?*
   Respuesta: `[COMPLETAR]`
2. *¿Qué le ha costado, en dinero, cancelaciones o material dañado, que el clima no saliera como esperaba? ¿Puede darme un ejemplo reciente?*
   Respuesta: `[COMPLETAR]`
3. *¿De dónde obtiene hoy el pronóstico y qué tanto confía en él? ¿Qué le falta?*
   Respuesta: `[COMPLETAR]`
4. *¿En qué meses o zonas del estado le resulta más complicado y por qué?*
   Respuesta: `[COMPLETAR]`
5. *Si existiera un reporte que le dijera qué esperar del clima por zona y por mes, ¿qué incluiría, cada cuánto lo querría y qué le parecería razonable pagar por él?*
   Respuesta: `[COMPLETAR]`

**Qué aprendimos**

`[COMPLETAR: 3 a 5 aprendizajes concretos y cómo cambian la pregunta o el diseño del observatorio.]`

## 4. Las tres preguntas analíticas

Cada pregunta corresponde a una técnica del proyecto y usa los mismos datos de la capa Oro.

**E1 · Variable a pronosticar (series de tiempo).** *¿Cuántos milímetros de lluvia acumulada habrá cada mes en el municipio de Colima durante los próximos 6 meses, y con qué intervalo de predicción?* Variable: `precipitation_sum` agregada por mes (mm), con 60 o más meses de historia. Se espera una estacionalidad marcada por la temporada de lluvias, por lo que se compararán suavizamiento exponencial simple, Holt, Holt-Winters y ARIMA/SARIMA, y se elegirá el modelo por su error (MAE, RMSE y MAPE) en datos de prueba.

**E2 · Factores a experimentar (diseño factorial).** Se elige la *ruta ingeniería*: un experimento factorial 2³ sobre el propio extractor y procesador de datos, que se corre contra copias locales de las respuestas ya guardadas en Bronce para no saturar ningún sitio. Factores propuestos: formato de escritura (CSV vs. Parquet), número de hilos de procesamiento (1 vs. 4) y método de lectura (`json` estándar vs. `pandas.read_json`). Respuestas: tiempo de procesamiento y tasa de error. La pregunta es *qué combinación de factores minimiza el tiempo sin aumentar los errores*. Los factores pueden ajustarse en E1 según lo que resulte más lento.

**E3 · Grupos multivariados (PCA y MANOVA).** *¿Difieren la zona costera, el valle y la sierra en conjunto en sus variables climáticas, y qué perfil caracteriza a cada una?* Unidad de análisis: el municipio-mes. Variables (más de 5): temperatura máxima, mínima y media, precipitación, lluvia, viento máximo, radiación solar y evapotranspiración. Agrupación inicial (a validar con la elevación que devuelve la API y con los datos): costa (Armería, Manzanillo, Tecomán), valle (Colima, Comala, Coquimatlán, Cuauhtémoc, Villa de Álvarez) y sierra (Ixtlahuacán, Minatitlán).

## 5. Plan de recopilación de datos

### 5.1 Fuentes

| | Fuente 1: Open-Meteo | Fuente 2: NASA POWER |
|---|---|---|
| **Qué ofrece** | Datos meteorológicos históricos (reanálisis) y pronóstico por coordenadas | Datos meteorológicos y de energía solar por coordenadas, orientados a agricultura |
| **Acceso** | API REST sin llave: `archive-api.open-meteo.com` (histórico) y `api.open-meteo.com` (pronóstico) | API REST sin llave: `power.larc.nasa.gov/api/temporal/daily/point` |
| **Formato** | JSON | JSON |
| **Estructura** | Arreglos paralelos `daily.time` y una lista por variable | Diccionario `properties.parameter.<variable>.<AAAAMMDD>` |
| **Frecuencia de actualización** | Diaria; el pronóstico se actualiza varias veces al día; la historia reciente tarda unos días en consolidarse | Diaria, con rezago de unos días |
| **Historia usada** | Desde 2021-01-01 | Desde 2021-01-01 |
| **Periodos** | 10 municipios × más de 2,000 días | 10 municipios × más de 2,000 días |
| **Datos personales** | Ninguno | Ninguno |

El uso de dos fuentes independientes permite, además, comparar la misma variable (por ejemplo, la precipitación) entre ellas, lo que será la base de la resolución de conflictos de la integración en E1.

### 5.2 Análisis ético y legal

| Aspecto | Open-Meteo | NASA POWER |
|---|---|---|
| **`robots.txt`** | Se descarga y se guarda en cada corrida en `docs/E0/evidencia/robots-<dominio>.txt`, con el resumen en `resumen-robots.txt`. Resultado (11-nov-2026): HTTP 200, `User-agent: *` / `Disallow: /`. Ver la sección 5.3 | Igual. Resultado (11-nov-2026): HTTP 200, `Disallow: /api/` para todos los agentes, además de bloqueos explícitos a rastreadores de IA (GPTBot, CCBot, etc.). Ver la sección 5.3 |
| **Términos de uso** | La API es gratuita para uso no comercial, con límites de uso diarios (alrededor de 10,000 llamadas al día en la capa gratuita). Términos: https://open-meteo.com/en/terms `[VERIFICAR el texto vigente y anotar la fecha de consulta]` | Datos públicos y de acceso libre; se pide reconocer a NASA POWER como fuente. Documentación y condiciones: https://power.larc.nasa.gov/docs/ `[VERIFICAR el texto vigente y anotar la fecha de consulta]` |
| **Licencia de los datos** | Creative Commons Atribución 4.0 (CC BY 4.0): se debe citar a Open-Meteo | Datos de la NASA de uso abierto con reconocimiento de la fuente |
| **Privacidad** | No hay datos de personas: solo variables meteorológicas por coordenada | No hay datos de personas |
| **Sesgos y limitaciones** | Son datos de modelos de reanálisis con malla de decenas de kilómetros, no mediciones de estación: la lluvia local y la sierra pueden estar subestimadas o suavizadas | Misma limitación por resolución espacial; las dos fuentes no son totalmente independientes porque usan modelos similares |

**Reglas del extractor:** se identifica con un *User-Agent* honesto que incluye el correo institucional y el repositorio del proyecto, descarga y evalúa `robots.txt` antes de consultar cada dominio, espera mínimo 1.5 segundos entre peticiones al mismo dominio (o el `Crawl-delay` si es mayor), reintenta con espera exponencial ante errores 429 o 5xx y registra cada petición en una bitácora. Para páginas web, si `robots.txt` prohíbe la ruta, la petición no se hace y se busca otra fuente. Para las APIs REST oficiales y documentadas, se aplica la política descrita en la sección 5.3.

**Nota sobre el uso comercial:** la gratuidad de Open-Meteo es para uso no comercial. Si el observatorio llegara a venderse como servicio, habría que contratar su plan comercial o cambiar de fuente. Esto se considerará en el modelo de negocio de E4.

### 5.3 Hallazgo de la primera corrida: bloqueo por `robots.txt` y uso legítimo de las APIs

En la primera corrida real de la captura (11 de noviembre de 2026, corrida `43112866220` de GitHub Actions), el extractor ético rechazó las 120 peticiones antes de enviarlas, con el motivo "robots.txt no permite", registrado en `calidad/bitacora_captura.csv`. La evidencia guardada en `docs/E0/evidencia/` muestra que ambos sitios responden su `robots.txt` con HTTP 200: Open-Meteo declara `Disallow: /` para todos los agentes y NASA POWER declara `Disallow: /api/`, además de bloquear de forma explícita a rastreadores de inteligencia artificial.

El Protocolo de Exclusión de Robots está dirigido a rastreadores (*crawlers*) que recorren e indexan páginas HTML. Ambas fuentes, en cambio, publican sus APIs REST precisamente para el acceso programático: Open-Meteo aparece incluso en la tabla de fuentes recomendadas del proyecto como "API sin llave". Por eso, el 11 de noviembre se consultó al docente de Ingeniería de Datos, quien el 12 de noviembre autorizó continuar con ambas APIs oficiales, con dos condiciones: un *User-Agent* personalizado con el correo institucional y los datos del proyecto, y pausas entre llamadas.

Con base en eso, el extractor distingue dos casos. En las páginas web, `robots.txt` sigue siendo obligatorio y bloquea la petición. En los dominios de APIs documentadas (`archive-api.open-meteo.com`, `api.open-meteo.com` y `power.larc.nasa.gov`), `robots.txt` se sigue descargando y guardando como evidencia en cada corrida, pero no bloquea la petición, y cada registro de la bitácora lo anota en la columna `mensaje`. La pausa mínima, el *User-Agent* y los reintentos aplican igual. El caso se registró como defecto 1 en `calidad/defectos-ximena.csv`, y el comportamiento está cubierto por pruebas automáticas (`tests/test_base.py`).

### 5.4 Captura y almacenamiento

- **Capa Bronce:** cada respuesta se guarda tal como llegó, dentro de un archivo JSON con sus metadatos (fuente, URL, fecha de captura, código HTTP, huella `sha256` y número de corrida), en `data/bronce/<fuente>/fecha_captura=<fecha>/`.
- **Captura programada:** el flujo `.github/workflows/captura.yml` corre cada 6 horas en GitHub Actions: guarda evidencia de `robots.txt`, descarga el pronóstico a 7 días (Open-Meteo) y los últimos 10 días (NASA POWER) y sube los resultados al repositorio.
- **Serie histórica inicial:** una corrida manual en modo `historico` descarga desde 2021 por tramos anuales. `pipeline/verificar_bronce.py` comprueba que cada municipio tenga al menos 36 meses.
- **Bitácora:** `calidad/bitacora_captura.csv` registra cada petición (resultado, código, tiempo). Es la base para medir disponibilidad, MTBF y MTTR en E1.

## 6. Arranque del sistema de calidad

Se abrieron `calidad/tiempo-ximena.csv` y `calidad/defectos-ximena.csv` y se definieron tres objetivos medibles (`calidad/objetivos.md`): disponibilidad de la captura de al menos 95 %, completitud de 36 o más meses en los 10 municipios y 100 % de peticiones que cumplen la política de `robots.txt` (bloqueo en páginas web y evidencia más excepción autorizada en APIs documentadas) y la pausa mínima. Al ser un equipo de una persona, la revisión de pares del *Quality Lead* no puede hacerse; se declara en la ficha de entrega.

## 7. Uso de IA generativa

Se usó Claude (Anthropic) para estructurar los documentos y escribir el código base del extractor y de las pruebas. La elección del tema, la entrevista, la revisión y la ejecución de la captura son del equipo.

## 8. Referencias

- Open-Meteo. *Historical Weather API*. https://open-meteo.com — Términos de uso: https://open-meteo.com/en/terms
- NASA. *Prediction Of Worldwide Energy Resources (POWER)*. https://power.larc.nasa.gov — Documentación: https://power.larc.nasa.gov/docs/
- IETF (2022). *RFC 9309: Robots Exclusion Protocol*. https://www.rfc-editor.org/rfc/rfc9309
- Proyecto Integrador Trusted Data Lab, Tecnológico Nacional de México (30 de octubre de 2026).
