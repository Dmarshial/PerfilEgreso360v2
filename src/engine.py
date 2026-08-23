"""Motor analítico determinístico de PerfilEgreso 360.

Flujo: Evaluación -> Resultado de Aprendizaje -> Línea formativa -> Perfil.
La IA interpreta; nunca reemplaza estos cálculos.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from . import config

BANCO_ACCIONES = {
    "Crítica": [
        "Revisar la coherencia entre resultados de aprendizaje, actividades e instrumentos evaluativos.",
        "Incrementar experiencias prácticas y evaluaciones integradoras asociadas a la línea.",
        "Implementar un plan de refuerzo con responsables, plazos e indicador para el siguiente corte.",
    ],
    "Media": [
        "Aplicar acciones de refuerzo focalizadas en los resultados de aprendizaje con menor logro.",
        "Revisar retroalimentación y oportunidades de práctica antes del próximo corte.",
    ],
    "Baja": [
        "Mantener seguimiento y verificar estabilidad del logro en el siguiente corte.",
    ],
}


def normalizar_nota(nota: float, escala_min: float | None = None, escala_max: float | None = None) -> float:
    escala_min = config.ESCALA_NOTA_MIN if escala_min is None else escala_min
    escala_max = config.ESCALA_NOTA_MAX if escala_max is None else escala_max
    try:
        nota = float(nota)
    except (TypeError, ValueError):
        return np.nan
    pct = (nota - escala_min) / (escala_max - escala_min) * 100
    return float(max(0.0, min(100.0, pct)))


def _normalizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(c).strip() for c in out.columns]
    return out


def calcular_logro_por_linea(evaluaciones: pd.DataFrame, config_ra: pd.DataFrame,
                              ponderaciones: pd.DataFrame | None = None) -> pd.DataFrame:
    ev = _normalizar_columnas(evaluaciones)
    cra = _normalizar_columnas(config_ra)

    req_ev = {"student_id", "ra_id", "nota"}
    req_ra = {"ra_id", "linea"}
    if not req_ev.issubset(ev.columns):
        raise ValueError(f"Evaluaciones requiere columnas: {sorted(req_ev)}")
    if not req_ra.issubset(cra.columns):
        raise ValueError(f"Config_RA requiere columnas: {sorted(req_ra)}")

    df = ev.merge(cra[["ra_id", "linea"]].drop_duplicates(), on="ra_id", how="left")
    df = df[df["linea"].notna()].copy()
    df["logro_pct"] = pd.to_numeric(df.get("logro_pct"), errors="coerce") if "logro_pct" in df else np.nan
    faltan = df["logro_pct"].isna()
    df.loc[faltan, "logro_pct"] = df.loc[faltan, "nota"].apply(normalizar_nota)

    df["peso"] = 1.0
    if ponderaciones is not None and not ponderaciones.empty and "tipo_evaluacion" in df.columns:
        pon = _normalizar_columnas(ponderaciones)
        if {"tipo_evaluacion", "peso"}.issubset(pon.columns):
            pon = pon[["tipo_evaluacion", "peso"]].copy()
            pon["peso"] = pd.to_numeric(pon["peso"], errors="coerce").fillna(0)
            df = df.drop(columns=["peso"]).merge(pon, on="tipo_evaluacion", how="left")
            df["peso"] = df["peso"].fillna(1.0)

    df["pond"] = df["logro_pct"] * df["peso"]
    agg = (
        df.groupby(["student_id", "linea"], as_index=False)
          .agg(pond=("pond", "sum"), peso=("peso", "sum"), n_evidencias=("nota", "count"))
    )
    agg["logro_pct"] = np.where(agg["peso"] > 0, agg["pond"] / agg["peso"], np.nan)
    return agg[["student_id", "linea", "logro_pct", "n_evidencias"]].sort_values(["student_id", "linea"])


def calcular_brechas(logro_linea: pd.DataFrame, meta: float) -> pd.DataFrame:
    if logro_linea is None or logro_linea.empty:
        return pd.DataFrame(columns=["linea", "logro_pct", "meta", "brecha", "prioridad"])
    base = logro_linea.groupby("linea", as_index=False)["logro_pct"].mean()
    base["meta"] = float(meta)
    base["brecha"] = (base["meta"] - base["logro_pct"]).clip(lower=0)
    base["prioridad"] = pd.cut(
        base["brecha"], bins=[-0.01, 9.999, 19.999, float("inf")],
        labels=["Baja", "Media", "Crítica"]
    ).astype(str)
    return base.sort_values("brecha", ascending=False).reset_index(drop=True)


def alertas_tempranas(evaluaciones: pd.DataFrame, nota_corte: float | None = None) -> pd.DataFrame:
    nota_corte = config.NOTA_ALERTA if nota_corte is None else nota_corte
    if evaluaciones is None or evaluaciones.empty:
        return pd.DataFrame(columns=["student_id", "n_alertas", "nota_min"])
    ev = evaluaciones.copy()
    ev["nota"] = pd.to_numeric(ev["nota"], errors="coerce")
    bajas = ev[ev["nota"] < nota_corte].copy()
    if bajas.empty:
        return pd.DataFrame(columns=["student_id", "n_alertas", "nota_min"])
    cols = [c for c in ["student_id", "asignatura"] if c in bajas.columns]
    if "asignatura" in cols:
        out = (bajas.groupby("student_id", as_index=False)
                    .agg(n_alertas=("asignatura", "nunique"), nota_min=("nota", "min")))
    else:
        out = (bajas.groupby("student_id", as_index=False)
                    .agg(n_alertas=("nota", "size"), nota_min=("nota", "min")))
    return out.sort_values(["n_alertas", "nota_min"], ascending=[False, True])


def evolucion_por_corte(evaluaciones: pd.DataFrame, config_ra: pd.DataFrame, linea: str) -> pd.DataFrame:
    if "corte" not in evaluaciones.columns:
        return pd.DataFrame(columns=["corte", "logro_pct"])
    ev = evaluaciones.copy()
    cra = config_ra[["ra_id", "linea"]].drop_duplicates()
    df = ev.merge(cra, on="ra_id", how="left")
    df = df[df["linea"] == linea].copy()
    df["logro_pct"] = pd.to_numeric(df.get("logro_pct"), errors="coerce") if "logro_pct" in df else np.nan
    faltan = df["logro_pct"].isna()
    df.loc[faltan, "logro_pct"] = df.loc[faltan, "nota"].apply(normalizar_nota)
    return df.groupby("corte", as_index=False)["logro_pct"].mean().sort_values("corte")


def logro_global_por_estudiante(logro_linea: pd.DataFrame) -> pd.DataFrame:
    if logro_linea is None or logro_linea.empty:
        return pd.DataFrame(columns=["student_id", "logro_global", "nivel"])
    out = logro_linea.groupby("student_id", as_index=False)["logro_pct"].mean()
    out = out.rename(columns={"logro_pct": "logro_global"})
    out["nivel"] = out["logro_global"].apply(config.clasificar_nivel)
    return out.sort_values("logro_global", ascending=False)


def generar_recomendaciones(brechas: pd.DataFrame) -> pd.DataFrame:
    if brechas is None or brechas.empty:
        return pd.DataFrame(columns=["linea", "logro_pct", "brecha", "prioridad", "accion_sugerida"])
    filas = []
    for _, r in brechas.iterrows():
        prioridad = str(r["prioridad"])
        if prioridad == "Baja" and float(r["brecha"]) <= 0:
            continue
        acciones = BANCO_ACCIONES.get(prioridad, BANCO_ACCIONES["Baja"])
        filas.append({
            "linea": r["linea"],
            "logro_pct": round(float(r["logro_pct"]), 1),
            "brecha": round(float(r["brecha"]), 1),
            "prioridad": prioridad,
            "accion_sugerida": " ".join(acciones),
        })
    return pd.DataFrame(filas)
