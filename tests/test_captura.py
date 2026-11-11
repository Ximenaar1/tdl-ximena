"""Pruebas con respuestas SIMULADAS (solo para probar la logica; no son datos del observatorio)."""
import csv
import json
from datetime import date

from extractores import captura, fuentes
from pipeline import verificar_bronce


class RespuestaFalsa:
    status_code = 200

    def __init__(self, cuerpo):
        self._cuerpo = cuerpo
        self.content = json.dumps(cuerpo).encode()

    def json(self):
        return self._cuerpo


class ExtractorFalso:
    def __init__(self, falla_en=None):
        self.llamadas, self.falla_en = [], falla_en

    def get(self, url):
        self.llamadas.append(url)
        if self.falla_en and self.falla_en in url:
            raise RuntimeError("fallo simulado")
        return RespuestaFalsa({"daily": {"time": ["2024-01-01", "2024-02-01"]}})


def test_rangos_anuales_cubren_todo_el_periodo():
    t = fuentes.rangos_anuales(date(2021, 1, 1), date(2023, 3, 10))
    assert t[0] == (date(2021, 1, 1), date(2021, 12, 31))
    assert t[-1] == (date(2023, 1, 1), date(2023, 3, 10))
    assert len(t) == 3


def test_historico_cubre_al_menos_36_meses():
    ini, fin = fuentes.INICIO_HISTORICO, date(2026, 11, 9) - __import__("datetime").timedelta(days=7)
    assert (fin.year - ini.year) * 12 + fin.month - ini.month + 1 >= 36


def test_ejecutar_guarda_bronce_con_metadatos_y_bitacora(tmp_path):
    ext = ExtractorFalso()
    fallos = captura.ejecutar("incremental", hoy=date(2026, 11, 9), ext=ext, raiz=tmp_path)
    assert fallos == 0
    archivos = list((tmp_path / "data" / "bronce").rglob("*.json"))
    assert len(archivos) == len(ext.llamadas) == 20
    sobre = json.loads(archivos[0].read_text(encoding="utf-8"))
    assert {"fuente", "url", "fecha_captura_utc", "sha256_respuesta"} <= set(sobre["meta"])
    filas = list(csv.DictReader(open(tmp_path / "calidad" / "bitacora_captura.csv", encoding="utf-8")))
    assert len(filas) == 20 and all(f["resultado"] == "ok" for f in filas)


def test_un_fallo_se_registra_y_no_detiene_la_captura(tmp_path):
    ext = ExtractorFalso(falla_en="power.larc.nasa.gov")
    fallos = captura.ejecutar("incremental", hoy=date(2026, 11, 9), ext=ext, raiz=tmp_path)
    assert fallos == 10
    filas = list(csv.DictReader(open(tmp_path / "calidad" / "bitacora_captura.csv", encoding="utf-8")))
    assert sum(f["resultado"] == "error" for f in filas) == 10
    assert len(filas) == 20


def test_verificar_bronce_detecta_menos_de_36_meses(tmp_path):
    carpeta = tmp_path / "data" / "bronce" / "openmeteo_archive"
    carpeta.mkdir(parents=True)
    (carpeta / "a.json").write_text(json.dumps(
        {"meta": {"municipio": "colima"}, "respuesta": {"daily": {"time": ["2024-01-01", "2024-02-01"]}}}))
    assert verificar_bronce.main(raiz=tmp_path) == 1
