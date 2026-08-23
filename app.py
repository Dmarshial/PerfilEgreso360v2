"""
PerfilEgreso 360 — Sistema de seguimiento y aseguramiento del logro
del Perfil de Egreso.

Ejecutar con:  streamlit run app.py
"""

import streamlit as st
import pandas as pd

from src import auth, config, data_io, engine, charts, ai, reports, theme

st.set_page_config(page_title=config.APP_TITLE, page_icon="🎯", layout="wide")
theme.inject_theme()

# --------------------------------------------------------------------------
# Puerta de acceso — nada se dibuja sin una sesión de Google autorizada
# --------------------------------------------------------------------------
usuario = auth.exigir_login()


# --------------------------------------------------------------------------
# Estado inicial
# --------------------------------------------------------------------------
def init_state():
    defaults = {
        "estudiantes": None,
        "evaluaciones": None,
        "config_lineas": None,
        "config_ra": None,
        "ponderaciones": None,
        "meta": config.META_INSTITUCIONAL_DEFAULT,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def hay_datos() -> bool:
    return st.session_state["evaluaciones"] is not None and st.session_state["config_ra"] is not None


init_state()

# Sincroniza la sesión con la identidad autenticada: si entra otra cuenta en
# este navegador, los datos cargados por la anterior se descartan.
auth.sincronizar_sesion(usuario)


# --------------------------------------------------------------------------
# Sidebar / navegación
# --------------------------------------------------------------------------
st.sidebar.title(f"🎯 {config.APP_TITLE}")
st.sidebar.caption(config.APP_SUBTITLE)
auth.barra_usuario(usuario)
st.sidebar.divider()
modulo = st.sidebar.radio(
    "Módulo",
    ["Captura", "Configuración", "Análisis y diagnóstico", "Recomendaciones", "Reportes"],
)
st.sidebar.divider()
st.sidebar.metric("Meta institucional", f"{st.session_state['meta']}%")
st.sidebar.caption("Datos cargados" if hay_datos() else "Sin datos cargados aún")


# --------------------------------------------------------------------------
# Módulo 1 — Captura de datos
# --------------------------------------------------------------------------
if modulo == "Captura":
    st.header("📥 Captura de datos")
    st.write(
        "PerfilEgreso 360 debe adaptarse al archivo institucional, no al revés. "
        "Puedes cargar un acta institucional, la plantilla propia, o usar datos de demostración."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Datos de demostración")
        n_demo = st.number_input("N.º de estudiantes demo", 10, 200, 40)
        if st.button("Cargar datos de demostración", width='stretch'):
            datos = data_io.generar_datos_demo(n_demo)
            for k, v in datos.items():
                st.session_state[k] = v
            st.success("Datos de demostración cargados.")

    with col2:
        st.subheader("Plantilla propia (.xlsx)")
        archivo_propio = st.file_uploader("Estudiantes / Evaluaciones / Config_Lineas / Config_RA / Ponderaciones",
                                           type=["xlsx"], key="propio")
        if archivo_propio and st.button("Procesar plantilla", width='stretch'):
            datos = data_io.leer_plantilla_propia(archivo_propio)
            for k, v in datos.items():
                st.session_state[k] = v
            st.success("Plantilla cargada.")

    with col3:
        st.subheader("Acta institucional USEK (.xlsx)")
        archivo_acta = st.file_uploader("Acta de Calificaciones Semestrales", type=["xlsx"], key="acta")
        if archivo_acta and st.button("Procesar acta", width='stretch'):
            try:
                acta = data_io.leer_acta_usek(archivo_acta)
                st.session_state["_acta_cruda"] = acta
                st.warning(
                    "Acta leída correctamente. Falta asociarla a Resultados de Aprendizaje "
                    "y líneas formativas para integrarla al cálculo (ver pendientes en README.md)."
                )
                st.dataframe(acta.head(20), width='stretch')
            except ValueError as e:
                st.error(str(e))

    if hay_datos():
        st.divider()
        st.subheader("Vista previa de los datos cargados")
        tabs = st.tabs(["Estudiantes", "Evaluaciones", "Config_RA", "Config_Lineas", "Ponderaciones"])
        claves = ["estudiantes", "evaluaciones", "config_ra", "config_lineas", "ponderaciones"]
        for tab, clave in zip(tabs, claves):
            with tab:
                df = st.session_state[clave]
                if df is not None:
                    st.dataframe(df.head(30), width='stretch')


# --------------------------------------------------------------------------
# Módulo 2 — Configuración
# --------------------------------------------------------------------------
elif modulo == "Configuración":
    st.header("⚙️ Configuración")
    st.write("El 'cerebro académico' del sistema: aquí se define cómo se lee el logro para esta carrera.")

    st.session_state["meta"] = st.slider("Meta institucional de logro (%)", 50, 100, st.session_state["meta"])

    if not hay_datos():
        st.info("Carga datos en el módulo Captura para configurar líneas y ponderaciones.")
    else:
        st.subheader("Líneas formativas y su meta")
        st.session_state["config_lineas"] = st.data_editor(
            st.session_state["config_lineas"], num_rows="dynamic", width='stretch'
        )

        st.subheader("Resultados de Aprendizaje → Línea formativa")
        st.session_state["config_ra"] = st.data_editor(
            st.session_state["config_ra"], num_rows="dynamic", width='stretch'
        )

        st.subheader("Ponderación por tipo de evidencia")
        st.session_state["ponderaciones"] = st.data_editor(
            st.session_state["ponderaciones"], num_rows="dynamic", width='stretch'
        )


# --------------------------------------------------------------------------
# Módulo 3 — Análisis y diagnóstico
# --------------------------------------------------------------------------
elif modulo == "Análisis y diagnóstico":
    st.header("📊 Análisis y diagnóstico")

    if not hay_datos():
        st.info("Carga datos en el módulo Captura para ver el análisis.")
    else:
        nivel = st.radio("Nivel de análisis", ["Individual", "Cohorte", "Carrera"], horizontal=True)
        meta = st.session_state["meta"]

        logro_linea = engine.calcular_logro_por_linea(
            st.session_state["evaluaciones"], st.session_state["config_ra"],
            st.session_state["ponderaciones"],
        )

        if nivel == "Individual":
            estudiante = st.selectbox("Estudiante", st.session_state["estudiantes"]["student_id"])
            datos_est = logro_linea[logro_linea["student_id"] == estudiante]
            if datos_est.empty:
                st.warning("Sin evaluaciones para este estudiante.")
            else:
                logro_global = datos_est["logro_pct"].mean()
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.metric("Logro perfil de egreso", f"{logro_global:.0f}%")
                    st.metric("Clasificación", config.clasificar_nivel(logro_global))
                with c2:
                    fig = charts.radar_perfil(
                        datos_est["linea"].tolist(), datos_est["logro_pct"].round(1).tolist(),
                        meta, titulo=f"Ficha — {estudiante}",
                    )
                    st.plotly_chart(fig, width='stretch')
                st.dataframe(datos_est.rename(columns={"logro_pct": "logro (%)"}), width='stretch')

        elif nivel == "Cohorte":
            cohorte_sel = st.selectbox("Cohorte", sorted(st.session_state["estudiantes"]["cohorte"].unique()))
            ids_cohorte = st.session_state["estudiantes"].query("cohorte == @cohorte_sel")["student_id"]
            datos_cohorte = logro_linea[logro_linea["student_id"].isin(ids_cohorte)]
            promedio = datos_cohorte.groupby("linea", as_index=False)["logro_pct"].mean()
            c1, c2 = st.columns([1, 2])
            with c1:
                st.metric("Logro promedio cohorte", f"{promedio['logro_pct'].mean():.0f}%")
                st.metric("N.º de estudiantes", len(ids_cohorte))
            with c2:
                fig = charts.radar_perfil(
                    promedio["linea"].tolist(), promedio["logro_pct"].round(1).tolist(),
                    meta, titulo=f"Perfil promedio — cohorte {cohorte_sel}",
                )
                st.plotly_chart(fig, width='stretch')

        else:  # Carrera
            promedio = logro_linea.groupby("linea", as_index=False)["logro_pct"].mean()
            logro_global = promedio["logro_pct"].mean()
            c1, c2, c3 = st.columns(3)
            c1.metric("Logro global", f"{logro_global:.0f}%")
            c2.metric("Meta institucional", f"{meta}%")
            brechas = engine.calcular_brechas(logro_linea, meta)
            c3.metric("Brechas críticas", int((brechas["prioridad"] == "Crítica").sum()))
            fig = charts.radar_perfil(
                promedio["linea"].tolist(), promedio["logro_pct"].round(1).tolist(),
                meta, titulo="Perfil de la carrera",
            )
            st.plotly_chart(fig, width='stretch')

        st.divider()
        st.subheader("Brechas por línea formativa")
        brechas = engine.calcular_brechas(logro_linea, meta)
        st.plotly_chart(charts.barras_brechas(brechas), width='stretch')

        st.subheader("Alertas tempranas")
        alertas = engine.alertas_tempranas(st.session_state["evaluaciones"])
        st.metric("Estudiantes con alerta", len(alertas))
        st.dataframe(alertas, width='stretch')

        if "corte" in st.session_state["evaluaciones"].columns:
            st.subheader("Evolución por corte")
            linea_sel = st.selectbox("Línea formativa", brechas["linea"])
            evol = engine.evolucion_por_corte(st.session_state["evaluaciones"], st.session_state["config_ra"], linea_sel)
            st.plotly_chart(charts.linea_evolucion(evol, meta, titulo=f"Evolución — {linea_sel}"), width='stretch')


# --------------------------------------------------------------------------
# Módulo 4 — Recomendaciones
# --------------------------------------------------------------------------
elif modulo == "Recomendaciones":
    st.header("💡 Recomendaciones de aseguramiento de la calidad")

    if not hay_datos():
        st.info("Carga datos en el módulo Captura para generar recomendaciones.")
    else:
        meta = st.session_state["meta"]
        logro_linea = engine.calcular_logro_por_linea(
            st.session_state["evaluaciones"], st.session_state["config_ra"], st.session_state["ponderaciones"]
        )
        brechas = engine.calcular_brechas(logro_linea, meta)
        recomendaciones = engine.generar_recomendaciones(brechas)

        if recomendaciones.empty:
            st.success("No hay brechas de prioridad media o crítica en este corte.")
        else:
            st.dataframe(recomendaciones, width='stretch')

        st.divider()
        st.subheader("Diagnóstico ejecutivo")
        api_key = st.text_input("OpenAI API key (opcional — se usa análisis local si se deja vacío)", type="password")
        if st.button("Generar diagnóstico"):
            logro_global = logro_linea["logro_pct"].mean()
            alertas = len(engine.alertas_tempranas(st.session_state["evaluaciones"]))
            texto = ai.analizar_con_ia(brechas, logro_global, meta, alertas, api_key=api_key or None)
            st.info(texto)


# --------------------------------------------------------------------------
# Módulo 5 — Reportes
# --------------------------------------------------------------------------
elif modulo == "Reportes":
    st.header("📑 Reportes")

    if not hay_datos():
        st.info("Carga datos en el módulo Captura para generar reportes.")
    else:
        tipo = st.selectbox("Tipo de reporte", config.TIPOS_REPORTE)
        meta = st.session_state["meta"]
        logro_linea = engine.calcular_logro_por_linea(
            st.session_state["evaluaciones"], st.session_state["config_ra"], st.session_state["ponderaciones"]
        )

        if tipo == "Alerta temprana":
            df = engine.alertas_tempranas(st.session_state["evaluaciones"])
        elif tipo == "Competencias":
            df = logro_linea.rename(columns={"linea": "competencia"})
        elif tipo == "Líneas formativas":
            df = engine.calcular_brechas(logro_linea, meta)
        elif tipo == "Total líneas":
            df = logro_linea.groupby("linea", as_index=False)["logro_pct"].mean()
        else:  # Total competencias
            df = engine.logro_global_por_estudiante(logro_linea)

        st.dataframe(df, width='stretch')

        excel_bytes = reports.exportar_excel({tipo: df})
        st.download_button(
            "Descargar reporte (Excel)", data=excel_bytes,
            file_name=f"{tipo.lower().replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
