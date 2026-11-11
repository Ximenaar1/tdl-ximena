# tdl-ximena · Observatorio de clima para eventos al aire libre en Colima

Proyecto Integrador Trusted Data Lab (Ingeniería de Datos, Análisis Estadístico, Calidad en SI).
Equipo: Jaidy Ximena Álvarez Rocha.

**Qué observa:** lluvia, temperatura y viento en los 10 municipios de Colima, para que negocios de renta de
mobiliario y organizadores de eventos decidan con anticipación.

## Cómo se ejecuta

```bash
pip install -r requirements.txt
python -m extractores.verificar_robots          # evidencia de robots.txt
python -m extractores.captura --modo historico  # serie historica (primera vez)
python -m extractores.captura --modo incremental
python -m pipeline.verificar_bronce             # comprueba >= 36 meses por municipio
python -m pytest -q
```

La captura programada corre en GitHub Actions (`.github/workflows/captura.yml`, cada 6 horas).
Entregas en `docs/E0/` (propuesta y ficha de entrega). Registros de calidad en `calidad/`.

Datos: Open-Meteo (CC BY 4.0) y NASA POWER. Ver `docs/E0/propuesta.md`.
