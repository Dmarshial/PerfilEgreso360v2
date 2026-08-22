"""
Visualizaciones de PerfilEgreso 360 con Plotly.
El radar es la visualización insignia del proyecto (concepto "ficha de
futbolista"), pero conviven con gráficos de brechas y evolución.
"""

import plotly.express as px
import plotly.graph_objects as go


PITCH = "#3f6b4e"
AMBER = "#e8a33d"
CORAL = "#c15139"
INK = "#12181f"
PAPER = "#f4efe3"
MIST = "#8b93a1"


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
        fillcolor="rgba(63,107,78,0.35)",
        fill="toself",
    ))

    fig.update_layout(
        title=titulo,
        polar=dict(
            bgcolor=INK,
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(244,239,227,0.15)",
                             tickfont=dict(color=MIST, size=9)),
            angularaxis=dict(gridcolor="rgba(244,239,227,0.15)", tickfont=dict(color=PAPER, size=11)),
        ),
        paper_bgcolor=INK,
        font=dict(color=PAPER),
        showlegend=True,
        legend=dict(orientation="h", y=-0.1),
        margin=dict(t=50, b=40, l=40, r=40),
    )
    return fig


def barras_brechas(brechas_df) -> go.Figure:
    color_map = {"Crítica": CORAL, "Media": AMBER, "Baja": PITCH}
    fig = px.bar(
        brechas_df, x="brecha", y="linea", orientation="h",
        color="prioridad", color_discrete_map=color_map,
        labels={"brecha": "Brecha (pts)", "linea": ""},
    )
    fig.update_layout(
        paper_bgcolor=INK, plot_bgcolor=INK, font=dict(color=PAPER),
        yaxis=dict(autorange="reversed"), margin=dict(t=20, b=20, l=10, r=10),
    )
    return fig


def linea_evolucion(evolucion_df, meta: float, titulo: str = "") -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=evolucion_df["corte"], y=evolucion_df["logro_pct"],
        mode="lines+markers+text",
        text=[f"{v:.0f}%" for v in evolucion_df["logro_pct"]],
        textposition="top center",
        line=dict(color=PITCH, width=3), marker=dict(size=9, color=PITCH),
        name="Logro observado",
    ))
    fig.add_hline(y=meta, line_dash="dash", line_color=AMBER,
                   annotation_text=f"Meta {meta}%", annotation_font_color=AMBER)
    fig.update_layout(
        title=titulo, paper_bgcolor=INK, plot_bgcolor=INK, font=dict(color=PAPER),
        yaxis=dict(range=[0, 100], gridcolor="rgba(244,239,227,0.1)"),
        xaxis=dict(gridcolor="rgba(244,239,227,0.1)"),
        margin=dict(t=40, b=20, l=20, r=20),
    )
    return fig
