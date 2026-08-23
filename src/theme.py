"""
Tema visual de PerfilEgreso 360 para Streamlit.

Cambio respecto de la versión anterior: la base deja de ser negra.
El fondo oscuro se veía bien en el mockup, pero en pantalla larga y con
tablas, formularios y gráficos encima castigaba la legibilidad.

Nueva lógica: la app es un *dossier impreso* — papel claro, tinta oscura,
reglas finas — y el negro queda reservado como acento (encabezado de la
ficha individual), no como fondo general. Se mantienen la tipografía y la
paleta del proyecto: Oswald para títulos, Source Serif 4 para texto,
IBM Plex Mono para etiquetas y datos.
"""

import streamlit as st

# Paleta única del proyecto — charts.py importa desde aquí para no duplicar.
PAPER = "#f7f3ea"        # fondo base
SURFACE = "#ffffff"      # tarjetas y tablas
INK = "#101820"          # texto principal
INK_SOFT = "#55606f"     # texto secundario (contraste ~5.3:1 sobre papel)
RULE = "rgba(16,24,32,0.14)"
RULE_STRONG = "rgba(16,24,32,0.30)"
AMBER = "#9a6410"        # acento legible sobre papel (texto y bordes)
AMBER_FILL = "#e0942b"   # acento para relleno de gráficos
PITCH = "#2c6647"        # verde institucional (logro)
PITCH_SOFT = "rgba(44,102,71,0.18)"
CORAL = "#a4351f"        # alerta / brecha crítica

CSS = f"""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,500;8..60,600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">

<style>
:root{{
  --paper:{PAPER};
  --surface:{SURFACE};
  --ink:{INK};
  --ink-soft:{INK_SOFT};
  --rule:{RULE};
  --rule-strong:{RULE_STRONG};
  --amber:{AMBER};
  --pitch:{PITCH};
  --coral:{CORAL};
}}

/* base */
.stApp{{
  background: var(--paper) !important;
  color: var(--ink) !important;
  font-family: 'Source Serif 4', serif !important;
}}
.stApp p, .stApp li, .stApp label, .stApp span, .stApp div[data-testid="stMarkdownContainer"]{{
  color: var(--ink);
}}

/* sidebar — papel un tono más cálido, no un bloque negro */
section[data-testid="stSidebar"]{{
  background: #efe8d9 !important;
  border-right: 1px solid var(--rule-strong);
}}
section[data-testid="stSidebar"] *{{ color: var(--ink) !important; }}
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"]{{ color: var(--ink-soft) !important; }}

/* títulos */
h1, h2, h3, [data-testid="stMetricValue"]{{
  font-family: 'Oswald', sans-serif !important;
  color: var(--ink) !important;
  letter-spacing: .01em;
}}
h1{{ border-bottom: 2px solid var(--ink); padding-bottom: 10px; }}
h2{{ border-bottom: 1px solid var(--rule); padding-bottom: 6px; }}

/* etiquetas, captions y datos */
[data-testid="stCaptionContainer"], .stCaption, small, code{{
  font-family: 'IBM Plex Mono', monospace !important;
  color: var(--ink-soft) !important;
}}

/* métricas como fichas de KPI */
[data-testid="stMetric"]{{
  background: var(--surface);
  border: 1px solid var(--rule);
  border-left: 3px solid var(--pitch);
  border-radius: 4px;
  padding: 14px 16px;
}}
[data-testid="stMetricLabel"]{{
  font-family: 'IBM Plex Mono', monospace !important;
  font-size: 11px !important;
  letter-spacing: .06em;
  text-transform: uppercase;
  color: var(--ink-soft) !important;
}}
[data-testid="stMetricValue"]{{ color: var(--pitch) !important; }}

/* botones */
.stButton > button, .stDownloadButton > button{{
  font-family: 'Oswald', sans-serif !important;
  letter-spacing: .04em;
  text-transform: uppercase;
  font-size: 13px !important;
  background: var(--surface) !important;
  color: var(--ink) !important;
  border: 1px solid var(--rule-strong) !important;
  border-radius: 3px !important;
}}
.stButton > button:hover, .stDownloadButton > button:hover{{
  border-color: var(--amber) !important;
  color: var(--amber) !important;
}}
.stButton > button[kind="primary"]{{
  background: var(--ink) !important;
  color: var(--paper) !important;
  border-color: var(--ink) !important;
}}
.stButton > button[kind="primary"]:hover{{
  background: var(--pitch) !important;
  border-color: var(--pitch) !important;
  color: #ffffff !important;
}}
.stButton > button:focus-visible, .stDownloadButton > button:focus-visible{{
  outline: 2px solid var(--amber) !important;
  outline-offset: 2px;
}}

/* pestañas */
button[data-baseweb="tab"]{{
  font-family: 'Oswald', sans-serif !important;
  letter-spacing: .04em;
  text-transform: uppercase;
  font-size: 13px !important;
  color: var(--ink-soft) !important;
}}
button[aria-selected="true"][data-baseweb="tab"]{{
  color: var(--ink) !important;
  border-bottom-color: var(--amber) !important;
}}

/* radios y selectores */
div[role="radiogroup"] label{{
  font-family: 'IBM Plex Mono', monospace !important;
  font-size: 13px !important;
}}

/* sliders */
div[data-testid="stSlider"] [role="slider"]{{ background: var(--amber) !important; }}

/* tablas y editores */
[data-testid="stDataFrame"], [data-testid="stDataEditor"]{{
  border: 1px solid var(--rule);
  border-radius: 4px;
  overflow: hidden;
  background: var(--surface);
}}

hr{{ border-color: var(--rule) !important; }}

div[data-testid="stAlertContainer"]{{
  font-family: 'Source Serif 4', serif !important;
  border-radius: 4px;
}}

/* ---------------- pantalla de acceso ---------------- */
.pe-gate{{
  background: var(--surface);
  border: 1px solid var(--rule-strong);
  border-top: 4px solid var(--ink);
  border-radius: 4px;
  padding: 32px 30px 26px;
  margin: 8vh 0 18px;
}}
.pe-gate-eyebrow{{
  font-family: 'IBM Plex Mono', monospace;
  font-size: 11px;
  letter-spacing: .16em;
  text-transform: uppercase;
  color: var(--coral);
  margin: 0 0 10px;
}}
.pe-gate-title{{
  font-family: 'Oswald', sans-serif;
  font-size: 34px;
  line-height: 1.1;
  color: var(--ink);
  margin: 0 0 4px;
  border: none;
}}
.pe-gate-sub{{
  font-family: 'Source Serif 4', serif;
  color: var(--ink-soft);
  font-size: 15px;
  margin: 0 0 18px;
}}
.pe-gate-text{{
  font-family: 'Source Serif 4', serif;
  color: var(--ink);
  font-size: 15px;
  line-height: 1.55;
  margin: 0;
  padding-top: 14px;
  border-top: 1px solid var(--rule);
}}

/* ---------------- tarjeta de usuario (sidebar) ---------------- */
.pe-user{{
  display: flex;
  flex-direction: column;
  gap: 2px;
  background: var(--surface);
  border: 1px solid var(--rule);
  border-left: 3px solid var(--amber);
  border-radius: 4px;
  padding: 10px 12px;
  margin-bottom: 8px;
}}
.pe-user-rol{{
  font-family: 'IBM Plex Mono', monospace;
  font-size: 10px;
  letter-spacing: .12em;
  text-transform: uppercase;
  color: var(--amber) !important;
}}
.pe-user-name{{
  font-family: 'Oswald', sans-serif;
  font-size: 15px;
  color: var(--ink) !important;
}}
.pe-user-mail{{
  font-family: 'IBM Plex Mono', monospace;
  font-size: 11px;
  color: var(--ink-soft) !important;
  word-break: break-all;
}}
</style>
"""


def inject_theme():
    st.markdown(CSS, unsafe_allow_html=True)
