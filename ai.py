"""
Capa de interpretación con IA.

Principio de diseño: la IA nunca calcula los indicadores (eso lo hace
engine.py de forma determinística); solo redacta el diagnóstico
ejecutivo a partir de resultados ya calculados. Si no hay API key
configurada, se usa un generador local basado en reglas.

Por privacidad, este módulo recibe datos agregados (por línea/carrera),
no antecedentes individuales de estudiantes (RUT, nombre, etc.).
"""

import os


def _resumen_local(brechas_df, logro_global: float, meta: float, alertas: int) -> str:
    criticas = brechas_df[brechas_df["prioridad"] == "Crítica"]
    fortalezas = brechas_df.sort_values("logro_pct", ascending=False).head(1)

    texto = [
        f"El logro global alcanza {logro_global:.0f}%, "
        f"{'sobre' if logro_global >= meta else 'bajo'} la meta institucional de {meta}%."
    ]

    if not fortalezas.empty:
        f = fortalezas.iloc[0]
        texto.append(f"{f['linea']} se mantiene como la línea más consolidada ({f['logro_pct']:.0f}%).")

    if not criticas.empty:
        nombres = ", ".join(criticas["linea"].tolist())
        texto.append(f"Las brechas críticas se concentran en: {nombres}.")

    if alertas:
        texto.append(f"Se registran {alertas} estudiantes con alerta temprana en el corte actual.")

    return " ".join(texto)


def analizar_con_ia(brechas_df, logro_global: float, meta: float, alertas: int,
                     api_key: str = None) -> str:
    """Devuelve un diagnóstico ejecutivo en texto. Usa OpenAI si hay
    api_key disponible (parámetro o variable de entorno OPENAI_API_KEY);
    de lo contrario, cae al análisis local basado en reglas."""

    api_key = api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return _resumen_local(brechas_df, logro_global, meta, alertas)

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        contexto = brechas_df[["linea", "logro_pct", "meta", "brecha", "prioridad"]].to_dict("records")
        prompt = (
            "Eres un analista de aseguramiento de la calidad de una universidad. "
            "A partir de estos datos AGREGADOS (ya calculados, no los recalcules), "
            "redacta un diagnóstico ejecutivo breve en español, en tono institucional, "
            "de máximo 3 párrafos, sin inventar cifras nuevas.\n\n"
            f"Logro global: {logro_global:.1f}%\n"
            f"Meta institucional: {meta}%\n"
            f"Alertas tempranas: {alertas} estudiantes\n"
            f"Detalle por línea formativa: {contexto}"
        )

        respuesta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return respuesta.choices[0].message.content.strip()

    except Exception as exc:  # noqa: BLE001 — fallback ante cualquier error de red/API
        return _resumen_local(brechas_df, logro_global, meta, alertas) + \
            f"\n\n_(Análisis local — no se pudo contactar la IA: {exc})_"
