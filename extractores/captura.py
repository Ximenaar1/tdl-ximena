"""Captura a la capa Bronce con bitacora. Uso: python -m extractores.captura --modo historico|incremental"""
import argparse
import csv
import hashlib
import json
import os
import time
from datetime import date, datetime, timezone
from pathlib import Path

from .base import ExtractorEtico
from .fuentes import peticiones

RAIZ = Path(__file__).resolve().parent.parent
CAMPOS_BITACORA = ["timestamp_utc", "run_id", "modo", "fuente", "municipio", "resultado",
                   "http_status", "bytes", "segundos", "mensaje"]


def _registrar(raiz, fila):
    ruta = Path(raiz) / "calidad" / "bitacora_captura.csv"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    nuevo = not ruta.exists()
    with open(ruta, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS_BITACORA)
        if nuevo:
            w.writeheader()
        w.writerow(fila)


def guardar_bronce(raiz, p, respuesta, cuerpo_json, run_id, modo, ahora):
    """Guarda la respuesta tal como llego, dentro de un sobre con metadatos de captura (linaje)."""
    crudo = respuesta.content
    sobre = {
        "meta": {
            "fuente": p["fuente"], "municipio": p["municipio"], "url": p["url"], "modo": modo,
            "fecha_captura_utc": ahora.isoformat(), "http_status": respuesta.status_code,
            "sha256_respuesta": hashlib.sha256(crudo).hexdigest(), "run_id": run_id,
        },
        "respuesta": cuerpo_json,
    }
    carpeta = Path(raiz) / "data" / "bronce" / p["fuente"] / f"fecha_captura={ahora.date().isoformat()}"
    carpeta.mkdir(parents=True, exist_ok=True)
    nombre = f"{p['municipio']}_{p['inicio']}_{p['fin']}_{ahora.strftime('%H%M%S')}.json"
    ruta = carpeta / nombre
    ruta.write_text(json.dumps(sobre, ensure_ascii=False), encoding="utf-8")
    return ruta


def ejecutar(modo, hoy=None, ext=None, raiz=RAIZ):
    """Devuelve el numero de peticiones fallidas."""
    hoy = hoy or date.today()
    ext = ext or ExtractorEtico()
    run_id = os.environ.get("GITHUB_RUN_ID", "local")
    fallos = 0
    for p in peticiones(modo, hoy):
        t0 = time.time()
        ahora = datetime.now(timezone.utc)
        fila = dict(timestamp_utc=ahora.isoformat(timespec="seconds"), run_id=run_id, modo=modo,
                    fuente=p["fuente"], municipio=p["municipio"])
        try:
            r = ext.get(p["url"])
            guardar_bronce(raiz, p, r, r.json(), run_id, modo, ahora)
            fila.update(resultado="ok", http_status=r.status_code, bytes=len(r.content),
                        mensaje=getattr(r, "nota_robots", ""))
        except Exception as e:  # se registra siempre: nada falla en silencio
            fallos += 1
            fila.update(resultado="error", http_status="", bytes=0, mensaje=str(e)[:200].replace("\n", " "))
        fila["segundos"] = round(time.time() - t0, 2)
        _registrar(raiz, fila)
    return fallos


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--modo", choices=["historico", "incremental"], default="incremental")
    args = ap.parse_args()
    n = ejecutar(args.modo)
    print(f"Peticiones fallidas: {n}")
    raise SystemExit(1 if n else 0)
