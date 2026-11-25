"""Pruebas de los datos del tablero (sin Streamlit)."""
import pandas as pd

from tablero import datos


def test_nombre_mes():
    assert datos.nombre_mes("2027-09") == "septiembre de 2027"


def test_frases_cliente_usan_el_pico_y_las_temporadas():
    pron = pd.DataFrame({"mes": ["2026-11", "2026-12", "2027-08", "2027-09"],
                         "pronostico_mm": [20.0, 10.0, 230.0, 275.0],
                         "minimo_95_mm": [0.0, 0.0, 50.0, 97.0], "maximo_95_mm": [200.0, 190.0, 400.0, 453.0]})
    frases = datos.frases_cliente(pron)
    assert "septiembre de 2027" in frases[0] and "275 mm" in frases[0] and "97 a 453" in frases[0]
    assert "agosto de 2027 a septiembre de 2027" in frases[1]
    assert "noviembre de 2026 a diciembre de 2026" in frases[2]


def test_datos_reales_del_tablero_se_leen():
    assert len(datos.cargar_pronostico()) == 12
    siete, captura = datos.pronostico_7_dias()
    assert captura is not None and siete["municipio"].nunique() == 10
    ind = datos.indicadores_calidad()
    assert ind["registros_cuarentena"] >= 0 and ind["registros_plata"] > 0
