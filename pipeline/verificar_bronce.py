"""Comprueba que la serie historica en Bronce cubre >= 36 meses por municipio (Open-Meteo archive)."""
import json
import sys
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def meses_por_municipio(raiz=RAIZ):
    meses = defaultdict(set)
    for ruta in (Path(raiz) / "data" / "bronce" / "openmeteo_archive").rglob("*.json"):
        sobre = json.loads(ruta.read_text(encoding="utf-8"))
        fechas = sobre["respuesta"].get("daily", {}).get("time", [])
        meses[sobre["meta"]["municipio"]].update(f[:7] for f in fechas)
    return meses


def main(minimo=36, raiz=RAIZ):
    meses = meses_por_municipio(raiz)
    if not meses:
        print("Sin datos en Bronce todavia.")
        return 1
    ok = True
    for mun, ms in sorted(meses.items()):
        estado = "OK" if len(ms) >= minimo else "FALTAN"
        ok &= len(ms) >= minimo
        print(f"{mun:15s} {len(ms):3d} meses ({min(ms)} a {max(ms)})  {estado}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
