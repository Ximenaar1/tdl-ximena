"""Pruebas del respaldo de Bronce: se restaura identico y detecta un archivo alterado."""
import zipfile

from pipeline import respaldo_bronce as r


def _bronce_falso(tmp_path):
    origen = tmp_path / "bronce" / "fuente" / "fecha_captura=2026-11-24"
    origen.mkdir(parents=True)
    (origen / "a.json").write_text('{"x": 1}')
    (origen / "b.json").write_text('{"x": 2}')
    return tmp_path / "bronce"


def test_respaldo_se_restaura_identico(tmp_path):
    origen = _bronce_falso(tmp_path)
    archivo = r.crear(tmp_path / "respaldo", origen)
    resultado = r.verificar(archivo, origen)
    assert resultado["ok"] and resultado["archivos_restaurados"] == 2


def test_respaldo_detecta_archivo_alterado(tmp_path):
    origen = _bronce_falso(tmp_path)
    archivo = r.crear(tmp_path / "respaldo", origen)
    (origen / "fuente" / "fecha_captura=2026-11-24" / "a.json").write_text('{"x": 999}')
    resultado = r.verificar(archivo, origen)
    assert not resultado["ok"] and resultado["distintos"] == ["fuente/fecha_captura=2026-11-24/a.json"]


def test_respaldo_incluye_manifiesto(tmp_path):
    origen = _bronce_falso(tmp_path)
    with zipfile.ZipFile(r.crear(tmp_path / "respaldo", origen)) as z:
        assert "MANIFIESTO.json" in z.namelist()
