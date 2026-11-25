"""E1 · Calidad: fiabilidad y disponibilidad de la captura, medidas con la bitacora real.

Uso: python -m calidad.fiabilidad      (solo necesita pandas; escribe docs/E1/fiabilidad.md y .json)

Definiciones (documentadas tambien en el reporte):
- Corrida exitosa: todas sus peticiones terminaron con resultado "ok". Una sola peticion con error la vuelve fallida.
- Falla: paso de "funcionando" a "fallando" (una corrida fallida despues de una exitosa, o al inicio del periodo).
  Varias corridas fallidas seguidas son UNA sola falla (un mismo episodio).
- Reparacion: la falla termina cuando termina la siguiente corrida exitosa.
- Tiempo observado: del inicio de la primera corrida al fin de la ultima del periodo. Como el sistema solo se observa
  cuando corre, el estado cambia en los momentos de las corridas.
- MTTR = tiempo caido / fallas; MTBF = tiempo funcionando / fallas; A = MTBF / (MTBF + MTTR).
"""
import json
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
BITACORA = RAIZ / "calidad" / "bitacora_captura.csv"
SALIDA = RAIZ / "docs" / "E1"
META = 95.0  # objetivo 1 de E0: disponibilidad >= 95 %
CORRECCION = pd.Timestamp("2026-11-14T05:00:00Z")  # primera corrida con los defectos 1 y 2 ya corregidos
ENTREGA_E1 = pd.Timestamp("2026-11-13T23:59:00Z")  # 13-nov 17:59 hora de Colima
HORAS_ENTRE_CORRIDAS = 6  # cron "17 */6 * * *"


def corridas(ruta=BITACORA):
    """Una fila por corrida: inicio, fin, peticiones, peticiones ok y si la corrida fue exitosa."""
    b = pd.read_csv(ruta)
    b["t"] = pd.to_datetime(b["timestamp_utc"], utc=True)
    c = b.groupby("run_id").agg(inicio=("t", "min"), fin=("t", "max"), modo=("modo", "first"),
                                peticiones=("resultado", "size"),
                                ok=("resultado", lambda s: int((s == "ok").sum())))
    c["exitosa"] = c["ok"] == c["peticiones"]
    return c.sort_values("inicio").reset_index()


def metricas(c):
    """MTBF, MTTR y disponibilidad de un conjunto de corridas ordenadas por tiempo."""
    if c.empty:
        return None
    observado = (c["fin"].iloc[-1] - c["inicio"].iloc[0]).total_seconds() / 3600
    episodios, inicio_falla = [], None
    for fila in c.itertuples():
        if not fila.exitosa and inicio_falla is None:
            inicio_falla = fila.inicio
        elif fila.exitosa and inicio_falla is not None:
            episodios.append({"inicio": inicio_falla, "reparada": fila.fin,
                              "horas": (fila.fin - inicio_falla).total_seconds() / 3600})
            inicio_falla = None
    abierta = inicio_falla is not None
    if abierta:  # una falla sin reparar al cierre del periodo cuenta como caida hasta el final
        episodios.append({"inicio": inicio_falla, "reparada": None,
                          "horas": (c["fin"].iloc[-1] - inicio_falla).total_seconds() / 3600})
    caido = sum(e["horas"] for e in episodios)
    funcionando = observado - caido
    n = len(episodios)
    return {
        "desde": str(c["inicio"].iloc[0]), "hasta": str(c["fin"].iloc[-1]),
        "corridas": len(c), "corridas_exitosas": int(c["exitosa"].sum()),
        "tasa_exito_corridas": round(100 * c["exitosa"].mean(), 1),
        "peticiones": int(c["peticiones"].sum()), "peticiones_ok": int(c["ok"].sum()),
        "tasa_exito_peticiones": round(100 * c["ok"].sum() / c["peticiones"].sum(), 1),
        "horas_observadas": round(observado, 1), "horas_funcionando": round(funcionando, 1),
        "horas_caido": round(caido, 2), "fallas": n, "falla_abierta": abierta,
        "MTBF_h": round(funcionando / n, 1) if n else None,
        "MTTR_h": round(caido / n, 2) if n else None,
        "disponibilidad": round(100 * funcionando / observado, 2) if observado else None,
        "episodios": [{"inicio": str(e["inicio"]), "reparada": str(e["reparada"]), "horas": round(e["horas"], 2)}
                      for e in episodios],
    }


def corridas_esperadas(desde, hasta):
    """Horarios del cron (minuto 17 de las 0, 6, 12 y 18 h UTC) dentro del periodo."""
    horarios = pd.date_range(desde.floor("D"), hasta.ceil("D"), freq=f"{HORAS_ENTRE_CORRIDAS}h") + pd.Timedelta("17min")
    return int(((horarios >= desde) & (horarios <= hasta)).sum())


def main():
    c = corridas()
    fin = c["fin"].iloc[-1]
    periodos = {
        "completo": c,
        "desde_correccion": c[c["inicio"] >= CORRECCION],
        "ultimos_14_dias": c[c["inicio"] >= fin - pd.Timedelta(days=14)],
        "antes_de_E1": c[c["inicio"] <= ENTREGA_E1],
    }
    r = {nombre: metricas(sub) for nombre, sub in periodos.items()}
    inc = c[c["modo"] == "incremental"]
    inc_corr = inc[inc["inicio"] >= CORRECCION]
    esperadas_corr = corridas_esperadas(CORRECCION, fin)
    r["cron"] = {"incrementales_ejecutadas": len(inc),
                 "horarios_del_cron": corridas_esperadas(inc["inicio"].iloc[0], fin),
                 "desde_correccion": {"horarios_del_cron": esperadas_corr,
                                      "incrementales_exitosas": int(inc_corr["exitosa"].sum()),
                                      "porcentaje": round(100 * inc_corr["exitosa"].sum() / esperadas_corr, 1)}}
    r["corridas"] = [{"run_id": int(f.run_id), "inicio": str(f.inicio), "modo": f.modo,
                      "peticiones": int(f.peticiones), "ok": int(f.ok), "exitosa": bool(f.exitosa)}
                     for f in c.itertuples()]
    SALIDA.mkdir(parents=True, exist_ok=True)
    (SALIDA / "fiabilidad.json").write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
    escribir_reporte(r)
    print(json.dumps({k: v for k, v in r.items() if k != "corridas"}, indent=2, ensure_ascii=False))


def _fmt(v, sufijo=""):
    return "no definido (0 fallas)" if v is None else f"{v}{sufijo}"


def escribir_reporte(r):
    nombres = {"completo": "Periodo completo", "desde_correccion": "Desde la correccion (14-nov)",
               "ultimos_14_dias": "Ultimos 14 dias", "antes_de_E1": "Antes de la entrega E1 (hasta 13-nov 17:59)"}
    filas = []
    for clave, titulo in nombres.items():
        m = r[clave]
        if m is None:
            filas.append(f"| {titulo} | sin corridas | | | | | | |")
            continue
        cumple = "si" if m["disponibilidad"] is not None and m["disponibilidad"] >= META else "no"
        filas.append(
            f"| {titulo} | {m['desde'][:16]} a {m['hasta'][:16]} | {m['corridas_exitosas']}/{m['corridas']} "
            f"({m['tasa_exito_corridas']} %) | {m['peticiones_ok']}/{m['peticiones']} ({m['tasa_exito_peticiones']} %) "
            f"| {m['fallas']} | {_fmt(m['MTBF_h'], ' h')} | {_fmt(m['MTTR_h'], ' h')} "
            f"| {m['disponibilidad']} % ({cumple}) |")
    episodios = "\n".join(f"- {e['inicio'][:16]} -> {e['reparada'][:16]}: {e['horas']} h"
                          for e in r["completo"]["episodios"])
    texto = f"""# Fiabilidad y disponibilidad de la captura (E1 · Calidad)

Generado por `python -m calidad.fiabilidad` a partir de `calidad/bitacora_captura.csv` (una fila por peticion).
Horas en UTC. Meta (objetivo 1 de E0): disponibilidad >= {META:.0f} %.

## Definiciones
- **Corrida exitosa:** todas sus peticiones terminaron "ok".
- **Falla:** paso de funcionando a fallando; varias corridas fallidas seguidas cuentan como una sola falla.
- **Reparacion:** termina con la siguiente corrida exitosa.
  Tiempo caido = de la primera corrida fallida a esa reparacion.
- **MTBF** = horas funcionando / fallas · **MTTR** = horas caido / fallas · **A** = MTBF / (MTBF + MTTR).
  Cuando no hay fallas, MTBF y MTTR no estan definidos; la disponibilidad es 100 % del tiempo observado.

## Resultados
| Periodo | Ventana (UTC) | Corridas exitosas | Peticiones ok | Fallas | MTBF | MTTR | Disponibilidad (cumple meta) |
|---|---|---|---|---|---|---|---|
{chr(10).join(filas)}

Episodios de falla en el periodo completo:
{episodios}

Programacion: el cron pide una corrida cada {HORAS_ENTRE_CORRIDAS} h
({r['cron']['horarios_del_cron']} horarios desde la primera corrida incremental), pero GitHub ejecuto
{r['cron']['incrementales_ejecutadas']} corridas incrementales: GitHub Actions no garantiza las ejecuciones
programadas y omite o retrasa algunas cuando tiene alta demanda.
Desde la correccion: {r['cron']['desde_correccion']['incrementales_exitosas']} corridas incrementales exitosas de
{r['cron']['desde_correccion']['horarios_del_cron']} horarios del cron
({r['cron']['desde_correccion']['porcentaje']} %).
Todas las corridas que GitHub si ejecuto desde entonces terminaron bien; las faltantes nunca se iniciaron.
"""
    (SALIDA / "fiabilidad.md").write_text(texto, encoding="utf-8")


if __name__ == "__main__":
    main()
