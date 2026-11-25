# Propuesta del observatorio · Clima para eventos al aire libre en Colima

**Autora:** Jaidy Ximena Álvarez Rocha (equipo de una persona) · **Materias:** Ingeniería de Datos, Análisis Estadístico para Ciencia de Datos, Calidad en los Sistemas de Información · **Entrega:** E0 (etiqueta `e0`)

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

**Datos de la entrevista**

- **Perfil:** propietario de un negocio de renta de mobiliario, toldos y brincolines inflables para eventos en Coquimatlán, Colima, con cerca de 7 años de operación. No se incluyen nombres ni datos personales.
- **Medio y fechas:** la entrevista se hizo en dos partes.
  1. **Por mensaje (Facebook Messenger), del 17 al 18 de noviembre de 2026.** La invitación se envió el 17-nov a las 10:00 y el entrevistado eligió responder por escrito. Las preguntas se respondieron entre el 17-nov (16:33) y el 18-nov (20:41).
  2. **Llamada telefónica de seguimiento el 24 de noviembre de 2026, a las 18:00, de unos 20 minutos** (incluidos el saludo y la explicación del proyecto). En la llamada confirmó sus respuestas escritas y amplió la pregunta 4.
- **Autorización:** sí. Autorizó por escrito usar sus respuestas en este trabajo escolar.
- **Evidencia:** la estudiante conserva las capturas del chat y el registro de la llamada. No se publican en el repositorio para proteger la identidad del negocio.

**Las 5 preguntas y las respuestas** (frases entre comillas tomadas de sus mensajes, con mínimas correcciones de ortografía)

1. *¿Qué decisiones de su negocio dependen del clima (lluvia, calor o viento) y con cuántos días de anticipación las toma?*
   "Sumamente importante checar en nuestro trabajo el clima, sobre todo en los contratos con toldos árabes, ya que la mayor parte del tiempo los ponemos con 1 día de anticipación. Si nosotros tenemos un pronóstico definido y después cambia, sí nos afecta, tanto en conformidad con el cliente como en lo económico en ocasiones."
2. *¿Qué le ha costado que el clima no saliera como esperaba, ya sea en dinero, cancelaciones o material dañado?*
   "Si nos falla, hasta en logística y tiempo nos resulta perjudicante, por el motivo de que llegan tarde los empleados." No dio un caso concreto con cifras; el impacto lo describe en logística, puntualidad del personal, conformidad del cliente y, en ocasiones, en lo económico.
3. *¿De dónde obtiene hoy el pronóstico del clima y qué tanto confía en él? ¿Qué información le hace falta?*
   "Sumamente importante para nosotros el clima que nos da Google; es ahí donde nos metemos y confiamos casi 100 %."
4. *¿En qué meses del año o en qué zonas de Colima (costa, valle o sierra) le resulta más complicado el clima para su trabajo, y por qué?*
   Por escrito: "Mayormente en valle y costa, aunque a nosotros nos afecta en valle y sierra de Coquimatlán; muy poco, pero en ocasiones." En la llamada precisó que los meses más complicados son **agosto y octubre**, porque es cuando más llueve.
5. *Si existiera un reporte que le dijera qué esperar del clima por municipio y por mes, ¿qué le gustaría que incluyera, cada cuánto lo querría y cuánto le parecería justo pagar por él?*
   "Quizás que sea más preciso. Y si se pudiera, incluir mapeos del municipio donde está lloviendo en tiempo real y con qué intensidad. Costos: yo creo que si hay un buen trabajo en la app, mínimo $199 por mes." Añadió que desconoce el tema tecnológico.

**Qué aprendimos**

- **La decisión crítica se toma con 1 día de anticipación** (instalación de toldos). Por eso, además del pronóstico mensual para planear la temporada, conviene medir qué tan bien acierta el **pronóstico de corto plazo** frente a lo que realmente ocurrió. El extractor ya captura el pronóstico a 7 días, así que esto se puede medir en las entregas siguientes.
- **Los meses críticos que señala (agosto y octubre) caen en la temporada de lluvias de junio a octubre**, lo que respalda pronosticar la lluvia mensual en E1 y verificar con los datos si esos meses son de verdad los de mayor lluvia o variabilidad.
- **La zona importa:** identifica el valle y la costa como las zonas más complicadas, con afectaciones ocasionales en la sierra de Coquimatlán. Esto respalda comparar costa, valle y sierra en E3.
- **Hoy depende de una sola fuente (Google) y confía casi por completo en ella.** Un observatorio que compare varias fuentes y comunique su margen de error aporta algo que no tiene.
- **Hay disposición a pagar** una suscripción mensual baja ($199 como referencia), lo que respalda el valor del problema para el modelo de negocio de E4. Pidió **mapas de lluvia en tiempo real**, que quedan fuera del alcance de este observatorio (datos diarios y pronóstico por municipio y mes); se registran como necesidad detectada y posible trabajo futuro.
- **Limitación:** es una sola entrevista. Sus respuestas son una opinión de caso, no una muestra representativa, y falta un ejemplo concreto de pérdida económica.

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
| **`robots.txt`** | Se descarga en cada corrida y se guarda en `docs/E0/evidencia/` (archivos `robots-<dominio>.txt` y `resumen-robots.txt`). Verificación del 18 de noviembre de 2026: el sitio respondió HTTP 200 y, según la verificación automática del extractor, las rutas `/v1/archive` y `/v1/forecast` figuran como no permitidas. | Igual. Verificación del 18 de noviembre de 2026: HTTP 200 y la ruta `/api/temporal/daily/point` figura como no permitida según la verificación automática. |
| **Términos de uso** | Consultados el 18 de noviembre de 2026 (open-meteo.com/en/terms): la API gratuita es solo para uso no comercial (se mencionan como ejemplos la investigación pública en instituciones públicas y el contenido educativo), con límite de menos de 10,000 llamadas al día, 5,000 por hora y 600 por minuto, por IP y por aplicación; pueden bloquear a quien haga mal uso del servicio. Este proyecto es académico y hace cerca de 20 peticiones por corrida. | Consultada el 18 de noviembre de 2026 la página de referencias de POWER (power.larc.nasa.gov/docs/referencing/): se pide citar el proyecto POWER en todo trabajo que use sus datos, con el nombre del servicio, la versión y la fecha de acceso, y se solicita informar a su equipo (larc-power-project@mail.nasa.gov) de los usos que se hagan. Esa página no establece condiciones de gratuidad, por lo que se cita la fuente y se mantiene un uso moderado. |
| **Licencia de los datos** | Creative Commons Atribución 4.0 (CC BY 4.0): se debe citar a Open-Meteo | Se cita siguiendo las indicaciones de POWER descritas arriba |
| **Privacidad** | No hay datos de personas: solo variables meteorológicas por coordenada | No hay datos de personas |
| **Sesgos y limitaciones** | Son datos de modelos de reanálisis con malla de decenas de kilómetros, no mediciones de estación: la lluvia local y la sierra pueden estar subestimadas o suavizadas | Misma limitación por resolución espacial; las dos fuentes no son totalmente independientes porque usan modelos similares |

**Reglas del extractor:** se identifica con un *User-Agent* honesto que incluye un contacto, verifica `robots.txt` antes de cada petición, espera mínimo 1.5 segundos entre peticiones al mismo dominio, reintenta con espera exponencial ante errores 429 o 5xx y registra cada petición en una bitácora. En las tres rutas utilizadas la verificación indicó que no están permitidas (ver 5.2.1), por lo que se aplicó la excepción documentada a continuación.

#### 5.2.1 Hallazgo: bloqueo por `robots.txt` y uso legítimo de las APIs

Durante el arranque del sistema, el extractor se bloqueaba a sí mismo: las tres primeras corridas (11 y 12 de noviembre de 2026) fallaron con el mensaje "robots.txt no permite" en las tres rutas utilizadas (140 peticiones fallidas, registradas en `calidad/bitacora_captura.csv`). La verificación automática del 18 de noviembre confirma que `robots.txt` figura como no permitidas las rutas `/v1/archive`, `/v1/forecast` y `/api/temporal/daily/point` (evidencia en `docs/E0/evidencia/resumen-robots.txt`).

El análisis es el siguiente: las directivas de `robots.txt` están pensadas para el rastreo e indexación de páginas web por parte de *crawlers*, no para el consumo de **endpoints de API REST documentados** que fueron diseñados para acceso programático. Las tres rutas utilizadas son de ese tipo, y Open-Meteo y NASA POWER las ofrecen públicamente. Se consultó al docente, quien **autorizó por escrito** continuar usando ambas fuentes a través de sus APIs oficiales documentadas, con la condición de mantener las buenas prácticas: un *User-Agent* personalizado con datos de contacto y del proyecto, y pausas entre peticiones (*rate limiting*). Con base en eso, el extractor registra en cada corrida el resultado de `robots.txt` y que se está aplicando esta excepción justificada.

Buenas prácticas que se mantienen: *User-Agent* con contacto institucional y nombre del proyecto, espera mínima de 1.5 segundos entre peticiones al mismo dominio, pocas peticiones por corrida (cerca de 20 en las incrementales), ningún dato personal y respeto de los términos de servicio.

Términos de servicio consultados: Open-Meteo, https://open-meteo.com/en/terms; NASA POWER, https://power.larc.nasa.gov/docs/.

**Nota sobre el uso comercial:** la gratuidad de Open-Meteo es para uso no comercial. Si el observatorio llegara a venderse como servicio, habría que contratar su plan comercial o cambiar de fuente. Esto se considerará en el modelo de negocio de E4.

### 5.3 Captura y almacenamiento

- **Capa Bronce:** cada respuesta se guarda tal como llegó, dentro de un archivo JSON con sus metadatos (fuente, URL, fecha de captura, código HTTP, huella `sha256` y número de corrida), en `data/bronce/<fuente>/fecha_captura=<fecha>/`.
- **Captura programada:** el flujo `.github/workflows/captura.yml` corre cada 6 horas en GitHub Actions: guarda evidencia de `robots.txt`, descarga el pronóstico a 7 días (Open-Meteo) y los últimos 10 días (NASA POWER) y sube los resultados al repositorio.
- **Serie histórica inicial:** una corrida manual en modo `historico` descarga desde 2021 por tramos anuales. `pipeline/verificar_bronce.py` comprueba que cada municipio tenga al menos 36 meses.
- **Bitácora:** `calidad/bitacora_captura.csv` registra cada petición (resultado, código, tiempo). Es la base para medir disponibilidad, MTBF y MTTR en E1.

## 6. Arranque del sistema de calidad

Se abrieron `calidad/tiempo-ximena.csv` y `calidad/defectos-ximena.csv` y se definieron tres objetivos medibles (`calidad/objetivos.md`): disponibilidad de la captura de al menos 95 %, completitud de 36 o más meses en los 10 municipios y 100 % de peticiones que respetan `robots.txt` y la pausa mínima. Al ser un equipo de una persona, la revisión de pares del *Quality Lead* no puede hacerse; se declara en la ficha de entrega.

## 7. Uso de IA generativa

Se usó Claude (Anthropic) para estructurar los documentos y escribir el código base del extractor y de las pruebas. La elección del tema, la entrevista, la revisión y la ejecución de la captura son del equipo.

## 8. Referencias

- Open-Meteo. *Historical Weather API* y términos de uso. https://open-meteo.com
- NASA. *Prediction Of Worldwide Energy Resources (POWER)*. https://power.larc.nasa.gov
- Proyecto Integrador Trusted Data Lab, Tecnológico Nacional de México (30 de octubre de 2026).
