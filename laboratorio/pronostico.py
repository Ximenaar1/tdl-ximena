"""E1 · Pronostico de la lluvia mensual del municipio de Colima.

Decisiones (consultadas con la estudiante el 24-nov-2026):
- Serie: lluvia total mensual (mm) del municipio de Colima, solo meses completos (capa Oro).
- Prueba: los ultimos 12 meses se esconden para medir el error; el resto es entrenamiento.
- Escala: milimetros directos (los pronosticos y rangos se recortan en 0 porque no hay lluvia negativa).
- Criterio para elegir el modelo: menor MAE en prueba (error medio en mm, facil de explicar). Se reportan
  tambien RMSE y MAPE.

Uso: python -m laboratorio.pronostico   (requiere statsmodels; corre en GitHub Actions, flujo "analisis")
Escribe docs/E1/pronostico.md, docs/E1/figuras/*.png y data/oro/pronostico_lluvia_colima.csv
"""
import itertools
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
ORO = RAIZ / "data" / "oro" / "clima_municipio_mes.csv"
SALIDA = RAIZ / "docs" / "E1"
FIGURAS = SALIDA / "figuras"
MUNICIPIO = "colima"
MESES_PRUEBA = 12
HORIZONTE = 6
ALFA = 0.05  # intervalo de prediccion del 95 %


# ---------- Preparacion y metricas (no requieren statsmodels) ----------

def preparar_serie(ruta=ORO, municipio=MUNICIPIO):
    """Devuelve el DataFrame mensual del municipio con indice de fechas (inicio de mes) y solo meses completos."""
    oro = pd.read_csv(ruta)
    df = oro[(oro["municipio"] == municipio) & (oro["mes_completo"])].copy()
    df.index = pd.PeriodIndex(df["mes"], freq="M").to_timestamp()
    df.index.freq = "MS"
    return df.sort_index()


def dividir(serie, n_prueba=MESES_PRUEBA):
    return serie.iloc[:-n_prueba], serie.iloc[-n_prueba:]


def metricas(real, pred):
    """MAE y RMSE en mm. MAPE solo en meses con lluvia real >= 1 mm (con 0 mm el porcentaje no existe)."""
    real, pred = np.asarray(real, float), np.asarray(pred, float)
    err = real - pred
    con_lluvia = real >= 1
    mape = np.mean(np.abs(err[con_lluvia] / real[con_lluvia])) * 100 if con_lluvia.any() else np.nan
    return {"MAE": float(np.mean(np.abs(err))), "RMSE": float(np.sqrt(np.mean(err**2))), "MAPE": float(mape)}


def correlacion_cruzada(y, x, max_rezago=6):
    """corr(lluvia en t, x en t-k) para k = 0..max_rezago (x adelantada k meses)."""
    return pd.Series({k: y.corr(x.shift(k)) for k in range(max_rezago + 1)})


# ---------- Modelos (requieren statsmodels) ----------

def ajustar_ets(y, tendencia, estacional):
    from statsmodels.tsa.exponential_smoothing.ets import ETSModel

    modelo = ETSModel(y, error="add", trend=tendencia, damped_trend=tendencia is not None and estacional is not None,
                      seasonal=estacional, seasonal_periods=12 if estacional else None)
    return modelo.fit(disp=False)


def pronostico_ets(res, n_obs, h):
    marco = res.get_prediction(start=n_obs, end=n_obs + h - 1).summary_frame(alpha=ALFA)
    return marco.rename(columns={"pi_lower": "inferior", "pi_upper": "superior"})[["mean", "inferior", "superior"]]


def elegir_sarima(y, d):
    """Busqueda pequena de ordenes (p, q en 0..2; P, Q en 0..1; D = 1, s = 12) por menor AIC."""
    from statsmodels.tsa.statespace.sarimax import SARIMAX

    candidatos = []
    for p, q, P, Q in itertools.product(range(3), range(3), range(2), range(2)):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                res = SARIMAX(y, order=(p, d, q), seasonal_order=(P, 1, Q, 12)).fit(disp=False)
            candidatos.append(((p, d, q), (P, 1, Q, 12), res.aic))
        except Exception as e:  # noqa: BLE001 - un orden que no converge se descarta y se reporta
            print(f"SARIMA {(p, d, q)}x{(P, 1, Q, 12)} descartado: {e}")
    candidatos.sort(key=lambda c: c[2])
    return candidatos


def ajustar_sarima(y, orden, estacional):
    from statsmodels.tsa.statespace.sarimax import SARIMAX

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return SARIMAX(y, order=orden, seasonal_order=estacional).fit(disp=False)


def pronostico_sarima(res, h):
    marco = res.get_forecast(h).summary_frame(alpha=ALFA)
    return marco.rename(columns={"mean_ci_lower": "inferior", "mean_ci_upper": "superior"})[
        ["mean", "inferior", "superior"]]


MODELOS_ETS = {
    "Suavizamiento exponencial simple": (None, None),
    "Holt (tendencia)": ("add", None),
    "Holt-Winters (tendencia amortiguada + estacionalidad aditiva)": ("add", "add"),
}


def main():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from scipy import stats
    from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
    from statsmodels.stats.diagnostic import acorr_ljungbox
    from statsmodels.tsa.seasonal import seasonal_decompose
    from statsmodels.tsa.stattools import adfuller

    FIGURAS.mkdir(parents=True, exist_ok=True)
    df = preparar_serie()
    y = df["lluvia_total_mm"].astype(float)
    entrenamiento, prueba = dividir(y)
    r = {"inicio": str(y.index[0].date()), "fin": str(y.index[-1].date()), "n": len(y),
         "n_entrenamiento": len(entrenamiento), "n_prueba": len(prueba)}

    # 1. Caracterizacion y descomposicion (aditiva: hay meses en 0, la multiplicativa no aplica)
    desc = seasonal_decompose(y, model="additive", period=12)
    fig = desc.plot()
    fig.set_size_inches(10, 8)
    fig.savefig(FIGURAS / "descomposicion.png", dpi=120)
    plt.close(fig)
    estacional = desc.seasonal.iloc[:12]
    r["perfil_estacional"] = {f"{i.month:02d}": round(v, 1) for i, v in estacional.items()}
    var_estacional = np.var(desc.seasonal) / np.var(y)
    r["peso_estacionalidad"] = round(float(var_estacional) * 100, 1)
    r["descriptivos"] = y.describe().round(1).to_dict()

    # 2. Estacionariedad y autocorrelacion
    adf = adfuller(y, autolag="AIC")
    adf_dif = adfuller(y.diff(12).dropna(), autolag="AIC")
    r["adf"] = {"estadistico": round(adf[0], 3), "p": round(adf[1], 4)}
    r["adf_dif12"] = {"estadistico": round(adf_dif[0], 3), "p": round(adf_dif[1], 4)}
    d = 0 if adf[1] < 0.05 else 1
    r["d"] = d
    fig, ejes = plt.subplots(2, 1, figsize=(10, 7))
    plot_acf(y, lags=24, ax=ejes[0])
    plot_pacf(y, lags=24, ax=ejes[1], method="ywm")
    fig.tight_layout()
    fig.savefig(FIGURAS / "acf_pacf.png", dpi=120)
    plt.close(fig)

    # Correlacion cruzada con la radiacion solar y la temperatura minima
    ccf_rad = correlacion_cruzada(y, df["radiacion_media_mj_m2"])
    ccf_tmin = correlacion_cruzada(y, df["tmin_media_c"])
    r["ccf_radiacion"] = ccf_rad.round(3).to_dict()
    r["ccf_tmin"] = ccf_tmin.round(3).to_dict()
    fig, eje = plt.subplots(figsize=(9, 4))
    ancho = 0.4
    eje.bar(ccf_rad.index - ancho / 2, ccf_rad.values, ancho, label="radiacion solar (t - k)")
    eje.bar(ccf_tmin.index + ancho / 2, ccf_tmin.values, ancho, label="temperatura minima (t - k)")
    eje.axhline(0, color="black", linewidth=0.8)
    eje.set_xlabel("rezago k (meses)")
    eje.set_ylabel("correlacion con la lluvia del mes t")
    eje.legend()
    fig.tight_layout()
    fig.savefig(FIGURAS / "correlacion_cruzada.png", dpi=120)
    plt.close(fig)

    # 3. Cuatro modelos ajustados con entrenamiento y evaluados en prueba
    resultados, pronosticos = {}, {}
    for nombre, (tend, est) in MODELOS_ETS.items():
        res = ajustar_ets(entrenamiento, tend, est)
        pred = pronostico_ets(res, len(entrenamiento), len(prueba)).clip(lower=0)
        pred.index = prueba.index
        pronosticos[nombre] = pred
        resultados[nombre] = {**metricas(prueba, pred["mean"]), "AIC": round(float(res.aic), 1)}
    candidatos = elegir_sarima(entrenamiento, d)
    orden, orden_est, _ = candidatos[0]
    r["sarima_top5"] = [{"orden": str(o), "estacional": str(s), "AIC": round(a, 1)} for o, s, a in candidatos[:5]]
    nombre_sarima = f"SARIMA{orden}x{orden_est}"
    res_sarima = ajustar_sarima(entrenamiento, orden, orden_est)
    pred = pronostico_sarima(res_sarima, len(prueba)).clip(lower=0)
    pred.index = prueba.index
    pronosticos[nombre_sarima] = pred
    resultados[nombre_sarima] = {**metricas(prueba, pred["mean"]), "AIC": round(float(res_sarima.aic), 1)}
    tabla = pd.DataFrame(resultados).T.sort_values("MAE")
    ganador = tabla.index[0]
    r["tabla"] = tabla.round(1).to_dict(orient="index")
    r["ganador"] = ganador

    fig, eje = plt.subplots(figsize=(11, 5))
    eje.plot(y.index, y.values, color="black", label="real")
    for nombre, pred in pronosticos.items():
        eje.plot(pred.index, pred["mean"], marker="o", markersize=3, label=nombre)
    eje.axvline(prueba.index[0], color="gray", linestyle="--")
    eje.set_ylabel("lluvia mensual (mm)")
    eje.set_title("Comparacion de modelos en los 12 meses de prueba")
    eje.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGURAS / "comparacion_modelos.png", dpi=120)
    plt.close(fig)

    # 4. Modelo ganador: se reajusta con toda la serie y se pronostican 6 meses con intervalo
    if ganador == nombre_sarima:
        final = ajustar_sarima(y, orden, orden_est)
        futuro = pronostico_sarima(final, HORIZONTE)
        residuos = final.resid.iloc[13:]  # se omiten los primeros meses que absorbe la diferenciacion
    else:
        tend, est = MODELOS_ETS[ganador]
        final = ajustar_ets(y, tend, est)
        futuro = pronostico_ets(final, len(y), HORIZONTE)
        residuos = final.resid
    futuro.index = pd.date_range(y.index[-1] + pd.offsets.MonthBegin(), periods=HORIZONTE, freq="MS")
    futuro = futuro.clip(lower=0).round(1)
    futuro.index.name = "mes"
    salida_csv = futuro.rename(columns={"mean": "pronostico_mm", "inferior": "minimo_95_mm", "superior": "maximo_95_mm"})
    salida_csv.insert(0, "municipio", MUNICIPIO)
    salida_csv.insert(1, "modelo", ganador)
    salida_csv.to_csv(RAIZ / "data" / "oro" / "pronostico_lluvia_colima.csv", date_format="%Y-%m")
    r["pronostico"] = {str(i.date())[:7]: v for i, v in futuro.to_dict(orient="index").items()}

    fig, eje = plt.subplots(figsize=(11, 5))
    eje.plot(y.index, y.values, color="black", label="real")
    eje.plot(futuro.index, futuro["mean"], color="tab:blue", marker="o", label=f"pronostico ({ganador})")
    eje.fill_between(futuro.index, futuro["inferior"], futuro["superior"], alpha=0.25, label="intervalo 95 %")
    eje.set_ylabel("lluvia mensual (mm)")
    eje.set_title("Colima: pronostico de lluvia mensual a 6 meses")
    eje.legend()
    fig.tight_layout()
    fig.savefig(FIGURAS / "pronostico.png", dpi=120)
    plt.close(fig)

    # 5. Diagnostico de residuos del ganador
    residuos = pd.Series(residuos).dropna()
    lb = acorr_ljungbox(residuos, lags=[12], return_df=True)
    mitad = len(residuos) // 2
    lev = stats.levene(residuos.iloc[:mitad], residuos.iloc[mitad:])
    sh = stats.shapiro(residuos)
    r["ljung_box"] = {"estadistico": round(float(lb["lb_stat"].iloc[0]), 2), "p": round(float(lb["lb_pvalue"].iloc[0]), 4)}
    r["levene"] = {"estadistico": round(float(lev.statistic), 2), "p": round(float(lev.pvalue), 4)}
    r["shapiro"] = {"estadistico": round(float(sh.statistic), 3), "p": round(float(sh.pvalue), 4)}
    fig, ejes = plt.subplots(1, 2, figsize=(11, 4))
    ejes[0].plot(residuos.index, residuos.values)
    ejes[0].axhline(0, color="black", linewidth=0.8)
    ejes[0].set_title("Residuos del modelo ganador")
    plot_acf(residuos, lags=min(24, len(residuos) // 2 - 1), ax=ejes[1])
    fig.tight_layout()
    fig.savefig(FIGURAS / "residuos.png", dpi=120)
    plt.close(fig)

    (SALIDA / "pronostico_resultados.json").write_text(json.dumps(r, indent=2, ensure_ascii=False, default=str),
                                                       encoding="utf-8")
    escribir_reporte(r, tabla)
    print(json.dumps({"ganador": ganador, "tabla": r["tabla"]}, indent=2, ensure_ascii=False))


def escribir_reporte(r, tabla):
    filas = "\n".join(
        f"| {n} | {v['MAE']:.1f} | {v['RMSE']:.1f} | {v['MAPE']:.1f} % | {v['AIC']:.1f} |" for n, v in tabla.iterrows())
    pron = "\n".join(
        f"| {m} | {v['mean']:.1f} | {v['inferior']:.1f} a {v['superior']:.1f} |" for m, v in r["pronostico"].items())

    def sig(p):
        return "si" if p < 0.05 else "no"

    primer = next(iter(r["pronostico"].items()))
    texto = f"""# Pronostico de la lluvia mensual · municipio de Colima

Generado automaticamente por `python -m laboratorio.pronostico` a partir de `data/oro/clima_municipio_mes.csv`.
Serie: {r['n']} meses completos ({r['inicio'][:7]} a {r['fin'][:7]}). Entrenamiento: {r['n_entrenamiento']} meses; prueba: los ultimos {r['n_prueba']}.

## 1. Caracterizacion y descomposicion
![descomposicion](figuras/descomposicion.png)

Descriptivos (mm/mes): {r['descriptivos']}.
Se uso una descomposicion **aditiva** porque la serie tiene meses con 0 mm, en los que la multiplicativa no esta definida.
La estacionalidad explica aproximadamente el {r['peso_estacionalidad']} % de la variacion de la serie.
Perfil estacional (mm sobre o bajo el nivel medio, por mes): {r['perfil_estacional']}.

## 2. Estacionariedad, ACF/PACF y correlacion cruzada
Prueba de Dickey-Fuller aumentada sobre la serie: estadistico {r['adf']['estadistico']}, p = {r['adf']['p']} (rechaza raiz unitaria: {sig(r['adf']['p'])}).
Sobre la diferencia estacional (12 meses): estadistico {r['adf_dif12']['estadistico']}, p = {r['adf_dif12']['p']}.
Orden de diferenciacion no estacional elegido: d = {r['d']}; se aplica diferenciacion estacional D = 1 (s = 12) por el pico de la ACF en el rezago 12.

![acf y pacf](figuras/acf_pacf.png)

Correlacion cruzada de la lluvia del mes t con la variable k meses antes:
- radiacion solar: {r['ccf_radiacion']}
- temperatura minima: {r['ccf_tmin']}

![correlacion cruzada](figuras/correlacion_cruzada.png)

## 3. Cuatro modelos y seleccion por error en prueba
SARIMA: busqueda de ordenes por AIC en el entrenamiento; los 5 mejores: {r['sarima_top5']}.

| Modelo | MAE (mm) | RMSE (mm) | MAPE* | AIC (entrenamiento) |
|---|---|---|---|---|
{filas}

\\* MAPE calculado solo en los meses de prueba con lluvia real de 1 mm o mas (con 0 mm el porcentaje no existe).
Criterio de seleccion: **menor MAE**. Modelo ganador: **{r['ganador']}**.

![comparacion](figuras/comparacion_modelos.png)

## 4. Pronostico a 6 meses (modelo ganador reajustado con toda la serie)
| Mes | Pronostico (mm) | Intervalo de prediccion 95 % (mm) |
|---|---|---|
{pron}

Los valores negativos se recortan a 0 porque no existe lluvia negativa.

![pronostico](figuras/pronostico.png)

**Frase para el cliente:** para {primer[0]} se esperan alrededor de {primer[1]['mean']:.0f} mm de lluvia en el municipio de Colima, con un rango probable de {primer[1]['inferior']:.0f} a {primer[1]['superior']:.0f} mm.

## 5. Diagnostico de residuos del modelo ganador
- Ljung-Box (12 rezagos): estadistico {r['ljung_box']['estadistico']}, p = {r['ljung_box']['p']} -> residuos autocorrelacionados: {sig(r['ljung_box']['p'])}.
- Levene (primera vs segunda mitad): estadistico {r['levene']['estadistico']}, p = {r['levene']['p']} -> varianza cambia: {sig(r['levene']['p'])}.
- Shapiro-Wilk: estadistico {r['shapiro']['estadistico']}, p = {r['shapiro']['p']} -> residuos no normales: {sig(r['shapiro']['p'])}.

![residuos](figuras/residuos.png)
"""
    (SALIDA / "pronostico.md").write_text(texto, encoding="utf-8")


if __name__ == "__main__":
    main()
