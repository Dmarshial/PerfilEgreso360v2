"""
Carga de datos para PerfilEgreso 360.

Principio de diseño (definido en el proyecto original):
la aplicación debe adaptarse al archivo institucional, no al revés.
Por eso `leer_acta_usek` intenta reconocer columnas típicas de un acta
de calificaciones en vez de exigir una plantilla rígida.
"""

import io
import numpy as np
import pandas as pd

from . import config

RNG = np.random.default_rng(42)


# --------------------------------------------------------------------------
# Datos de demostración
# --------------------------------------------------------------------------
def generar_datos_demo(n_estudiantes: int = 40) -> dict:
    """Genera un set de datos sintético con la misma estructura de 6 hojas
    planteada originalmente: Estudiantes, Evaluaciones, Config_Lineas,
    Config_RA, Ponderaciones, Recomendaciones (esta última se calcula, no
    se genera aquí)."""

    lineas = config.LINEAS_FORMATIVAS_DEMO

    # Config_RA: 1-2 resultados de aprendizaje por línea
    config_ra = pd.DataFrame(
        [
            {"ra_id": f"RA{str(i+1).zfill(2)}", "resultado": f"Resultado de aprendizaje {i+1}", "linea": linea}
            for i, linea in enumerate(lineas)
        ]
    )

    config_lineas = pd.DataFrame(
        [{"linea": linea, "meta": config.META_INSTITUCIONAL_DEFAULT} for linea in lineas]
    )

    ponderaciones = pd.DataFrame(
        [{"tipo_evaluacion": k, "peso": v} for k, v in config.PONDERACIONES_DEMO.items()]
    )

    estudiantes = pd.DataFrame(
        [
            {
                "student_id": f"E{str(i+1).zfill(3)}",
                "nombre": f"Estudiante {i+1}",
                "carrera": "Ciencias de la Actividad Física y del Deporte",
                "cohorte": RNG.choice([2022, 2023, 2024]),
                "sede": "Providencia",
                "semestre": RNG.integers(3, 9),
            }
            for i in range(n_estudiantes)
        ]
    )

    tipos_eval = list(config.PONDERACIONES_DEMO.keys())
    cortes = ["Corte 1", "Corte 2", "Corte 3"]

    filas = []
    for _, est in estudiantes.iterrows():
        # cada estudiante tiene un nivel base por línea, con variación por corte
        for _, ra in config_ra.iterrows():
            base = RNG.normal(loc=75, scale=12)
            for i_corte, corte in enumerate(cortes):
                mejora = i_corte * RNG.normal(3, 2)
                nota = np.clip((base + mejora) / 100 * 6 + 1, 1.0, 7.0)
                filas.append(
                    {
                        "student_id": est["student_id"],
                        "asignatura": f"Asignatura {ra['linea'][:12]}",
                        "ra_id": ra["ra_id"],
                        "tipo_evaluacion": RNG.choice(tipos_eval),
                        "nota": round(nota, 1),
                        "corte": corte,
                    }
                )
    evaluaciones = pd.DataFrame(filas)

    return {
        "estudiantes": estudiantes,
        "evaluaciones": evaluaciones,
        "config_lineas": config_lineas,
        "config_ra": config_ra,
        "ponderaciones": ponderaciones,
    }


# --------------------------------------------------------------------------
# Plantilla propia de PerfilEgreso 360 (6 hojas)
# --------------------------------------------------------------------------
def leer_plantilla_propia(archivo) -> dict:
    """Lee un Excel con las hojas: Estudiantes, Evaluaciones, Config_Lineas,
    Config_RA, Ponderaciones."""
    xls = pd.ExcelFile(archivo)
    data = {}
    mapeo = {
        "Estudiantes": "estudiantes",
        "Evaluaciones": "evaluaciones",
        "Config_Lineas": "config_lineas",
        "Config_RA": "config_ra",
        "Ponderaciones": "ponderaciones",
    }
    for hoja, clave in mapeo.items():
        if hoja in xls.sheet_names:
            data[clave] = pd.read_excel(xls, sheet_name=hoja)
    return data


# --------------------------------------------------------------------------
# Acta de Calificaciones Semestrales USEK (formato institucional real)
# --------------------------------------------------------------------------
# Alias de columnas esperables en un acta real. Se ajusta según el archivo
# institucional efectivo cuando esté disponible.
ALIAS_COLUMNAS = {
    "student_id": ["rut", "run", "id_estudiante", "student_id"],
    "nombre": ["nombre", "alumno", "estudiante"],
    "asignatura": ["asignatura", "curso", "sigla"],
    "nota": ["nota final", "nota_final", "calificacion final", "nota", "calif. final"],
    "estado": ["estado", "resultado", "aprobacion"],
}


def _encontrar_columna(columnas, alias):
    columnas_lower = {c.lower().strip(): c for c in columnas}
    for a in alias:
        if a in columnas_lower:
            return columnas_lower[a]
    return None


def leer_acta_usek(archivo) -> pd.DataFrame:
    """Intenta reconocer un acta institucional real y devolverla en un
    formato mínimo estandarizado (student_id, nombre, asignatura, nota).

    Este lector es un punto de partida: falta robustecerlo para los
    distintos formatos de acta que puedan existir (ver pendientes del
    proyecto en README.md).
    """
    df = pd.read_excel(archivo)
    columnas = list(df.columns)

    col_id = _encontrar_columna(columnas, ALIAS_COLUMNAS["student_id"])
    col_nombre = _encontrar_columna(columnas, ALIAS_COLUMNAS["nombre"])
    col_asig = _encontrar_columna(columnas, ALIAS_COLUMNAS["asignatura"])
    col_nota = _encontrar_columna(columnas, ALIAS_COLUMNAS["nota"])

    faltantes = [n for n, c in [("identificador", col_id), ("nota", col_nota)] if c is None]
    if faltantes:
        raise ValueError(
            f"No se pudieron identificar columnas de {', '.join(faltantes)} en el acta. "
            "Revisa el formato o usa la plantilla propia de PerfilEgreso 360."
        )

    salida = pd.DataFrame(
        {
            "student_id": df[col_id].astype(str),
            "nombre": df[col_nombre] if col_nombre else "",
            "asignatura": df[col_asig] if col_asig else "Sin especificar",
            "nota": pd.to_numeric(df[col_nota], errors="coerce"),
        }
    ).dropna(subset=["nota"])

    return salida
