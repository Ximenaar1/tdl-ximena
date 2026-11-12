"""Guarda como evidencia el robots.txt de cada dominio y si permite las rutas que usamos."""
import urllib.robotparser
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests

from .base import APIS_DOCUMENTADAS, UA
from .fuentes import NASA, OM_ARCHIVE, OM_FORECAST

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "docs" / "E0" / "evidencia"


def main():
    DESTINO.mkdir(parents=True, exist_ok=True)
    resumen = [f"Verificacion robots.txt - {datetime.now(timezone.utc).isoformat(timespec='seconds')}", ""]
    for url in (OM_ARCHIVE, OM_FORECAST, NASA):
        p = urlparse(url)
        base = f"{p.scheme}://{p.netloc}"
        try:
            r = requests.get(base + "/robots.txt", headers={"User-Agent": UA}, timeout=30)
            estado, texto = r.status_code, r.text
        except Exception as e:
            estado, texto = "error", str(e)
        (DESTINO / f"robots-{p.netloc}.txt").write_text(f"# HTTP {estado}\n{texto}", encoding="utf-8")
        rp = urllib.robotparser.RobotFileParser()
        if estado == 200:
            rp.parse(texto.splitlines())
            permitido = rp.can_fetch(UA, url)
        else:
            permitido = "sin robots.txt valido (revisar manualmente)"
        linea = f"{p.netloc}: HTTP {estado}; ruta {p.path} permitida: {permitido}"
        if permitido is False and p.netloc in APIS_DOCUMENTADAS:
            linea += (f" -> API REST documentada; se usa con autorizacion del docente (2026-11-12)."
                      f" Terminos: {APIS_DOCUMENTADAS[p.netloc]}")
        resumen.append(linea)
    (DESTINO / "resumen-robots.txt").write_text("\n".join(resumen) + "\n", encoding="utf-8")
    print("\n".join(resumen))


if __name__ == "__main__":
    main()
