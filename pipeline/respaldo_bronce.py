"""Respaldo de la capa Bronce y prueba de restauracion.

Bronce es la unica capa que no se puede regenerar (las demas salen de ella con el pipeline), por eso se respalda:
1. `crear`: empaqueta data/bronce en un .zip y guarda un manifiesto con la huella SHA-256 de cada archivo.
2. `verificar`: descomprime el respaldo en una carpeta temporal y comprueba que cada archivo restaurado tiene
   exactamente la misma huella que el original. Si falta uno o alguno cambio, el respaldo no sirve.

Uso: python -m pipeline.respaldo_bronce [carpeta_destino]
En GitHub Actions (flujo "seguridad") el .zip se sube como artefacto, una copia fuera del repositorio.
"""
import hashlib
import json
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
BRONCE = RAIZ / "data" / "bronce"


def huella(ruta):
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()


def manifiesto(origen=BRONCE):
    return {str(p.relative_to(origen)).replace("\\", "/"): huella(p)
            for p in sorted(origen.rglob("*")) if p.is_file()}


def crear(destino, origen=BRONCE):
    """Crea respaldo_bronce_<fecha>.zip y su manifiesto en `destino`. Devuelve la ruta del zip."""
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    fecha = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    archivo = destino / f"respaldo_bronce_{fecha}.zip"
    man = manifiesto(origen)
    with zipfile.ZipFile(archivo, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for relativa in man:
            z.write(origen / relativa, relativa)
        z.writestr("MANIFIESTO.json", json.dumps(man, indent=1))
    return archivo


def verificar(archivo_zip, origen=BRONCE):
    """Restaura el zip en una carpeta temporal y compara huellas con el original."""
    original = manifiesto(origen)
    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(archivo_zip) as z:
            z.extractall(tmp)
        restaurado = manifiesto(Path(tmp))
    restaurado.pop("MANIFIESTO.json", None)
    faltantes = sorted(set(original) - set(restaurado))
    distintos = sorted(k for k in original.keys() & restaurado.keys() if original[k] != restaurado[k])
    return {"archivos_originales": len(original), "archivos_restaurados": len(restaurado),
            "faltantes": faltantes, "distintos": distintos, "ok": not faltantes and not distintos}


def main():
    destino = sys.argv[1] if len(sys.argv) > 1 else "respaldo"
    archivo = crear(destino)
    resultado = verificar(archivo)
    print(json.dumps({"respaldo": str(archivo), "bytes": archivo.stat().st_size, **resultado}, indent=2))
    if not resultado["ok"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
