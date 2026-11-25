# Revision de seguridad y cobertura

Corrida: 45552494807 · 2026-11-25T05:19:02Z · commit c4f5a3a

| Control | Resultado | Detalle |
|---|---|---|
| Secretos en todo el historial (gitleaks) | success | success = 0 secretos (evento push: push revisa los commits nuevos; manual y semanal, todo el historial) |
| Vulnerabilidades en dependencias (pip-audit) | success | [pip-audit.md](pip-audit.md) |
| Pruebas y cobertura (pytest-cov) | success | TOTAL                               768    269    65% · [cobertura.txt](cobertura.txt) |
| Respaldo de Bronce restaurado identico | success | [respaldo.json](respaldo.json) |
