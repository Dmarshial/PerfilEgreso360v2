"""
Motor analítico de PerfilEgreso 360.

Flujo: Evaluación -> Resultado de Aprendizaje -> Línea formativa -> Perfil de Egreso
Los indicadores se calculan siempre con reglas determinísticas; la IA
(ver ai.py) solo interpreta estos resultados, nunca los calcula.
"""

import pandas as pd

from . import config

# Banco de acciones sugeridas por defecto, usado por el motor de
# recomendaciones cuando no hay una IA disponible.
BANCO_ACCIONES = [
    "Revisar las actividades prácticas asociadas a esta línea",
    "Aumentar las experiencias aplicadas / de terreno",
    "Revisar los instrumentos evaluativos utilizados",
    "Implementar una evaluación integradora de cierre de ciclo",
    "Reforzar los resultados de aprendizaje con menor logro",
    "Establecer seguimiento específico para el próximo corte",
]


def normalizar_nota(nota: float, escala_min: float = None, escala_max: float = None) -> float:
    """Convierte una nota (por defecto escala 1.0–7.0 chilena) a % de logro."""
    escala_min = config.ESCALA_NOTA_MIN if escala_min is None else escala_min
    escala_max = config.ESCALA_NOTA_MAX if escala_max is None else escala_max
    pct = (nota - escala_min) / (escala_max - escala_min) * 100
    return max(0.0, min(100.0, pct))


def calcular_logro_por_linea(evaluaciones: pd.DataFrame, config_ra: pd.DataFrame,
                              ponderaciones: pd.DataFrame = None) -> pd.DataFrame:
    """Tributa cada evaluación a su línea formativa vía Config_RA, aplica
    ponderaciones por tipo de evidencia (si existen) y agrega el logro
    por estudiante y línea formativa."""

    df = evaluaciones.merge(config_ra[["ra_id", "linea"]], on="ra_id", how="left")
    df["logro_pct"] = df["nota"].apply(normalizar_nota)

    if ponderaciones is not None and "tipo_evaluacion" in df.columns:
        pesos = dict(zip(ponderaciones["tipo_evaluacion"], ponderaciones["peso"]))
        df["peso"] = df["tipo_evaluacion"].map(pesos).fillna(1.0)
    else:
        df["peso"] = 1.0

    df["logro_ponderado"] = df["logro_pct"] * df["peso"]

    agrupado = (
        df.groupby(["student_id", "linea"], as_index=False)
        .apply(lambda g: pd.Series({
            "logro_pct": g["logro_ponderado"].sum() / g["peso"].sum() if g["peso"].sum() else g["logro_pct"].mean()
        }))
        .reset_index(drop=True)
    )
    return agrupado


def logro_global_por_estudiante(logro_por_linea: pd.DataFrame) -> pd.DataFrame:
    return (
        logro_por_linea.groupby("student_id", as_index=False)["logro_pct"]
        .mean()
        .rename(columns={"logro_pct": "logro_global"})
    )


def calcular_brechas(logro_por_linea: pd.DataFrame, meta: float) -> pd.DataFrame:
    resumen = logro_por_linea.groupby("linea", as_index=False)["logro_pct"].mean()
    resumen["meta"] = meta
    resumen["brecha"] = (meta - resumen["logro_pct"]).clip(lower=0)
    resumen["prioridad"] = resumen["brecha"].apply(config.clasificar_prioridad)
    resumen["nivel"] = resumen["logro_pct"].apply(config.clasificar_nivel)
    return resumen.sort_values("brecha", ascending=False).reset_index(drop=True)


def alertas_tempranas(evaluaciones: pd.DataFrame, umbral: float = None) -> pd.DataFrame:
    umbral = config.NOTA_APROBACION if umbral is None else umbral
    riesgo = evaluaciones[evaluaciones["nota"] < umbral]
    return (
        riesgo.groupby("student_id", as_index=False)
        .size()
        .rename(columns={"size": "evaluaciones_bajo_umbral"})
        .sort_values("evaluaciones_bajo_umbral", ascending=False)
    )


def generar_recomendaciones(brechas: pd.DataFrame, max_acciones: int = 3) -> pd.DataFrame:
    """Motor de recomendaciones basado en reglas: prioridad de la brecha
    determina cuántas y qué tan urgentes son las acciones sugeridas."""
    filas = []
    for _, fila in brechas.iterrows():
        if fila["prioridad"] == "Baja":
            continue
        n_acciones = max_acciones if fila["prioridad"] == "Crítica" else max(2, max_acciones - 1)
        acciones = BANCO_ACCIONES[:n_acciones]
        filas.append(
            {
                "linea": fila["linea"],
                "logro_pct": round(fila["logro_pct"], 1),
                "meta": fila["meta"],
                "brecha": round(fila["brecha"], 1),
                "prioridad": fila["prioridad"],
                "acciones_sugeridas": " · ".join(acciones),
            }
        )
    return pd.DataFrame(filas)


def evolucion_por_corte(evaluaciones: pd.DataFrame, config_ra: pd.DataFrame,
                         linea: str = None) -> pd.DataFrame:
    """Serie de logro por corte, opcionalmente filtrada a una línea formativa."""
    if "corte" not in evaluaciones.columns:
        return pd.DataFrame(columns=["corte", "logro_pct"])

    df = evaluaciones.merge(config_ra[["ra_id", "linea"]], on="ra_id", how="left")
    if linea:
        df = df[df["linea"] == linea]
    df["logro_pct"] = df["nota"].apply(normalizar_nota)
    return (
        df.groupby("corte", as_index=False)["logro_pct"]
        .mean()
        .rename(columns={"logro_pct": "logro_pct"})
    )
