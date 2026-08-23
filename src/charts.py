"""
Visualizaciones de PerfilEgreso 360 con Plotly.

El radar sigue siendo la visualización insignia (concepto "ficha de
futbolista"), pero ahora se dibuja sobre fondo claro para acompañar el tema
papel de la app. Los colores se importan de theme.py: una sola paleta para
CSS y gráficos.
"""

import plotly.express as px
import plotly.graph_objects as go

from src.theme import (
    AMBER,
    AMBER_FILL,
    CORAL,
    INK,
    INK_SOFT,
    PITCH,
    PITCH_SOFT,
    SURFACE,
)

# Fondo transparente: el gráfico hereda el papel de la app y no queda un
# rectángulo de otro color flotando dentro de la página.
TRANSPARENTE = "rgba(0,0,0,0)"
GRID = "rgba(16,24,32,0.16)"

LAYOUT_BASE = dict(
    paper_bgcolor=TRANSPARENTE,
    plot_bgcolor=TRANSPARENTE,
    font=dict(color=INK, family="Source Serif 4, serif"),
)


def radar_perfil(dimensiones: list, valores: list, meta: float, titulo: str = "") -> go.Figure:
    """Radar de competencias con la meta institucional superpuesta,
    replicando la ficha individual tipo jugador."""
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=[meta] * len(dimensiones) + [meta],
        theta=dimensiones + [dimensiones[0]],
        name="Meta institucional",
        line=dict(color=AMBER, dash="dash", width=1.5),
        fill=None,
    ))

    fig.add_trace(go.Scatterpolar(
        r=valores + [valores[0]],
        theta=dimensiones + [dimensiones[0]],
        name="Logro",
        line=dict(color=PITCH, width=2.5),
        fillcolor=PITCH_SOFT,
        fill="toself",
    ))

    fig.update_layout(
        title=dict(text=titulo, font=dict(color=INK, family="Oswald, sans-serif", size=18)),
        polar=dict(
            bgcolor=SURFACE,
            radialaxis=dict(visible=True, range=[0, 100], gridcolor=GRID,
                            linecolor=GRID, tickfont=dict(color=INK_SOFT, size=9)),
            angularaxis=dict(gridcolor=GRID, linecolor=GRID,
                             tickfont=dict(color=INK, size=11)),
        ),
        showlegend=True,
        legend=dict(orientation="h", y=-0.1, font=dict(color=INK_SOFT)),
        margin=dict(t=50, b=40, l=40, r=40),
        **LAYOUT_BASE,
    )
    return fig


def barras_brechas(brechas_df) -> go.Figure:
    color_map = {"Crítica": CORAL, "Media": AMBER_FILL, "Baja": PITCH}
    fig = px.bar(
        brechas_df, x="brecha", y="linea", orientation="h",
        color="prioridad", color_discrete_map=color_map,
        labels={"brecha": "Brecha (pts)", "linea": ""},
    )
    fig.update_layout(
        yaxis=dict(autorange="reversed", gridcolor=GRID),
        xaxis=dict(gridcolor=GRID, zerolinecolor=GRID),
        legend=dict(font=dict(color=INK_SOFT)),
        margin=dict(t=20, b=20, l=10, r=10),
        **LAYOUT_BASE,
    )
    return fig


def linea_evolucion(evolucion_df, meta: float, titulo: str = "") -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=evolucion_df["corte"], y=evolucion_df["logro_pct"],
        mode="lines+markers+text",
        text=[f"{v:.0f}%" for v in evolucion_df["logro_pct"]],
        textposition="top center",
        textfont=dict(color=INK),
        line=dict(color=PITCH, width=3), marker=dict(size=9, color=PITCH),
        name="Logro observado",
    ))
    fig.add_hline(y=meta, line_dash="dash", line_color=AMBER,
                  annotation_text=f"Meta {meta}%", annotation_font_color=AMBER)
    fig.update_layout(
        title=dict(text=titulo, font=dict(color=INK, family="Oswald, sans-serif", size=18)),
        yaxis=dict(range=[0, 100], gridcolor=GRID),
        xaxis=dict(gridcolor=GRID),
        margin=dict(t=40, b=20, l=20, r=20),
        **LAYOUT_BASE,
    )
    return fig
