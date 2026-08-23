"""Interpretación ejecutiva asistida por IA, con fallback local."""
from __future__ import annotations

import pandas as pd


def _analisis_local(brechas: pd.DataFrame, logro_global: float, meta: float, alertas: int) -> str:
    nivel = "sobre la meta" if logro_global >= meta else "bajo la meta institucional"
    crit = brechas[brechas["prioridad"] == "Crítica"] if not brechas.empty else brechas
    med = brechas[brechas["prioridad"] == "Media"] if not brechas.empty else brechas
    partes = [
        f"El logro global observado es {logro_global:.1f}%, {nivel} de {meta:.0f}%.",
        f"Se registran {alertas} estudiantes con alerta temprana según calificaciones bajo el umbral definido.",
    ]
    if crit is not None and not crit.empty:
        top = crit.head(3)
        detalle = "; ".join(f"{r.linea}: brecha {r.brecha:.1f} pts" for _, r in top.iterrows())
        partes.append("Prioridades críticas: " + detalle + ".")
        partes.append("Se recomienda priorizar revisión de la alineación RA–actividad–evaluación, refuerzo práctico y seguimiento en el próximo corte.")
    elif med is not None and not med.empty:
        partes.append("No se identifican brechas críticas; existen brechas medias que requieren refuerzo focalizado y seguimiento.")
    else:
        partes.append("No se observan brechas relevantes frente a la meta; corresponde sostener el seguimiento longitudinal.")
    return " ".join(partes)


def analizar_con_ia(brechas: pd.DataFrame, logro_global: float, meta: float, alertas: int,
                    api_key: str | None = None) -> str:
    if not api_key:
        return _analisis_local(brechas, logro_global, meta, alertas)
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        tabla = brechas[["linea", "logro_pct", "brecha", "prioridad"]].round(1).to_dict("records") if not brechas.empty else []
        prompt = f"""
Eres un analista de aseguramiento de la calidad en educación superior.
Interpreta únicamente los datos agregados siguientes; no inventes causas como hechos.
Logro global: {logro_global:.1f}%
Meta: {meta:.1f}%
Estudiantes con alerta: {alertas}
Brechas: {tabla}

Entrega en español, máximo 350 palabras:
1) diagnóstico ejecutivo;
2) fortalezas;
3) brechas prioritarias;
4) causas posibles, explícitamente como hipótesis;
5) tres acciones de mejora medibles para el siguiente corte;
6) indicadores de seguimiento.
"""
        resp = client.responses.create(model="gpt-4.1-mini", input=prompt)
        return resp.output_text
    except Exception as e:
        local = _analisis_local(brechas, logro_global, meta, alertas)
        return local + f"\n\n[Análisis IA no disponible; se utilizó el motor local. Detalle técnico: {type(e).__name__}]"
