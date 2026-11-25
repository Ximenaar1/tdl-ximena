"""E1 · Pronostico de la lluvia mensual del municipio de Colima.

Decisiones (consultadas con la estudiante el 24-nov-2026):
- Serie: lluvia total mensual (mm) del municipio de Colima, solo meses completos (capa Oro).
- Prueba: los ultimos 12 meses se esconden para medir el error; el resto es entrenamiento.
- Escala: se prueban milimetros directos y escala logaritmica (log(1 + mm)); gana la de menor MAE en mm.
- Horizonte: 12 meses, para cubrir la siguiente temporada de lluvias (decidido el 24-nov-2026).
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
HORIZONTE = 12
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
    """Ajuste ETS reproducible.

    Con la inicializacion por defecto ("estimated") el optimizador busca a la vez los parametros de
    suavizamiento y los 14 estados iniciales; con los mismos datos dio AIC 697.1 en una corrida y 700.1 en
    otra (25-nov-2026). Con "heuristic" los estados iniciales se calculan con una regla fija a partir de los
    primeros anios de la serie y el optimizador solo busca alfa, beta, gamma y phi: el punto de partida es
    siempre el mismo y el resultado tambien.
    """
    from statsmodels.tsa.exponential_smoothing.ets import ETSModel

    modelo = ETSModel(y, error="add", trend=tendencia, damped_trend=tendencia is not None and estacional is not None,
                      seasonal=estacional, seasonal_periods=12 if estacional else None,
                      initialization_method="heuristic")
    return modelo.fit(disp=False, maxiter=2000)


def convergio(res):
    """True si el optimizador reporta convergencia (None si la version de statsmodels no lo informa)."""
    retvals = getattr(res, "mle_retvals", None) or {}
    valor = retvals.get("converged")
    return None if valor is None else bool(valor)


def huella_reproducibilidad(ruta=ORO):
    """Huella de los datos (SHA-256 del archivo de Oro) y versiones usadas, para comparar corridas."""
    import hashlib
    import platform
    from importlib.metadata import PackageNotFoundError, version

    versiones = {}
    for paquete in ["statsmodels", "pandas", "numpy", "scipy", "matplotlib"]:
        try:
            versiones[paquete] = version(paquete)
        except PackageNotFoundError:
            versiones[paquete] = None
    return {"sha256_datos": hashlib.sha256(Path(ruta).read_bytes()).hexdigest(),
            "python": platform.python_version(), "versiones": versiones}


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

# Escala de modelado: (transformacion, inversa). En log se modela log(1 + mm) y se regresa con exp(x) - 1;
# al regresar, el pronostico central representa la mediana y los limites del intervalo siguen siendo validos.
ESCALAS = {"mm": (lambda s: s, lambda s: s), "log": (np.log1p, np.expm1)}


def nombre_modelo(modelo, orden):
    return f"SARIMA{orden[0]}x{orden[1]}" if modelo == "SARIMA" else modelo


def ajustar_y_pronosticar(modelo, serie, h, escala, orden):
    """Ajusta en la escala indicada y devuelve (resultado, pronostico en mm recortado en 0)."""
    ida, regreso = ESCALAS[escala]
    datos = ida(serie)
    if modelo == "SARIMA":
        res = ajustar_sarima(datos, *orden)
        pred = pronostico_sarima(res, h)
    else:
        res = ajustar_ets(datos, *MODELOS_ETS[modelo])
        pred = pronostico_ets(res, len(datos), h)
    return res, regreso(pred).clip(lower=0)


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
         "n_entrenamiento": len(entrenamiento), "n_prueba": len(prueba),
         "reproducibilidad": huella_reproducibilidad()}

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

    # 3. Cuatro modelos x dos escalas (mm directos y logaritmica), evaluados en prueba en mm
    resultados, pronosticos, ordenes, origen, convergencia = {}, {}, {}, {}, {}
    r["sarima_top5"] = {}
    for escala, (ida, _) in ESCALAS.items():
        candidatos = elegir_sarima(ida(entrenamiento), d)
        ordenes[escala] = candidatos[0][:2]
        r["sarima_top5"][escala] = [{"orden": str(o), "estacional": str(s), "AIC": round(float(a), 1)}
                                    for o, s, a in candidatos[:5]]
        for modelo in [*MODELOS_ETS, "SARIMA"]:
            res, pred = ajustar_y_pronosticar(modelo, entrenamiento, len(prueba), escala, ordenes[escala])
            pred.index = prueba.index
            nombre = f"{nombre_modelo(modelo, ordenes[escala])} [{escala}]"
            pronosticos[nombre] = pred
            origen[nombre] = (modelo, escala)
            resultados[nombre] = {**metricas(prueba, pred["mean"]), "AIC": round(float(res.aic), 1)}
            convergencia[nombre] = convergio(res)
    r["reproducibilidad"]["convergencia"] = convergencia
    tabla = pd.DataFrame(resultados).T.sort_values("MAE")
    ganador = tabla.index[0]
    r["tabla"] = tabla.round(1).to_dict(orient="index")
    r["ganador"] = ganador
    modelo_ganador, escala_ganadora = origen[ganador]
    r["escala_ganadora"] = escala_ganadora

    fig, eje = plt.subplots(figsize=(11, 5))
    eje.plot(y.index[-36:], y.values[-36:], color="black", linewidth=2, label="real")
    for nombre in tabla.index[:4]:
        eje.plot(pronosticos[nombre].index, pronosticos[nombre]["mean"], marker="o", markersize=3, label=nombre)
    eje.axvline(prueba.index[0], color="gray", linestyle="--")
    eje.set_ylabel("lluvia mensual (mm)")
    eje.set_title("Los 4 mejores modelos en los 12 meses de prueba")
    eje.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(FIGURAS / "comparacion_modelos.png", dpi=120)
    plt.close(fig)

    # 4. Modelo ganador: se reajusta con toda la serie y se pronostican 12 meses con intervalo
    final, futuro = ajustar_y_pronosticar(modelo_ganador, y, HORIZONTE, escala_ganadora, ordenes[escala_ganadora])
    residuos = final.resid.iloc[13:] if modelo_ganador == "SARIMA" else final.resid
    futuro.index = pd.date_range(y.index[-1] + pd.offsets.MonthBegin(), periods=HORIZONTE, freq="MS")
    futuro = futuro.round(1)
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
    eje.set_title(f"Colima: pronostico de lluvia mensual a {HORIZONTE} meses")
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
    pico = max(r["pronostico"].items(), key=lambda kv: kv[1]["mean"])
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

## 3. Cuatro modelos, dos escalas y seleccion por error en prueba
Cada modelo se ajusto en dos escalas: **mm** (milimetros directos) y **log** (se modela log(1 + mm) y el pronostico se regresa a mm con exp(x) - 1). El error siempre se mide en mm sobre los 12 meses de prueba.
SARIMA: busqueda de ordenes por AIC en el entrenamiento, por escala; los 5 mejores: {r['sarima_top5']}.

| Modelo [escala] | MAE (mm) | RMSE (mm) | MAPE* | AIC (entrenamiento) |
|---|---|---|---|---|
{filas}

\\* MAPE calculado solo en los meses de prueba con lluvia real de 1 mm o mas (con 0 mm el porcentaje no existe).
El AIC solo es comparable entre modelos de la misma familia y la misma escala; por eso la seleccion se hace con el error en prueba.
Criterio de seleccion: **menor MAE**. Modelo ganador: **{r['ganador']}**.

![comparacion](figuras/comparacion_modelos.png)

## 4. Pronostico a 12 meses (modelo ganador reajustado con toda la serie)
| Mes | Pronostico (mm) | Intervalo de prediccion 95 % (mm) |
|---|---|---|
{pron}

Los valores negativos se recortan a 0 porque no existe lluvia negativa. Escala del modelo ganador: **{r['escala_ganadora']}**{" (el valor central es la mediana esperada)" if r['escala_ganadora'] == "log" else ""}.

![pronostico](figuras/pronostico.png)

**Frases para el cliente:**
- Para {primer[0]} se esperan alrededor de {primer[1]['mean']:.0f} mm de lluvia en el municipio de Colima, con un rango probable de {primer[1]['inferior']:.0f} a {primer[1]['superior']:.0f} mm.
- Para el mes mas lluvioso del pronostico ({pico[0]}) se esperan alrededor de {pico[1]['mean']:.0f} mm, con un rango probable de {pico[1]['inferior']:.0f} a {pico[1]['superior']:.0f} mm: conviene reservar toldos y personal con anticipacion para esa temporada.

## 5. Diagnostico de residuos del modelo ganador
- Ljung-Box (12 rezagos): estadistico {r['ljung_box']['estadistico']}, p = {r['ljung_box']['p']} -> residuos autocorrelacionados: {sig(r['ljung_box']['p'])}.
- Levene (primera vs segunda mitad): estadistico {r['levene']['estadistico']}, p = {r['levene']['p']} -> varianza cambia: {sig(r['levene']['p'])}.
- Shapiro-Wilk: estadistico {r['shapiro']['estadistico']}, p = {r['shapiro']['p']} -> residuos no normales: {sig(r['shapiro']['p'])}.

![residuos](figuras/residuos.png)

## 6. Reproducibilidad
Diagnostico (25-nov-2026): dos corridas con **el mismo archivo de datos** (misma huella SHA-256) y el mismo codigo de
ajuste dieron para Holt-Winters [mm] AIC 697.1 / MAE 43.7 y AIC 700.1 / MAE 47.3. Como el AIC cambio con datos
identicos, el optimizador termino en puntos distintos: con la inicializacion "estimated" buscaba 14 estados iniciales
ademas de los parametros de suavizamiento, un problema mal condicionado.
Correccion: (1) los modelos ETS usan `initialization_method="heuristic"` (estados iniciales con una regla fija) y
`maxiter=2000`; (2) el flujo `analisis` corre con un solo hilo de calculo numerico (`OMP_NUM_THREADS=1`) para que el
orden de las sumas no varie; (3) cada corrida guarda la huella de los datos y las versiones usadas, para fijarlas en
`requirements.txt` y poder distinguir si un cambio de resultado viene de los datos o del software.

- Huella de los datos (SHA-256 de `clima_municipio_mes.csv`): `{r['reproducibilidad']['sha256_datos']}`
- Python {r['reproducibilidad']['python']}; versiones: {r['reproducibilidad']['versiones']}
- Convergencia del optimizador por modelo: {r['reproducibilidad']['convergencia']}
"""
    (SALIDA / "pronostico.md").write_text(texto, encoding="utf-8")


if __name__ == "__main__":
    main()
