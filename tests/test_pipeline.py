"""Pruebas del pipeline Bronce -> Plata -> Oro con datos SIMULADOS (sin red)."""
import json
from pathlib import Path

import pandas as pd
import pytest

from pipeline import bronce_a_plata as bp
from pipeline import ejecutar
from pipeline import puerta_calidad as pc

DIAS = pd.date_range("2024-01-01", "2024-02-29", freq="D")


def _escribir(raiz, fuente, municipio, captura, respuesta, nombre):
    carpeta = Path(raiz) / "data" / "bronce" / fuente / f"fecha_captura={captura[:10]}"
    carpeta.mkdir(parents=True, exist_ok=True)
    sobre = {"meta": {"fuente": fuente, "municipio": municipio, "fecha_captura_utc": captura}, "respuesta": respuesta}
    (carpeta / nombre).write_text(json.dumps(sobre), encoding="utf-8")


def _openmeteo(dias, tmin=15.0):
    n = len(dias)
    return {"daily": {
        "time": [d.strftime("%Y-%m-%d") for d in dias],
        "temperature_2m_max": [30.0] * n, "temperature_2m_min": [tmin] * n, "temperature_2m_mean": [22.0] * n,
        "precipitation_sum": [0.0] * (n - 1) + [12.0], "rain_sum": [0.0] * (n - 1) + [12.0],
        "wind_speed_10m_max": [15.0] * n, "shortwave_radiation_sum": [20.0] * n,
        "et0_fao_evapotranspiration": [4.0] * n,
    }}


def _nasa(dias, lluvia):
    fechas = [d.strftime("%Y%m%d") for d in dias]
    return {"properties": {"parameter": {
        "T2M_MAX": dict.fromkeys(fechas, 29.0), "T2M_MIN": dict.fromkeys(fechas, 16.0),
        "PRECTOTCORR": dict.fromkeys(fechas, lluvia), "WS10M_MAX": dict.fromkeys(fechas, 5.0),
        "ALLSKY_SFC_SW_DWN": dict.fromkeys(fechas, 19.0),
    }}}


@pytest.fixture
def bronce(tmp_path):
    _escribir(tmp_path, "openmeteo_archive", "colima", "2026-11-14T05:00:00+00:00", _openmeteo(DIAS), "a.json")
    # Un dia imposible (tmin > tmax) en otro municipio para probar la cuarentena
    _escribir(tmp_path, "openmeteo_archive", "tecoman", "2026-11-14T05:00:00+00:00",
              _openmeteo(DIAS[:1], tmin=35.0), "b.json")
    # NASA: primera captura sin dato (-999), la posterior ya trae el valor real -> duplicado
    _escribir(tmp_path, "nasa_power", "colima", "2026-11-14T05:00:00+00:00", _nasa(DIAS, -999.0), "c.json")
    _escribir(tmp_path, "nasa_power", "colima", "2026-11-20T05:00:00+00:00", _nasa(DIAS[-5:], 2.0), "d.json")
    return tmp_path


def test_nasa_convierte_faltantes_y_unidades(bronce):
    nasa = bp.leer_nasa(bronce)
    assert nasa["nasa_lluvia_mm"].isna().sum() == len(DIAS)          # -999 -> vacio
    assert nasa["nasa_viento_max_kmh"].iloc[0] == pytest.approx(18.0)  # 5 m/s -> 18 km/h


def test_duplicados_conservan_la_captura_mas_reciente(bronce):
    nasa, n_dup = bp.quitar_duplicados(bp.leer_nasa(bronce))
    assert n_dup == 5
    assert nasa[nasa["fecha"] == DIAS[-1]]["nasa_lluvia_mm"].iloc[0] == 2.0


def test_puerta_manda_a_cuarentena_con_motivo(bronce):
    om, _ = bp.quitar_duplicados(bp.leer_openmeteo(raiz=bronce))
    nasa, _ = bp.quitar_duplicados(bp.leer_nasa(bronce))
    aprobados, cuarentena = pc.aplicar_reglas(bp.integrar(om, nasa))
    assert len(cuarentena) == 1
    assert "tmin mayor que tmax" in cuarentena["motivo"].iloc[0]
    assert len(aprobados) == len(DIAS)


def test_atipico_se_marca_pero_no_se_borra():
    df = pd.DataFrame({
        "municipio": "colima", "fecha": pd.date_range("2024-07-01", periods=20),
        "tmax_c": [30.0] * 19 + [45.0], "tmin_c": 20.0, "viento_max_kmh": 15.0,
        "lluvia_mm": [5.0, 6.0, 4.0, 5.5, 6.5] * 3 + [5.0, 4.5, 6.0, 5.0, 300.0],
    })
    marcado = pc.marcar_atipicos(df)
    assert len(marcado) == 20
    assert marcado["atipico_tmax_c"].iloc[-1]
    assert marcado["atipico_lluvia_mm"].iloc[-1]


def test_pipeline_completo_genera_capas(bronce):
    r = ejecutar.correr(bronce)
    assert r["cuarentena"] == 1
    oro = pd.read_csv(bronce / "data/oro/clima_municipio_mes.csv")
    enero = oro[(oro["municipio"] == "colima") & (oro["mes"] == "2024-01")].iloc[0]
    assert enero["dias_con_dato"] == 31 and enero["mes_completo"]
    assert (bronce / "data/cuarentena/cuarentena.csv").exists()
    assert (bronce / "docs/E1/reporte_pipeline.md").exists()


def test_esquema_pandera_aprueba_plata(bronce):
    pytest.importorskip("pandera")
    r = ejecutar.correr(bronce)
    assert r["esquema_pandera"] is True
