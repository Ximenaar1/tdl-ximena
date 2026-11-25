"""Pruebas de la preparacion de la serie y de las metricas de error del pronostico."""
import math

from laboratorio import pronostico as p


def test_serie_mensual_completa_y_division():
    y = p.preparar_serie()["lluvia_total_mm"]
    assert len(y) >= 36
    assert str(y.index.freqstr).startswith("MS")
    entrenamiento, prueba = p.dividir(y)
    assert len(prueba) == p.MESES_PRUEBA and entrenamiento.index[-1] < prueba.index[0]


def test_metricas_excluyen_meses_sin_lluvia_del_mape():
    m = p.metricas([0.0, 100.0, 200.0], [10.0, 110.0, 180.0])
    assert m["MAE"] == 40 / 3
    assert math.isclose(m["RMSE"], math.sqrt((100 + 100 + 400) / 3))
    assert math.isclose(m["MAPE"], (10 / 100 + 20 / 200) / 2 * 100)


def test_huella_reproducibilidad_es_estable():
    h1, h2 = p.huella_reproducibilidad(), p.huella_reproducibilidad()
    assert h1["sha256_datos"] == h2["sha256_datos"] and len(h1["sha256_datos"]) == 64
    assert "statsmodels" in h1["versiones"]
