# Revision de seguridad y cobertura

Corrida: 45550408779 · 2026-11-25T04:59:51Z · commit 5644a8d

| Control | Resultado | Detalle |
|---|---|---|
| Secretos en todo el historial (gitleaks) | success | success = 0 secretos (evento push: push revisa los commits nuevos; manual y semanal, todo el historial) |
| Vulnerabilidades en dependencias (pip-audit) | success | [pip-audit.md](pip-audit.md) |
| Pruebas y cobertura (pytest-cov) | success | TOTAL                               768    269    65% · [cobertura.txt](cobertura.txt) |
| Respaldo de Bronce restaurado identico | success | [respaldo.json](respaldo.json) |
