"""Pruebas del calculo de fiabilidad (MTBF, MTTR, disponibilidad) con corridas sinteticas."""
import pandas as pd

from calidad import fiabilidad as f


def _corridas(estados):
    """Una corrida cada 6 h; cada corrida dura 0 h. estados: lista de True (exitosa) / False (fallida)."""
    t0 = pd.Timestamp("2026-01-01T00:00:00Z")
    filas = [{"run_id": i, "inicio": t0 + pd.Timedelta(hours=6 * i), "fin": t0 + pd.Timedelta(hours=6 * i),
              "modo": "incremental", "peticiones": 20, "ok": 20 if e else 0, "exitosa": e}
             for i, e in enumerate(estados)]
    return pd.DataFrame(filas)


def test_fallas_seguidas_son_un_solo_episodio():
    m = f.metricas(_corridas([True, False, False, True, True]))
    assert m["fallas"] == 1
    assert m["horas_caido"] == 12 and m["horas_observadas"] == 24
    assert m["MTBF_h"] == 12 and m["MTTR_h"] == 12 and m["disponibilidad"] == 50


def test_sin_fallas_mtbf_no_definido_y_disponibilidad_total():
    m = f.metricas(_corridas([True, True, True]))
    assert m["fallas"] == 0 and m["MTBF_h"] is None and m["disponibilidad"] == 100


def test_falla_sin_reparar_cuenta_hasta_el_final():
    m = f.metricas(_corridas([True, False, False]))
    assert m["falla_abierta"] and m["horas_caido"] == 6


def test_bitacora_real_se_lee_por_corrida():
    c = f.corridas()
    assert c["inicio"].is_monotonic_increasing
    assert (c["ok"] <= c["peticiones"]).all()
