# Revision de seguridad y cobertura

Corrida: 45553494683 · 2026-11-25T05:26:25Z · commit 08c5283

| Control | Resultado | Detalle |
|---|---|---|
| Secretos en todo el historial (gitleaks) | success | success = 0 secretos (evento workflow_dispatch: push revisa los commits nuevos; manual y semanal, todo el historial) |
| Vulnerabilidades en dependencias (pip-audit) | success | [pip-audit.md](pip-audit.md) |
| Pruebas y cobertura (pytest-cov) | success | TOTAL                               768    269    65% · [cobertura.txt](cobertura.txt) |
| Respaldo de Bronce restaurado identico | success | [respaldo.json](respaldo.json) |
