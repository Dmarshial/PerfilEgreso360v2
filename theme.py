"""
Tema visual de PerfilEgreso 360 para Streamlit.

Streamlit por defecto no tiene identidad propia: este módulo inyecta la
misma paleta y tipografía del mockup (dossier tipo ficha de jugador +
panel ejecutivo) para que la app no se vea como un prototipo genérico.
"""

import streamlit as st

CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,500;8..60,600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">

<style>
:root{
  --ink:#12181f;
  --ink-soft:#1a2330;
  --ink-line: rgba(244,239,227,0.10);
  --ink-line-strong: rgba(244,239,227,0.20);
  --paper:#f4efe3;
  --amber:#e8a33d;
  --pitch:#3f6b4e;
  --pitch-bright:#5c9770;
  --coral:#c15139;
  --mist:#8b93a1;
}

/* base */
.stApp{
  background: var(--ink) !important;
  color: var(--paper) !important;
  font-family: 'Source Serif 4', serif !important;
}

/* sidebar */
section[data-testid="stSidebar"]{
  background: var(--ink-soft) !important;
  border-right: 1px solid var(--ink-line-strong);
}
section[data-testid="stSidebar"] * { color: var(--paper) !important; }

/* headings */
h1, h2, h3, [data-testid="stMetricValue"]{
  font-family: 'Oswald', sans-serif !important;
  letter-spacing: .01em;
  text-transform: none;
}
h1 { border-bottom: 1px solid var(--ink-line-strong); padding-bottom: 10px; }

/* eyebrow / captions / mono labels */
[data-testid="stCaptionContainer"], .stCaption, small, code{
  font-family: 'IBM Plex Mono', monospace !important;
  color: var(--mist) !important;
}

/* metrics as "kpi cards" */
[data-testid="stMetric"]{
  background: var(--ink-soft);
  border: 1px solid var(--ink-line);
  border-radius: 6px;
  padding: 14px 16px;
}
[data-testid="stMetricLabel"]{
  font-family: 'IBM Plex Mono', monospace !important;
  font-size: 11px !important;
  letter-spacing: .06em;
  text-transform: uppercase;
  color: var(--mist) !important;
}
[data-testid="stMetricValue"]{ color: var(--pitch-bright) !important; }

/* buttons */
.stButton > button, .stDownloadButton > button{
  font-family: 'Oswald', sans-serif !important;
  letter-spacing: .04em;
  text-transform: uppercase;
  font-size: 13px !important;
  background: transparent !important;
  color: var(--paper) !important;
  border: 1px solid var(--ink-line-strong) !important;
  border-radius: 3px !important;
}
.stButton > button:hover, .stDownloadButton > button:hover{
  border-color: var(--amber) !important;
  color: var(--amber) !important;
}
.stButton > button[kind="primary"]{
  background: var(--amber) !important;
  color: var(--ink) !important;
  border-color: var(--amber) !important;
}

/* tabs */
button[data-baseweb="tab"]{
  font-family: 'Oswald', sans-serif !important;
  letter-spacing: .04em;
  text-transform: uppercase;
  font-size: 13px !important;
  color: var(--mist) !important;
}
button[aria-selected="true"][data-baseweb="tab"]{
  color: var(--amber) !important;
  border-bottom-color: var(--amber) !important;
}

/* radio / segmented controls (módulo, nivel de análisis) */
div[role="radiogroup"] label{
  font-family: 'IBM Plex Mono', monospace !important;
  font-size: 13px !important;
}

/* sliders */
div[data-testid="stSlider"] [role="slider"]{ background: var(--amber) !important; }

/* dataframes / tables */
[data-testid="stDataFrame"]{
  border: 1px solid var(--ink-line);
  border-radius: 6px;
  overflow: hidden;
}

/* dividers */
hr{ border-color: var(--ink-line-strong) !important; }

/* alerts (info/success/warning/error) keep readable on dark bg */
div[data-testid="stAlertContainer"]{
  font-family: 'Source Serif 4', serif !important;
  border-radius: 6px;
}
</style>
"""


def inject_theme():
    st.markdown(CSS, unsafe_allow_html=True)
