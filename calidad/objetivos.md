# Objetivos de calidad de E0

| # | Objetivo | Metrica | Meta | Como se mide |
|---|----------|---------|------|--------------|
| 1 | Disponibilidad de la captura | corridas exitosas / corridas programadas | >= 95 % en los 7 dias previos a E1 | `calidad/bitacora_captura.csv` (columna `resultado`) |
| 2 | Completitud de la serie historica | meses con datos por municipio en Bronce | 36 o mas meses en los 10 municipios | `python -m pipeline.verificar_bronce` |
| 3 | Captura etica | peticiones que respetan robots.txt y pausa >= 1 s entre peticiones al mismo dominio | 100 % | `docs/E0/evidencia/resumen-robots.txt` y la bitacora (cero errores de permiso) |
