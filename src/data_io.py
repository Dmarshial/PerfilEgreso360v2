"""Entrada de datos: demo, plantilla propia y acta institucional USEK."""
from __future__ import annotations

import io
import re
import numpy as np
import pandas as pd

from . import config


def generar_datos_demo(n_estudiantes: int = 40, seed: int = 42) -> dict:
    rng = np.random.default_rng(seed)
    n_estudiantes = int(n_estudiantes)
    cohortes = rng.choice([2024, 2025, 2026], size=n_estudiantes, p=[0.2, 0.35, 0.45])
    estudiantes = pd.DataFrame({
        "student_id": [f"E{i:04d}" for i in range(1, n_estudiantes + 1)],
        "nombre": [f"Estudiante {i:02d}" for i in range(1, n_estudiantes + 1)],
        "cohorte": cohortes,
        "carrera": "Ciencias de la Actividad Física y del Deporte",
    })

    lineas = config.LINEAS_DEMO
    config_lineas = pd.DataFrame({"linea": lineas, "meta": config.META_INSTITUCIONAL_DEFAULT})
    ras = []
    for i, linea in enumerate(lineas, start=1):
        ras.append({"ra_id": f"RA{i:02d}A", "resultado_aprendizaje": f"RA aplicado de {linea}", "linea": linea})
        ras.append({"ra_id": f"RA{i:02d}B", "resultado_aprendizaje": f"RA integrador de {linea}", "linea": linea})
    config_ra = pd.DataFrame(ras)

    ponderaciones = pd.DataFrame({
        "tipo_evaluacion": ["Prueba", "Práctica", "Taller", "Interciclo", "Externa"],
        "peso": [25, 35, 15, 15, 10],
    })

    filas = []
    tipos = ponderaciones["tipo_evaluacion"].tolist()
    cortes = ["Corte 1", "Corte 2", "Corte 3"]
    for sid in estudiantes["student_id"]:
        habilidad = rng.normal(5.25, 0.55)
        for _, ra in config_ra.iterrows():
            for corte_idx, corte in enumerate(cortes):
                nota = np.clip(habilidad + corte_idx * 0.10 + rng.normal(0, 0.55), 1.0, 7.0)
                filas.append({
                    "student_id": sid,
                    "asignatura": f"Asignatura {rng.integers(1, 13):02d}",
                    "ra_id": ra["ra_id"],
                    "tipo_evaluacion": rng.choice(tipos, p=[0.26, 0.34, 0.18, 0.14, 0.08]),
                    "nota": round(float(nota), 1),
                    "corte": corte,
                })
    evaluaciones = pd.DataFrame(filas)
    return {
        "estudiantes": estudiantes,
        "evaluaciones": evaluaciones,
        "config_lineas": config_lineas,
        "config_ra": config_ra,
        "ponderaciones": ponderaciones,
    }


def _canon(s: str) -> str:
    s = str(s).strip().lower()
    s = re.sub(r"[^a-záéíóúüñ0-9]+", "_", s)
    return s.strip("_")


def _renombrar(df: pd.DataFrame, mapa: dict[str, list[str]]) -> pd.DataFrame:
    cols = {_canon(c): c for c in df.columns}
    ren = {}
    for destino, candidatos in mapa.items():
        for c in candidatos:
            if _canon(c) in cols:
                ren[cols[_canon(c)]] = destino
                break
    return df.rename(columns=ren)


def leer_plantilla_propia(archivo) -> dict:
    xls = pd.ExcelFile(archivo)
    requeridas = ["Estudiantes", "Evaluaciones", "Config_Lineas", "Config_RA", "Ponderaciones"]
    faltan = [h for h in requeridas if h not in xls.sheet_names]
    if faltan:
        raise ValueError("Faltan hojas requeridas: " + ", ".join(faltan))

    estudiantes = pd.read_excel(xls, "Estudiantes")
    evaluaciones = pd.read_excel(xls, "Evaluaciones")
    config_lineas = pd.read_excel(xls, "Config_Lineas")
    config_ra = pd.read_excel(xls, "Config_RA")
    ponderaciones = pd.read_excel(xls, "Ponderaciones")

    estudiantes = _renombrar(estudiantes, {
        "student_id": ["student_id", "id_estudiante", "id alumno", "rut", "r.u.t."],
        "nombre": ["nombre", "nombres", "estudiante", "alumno"],
        "cohorte": ["cohorte", "año_ingreso", "ano_ingreso"],
        "carrera": ["carrera", "programa"],
    })
    evaluaciones = _renombrar(evaluaciones, {
        "student_id": ["student_id", "id_estudiante", "rut"],
        "asignatura": ["asignatura", "curso"],
        "ra_id": ["ra_id", "id_ra", "resultado_aprendizaje"],
        "tipo_evaluacion": ["tipo_evaluacion", "tipo", "evidencia"],
        "nota": ["nota", "calificacion", "calificación"],
        "corte": ["corte", "periodo", "momento"],
    })
    config_lineas = _renombrar(config_lineas, {
        "linea": ["linea", "nombre_linea", "línea", "linea_formativa"],
        "meta": ["meta", "meta_logro", "meta_porcentaje"],
    })
    config_ra = _renombrar(config_ra, {
        "ra_id": ["ra_id", "id_ra"],
        "resultado_aprendizaje": ["resultado_aprendizaje", "resultado de aprendizaje", "ra"],
        "linea": ["linea", "nombre_linea", "linea_formativa"],
    })
    ponderaciones = _renombrar(ponderaciones, {
        "tipo_evaluacion": ["tipo_evaluacion", "tipo", "evidencia"],
        "peso": ["peso", "ponderacion", "ponderación", "porcentaje"],
    })

    obligatorias = {
        "Estudiantes": (estudiantes, ["student_id", "nombre", "cohorte"]),
        "Evaluaciones": (evaluaciones, ["student_id", "ra_id", "nota"]),
        "Config_RA": (config_ra, ["ra_id", "linea"]),
        "Config_Lineas": (config_lineas, ["linea"]),
        "Ponderaciones": (ponderaciones, ["tipo_evaluacion", "peso"]),
    }
    errores = []
    for hoja, (df, cols) in obligatorias.items():
        miss = [c for c in cols if c not in df.columns]
        if miss:
            errores.append(f"{hoja}: {', '.join(miss)}")
    if errores:
        raise ValueError("Columnas faltantes — " + " | ".join(errores))

    if "meta" not in config_lineas:
        config_lineas["meta"] = config.META_INSTITUCIONAL_DEFAULT
    if "tipo_evaluacion" not in evaluaciones:
        evaluaciones["tipo_evaluacion"] = "Evaluación"
    return {
        "estudiantes": estudiantes,
        "evaluaciones": evaluaciones,
        "config_lineas": config_lineas,
        "config_ra": config_ra,
        "ponderaciones": ponderaciones,
    }


def _valor_cercano(df: pd.DataFrame, texto: str, max_col_offset: int = 8):
    texto = texto.lower()
    for r in range(df.shape[0]):
        for c in range(df.shape[1]):
            v = df.iat[r, c]
            if isinstance(v, str) and texto in v.lower():
                for cc in range(c + 1, min(df.shape[1], c + max_col_offset + 1)):
                    val = df.iat[r, cc]
                    if pd.notna(val) and str(val).strip() not in {"", "nan"}:
                        return val
    return None


def leer_acta_usek(archivo) -> pd.DataFrame:
    """Lee el formato real de Acta de Calificaciones Semestrales USEK.

    Devuelve formato largo por estudiante-asignatura, con NF y asistencia.
    La tributación a RA/línea se configura después, porque el acta no la contiene.
    """
    try:
        xls = pd.ExcelFile(archivo)
    except Exception as e:
        raise ValueError(f"No fue posible abrir el archivo: {e}")

    resultados = []
    for hoja in xls.sheet_names:
        raw = pd.read_excel(xls, sheet_name=hoja, header=None)
        if raw.empty:
            continue

        # Busca la fila donde aparece N° ORDEN / RUT; en el archivo real es la 11 (base 0).
        header_idx = None
        for i in range(min(len(raw), 40)):
            fila = " | ".join(str(x) for x in raw.iloc[i].tolist() if pd.notna(x)).upper()
            if ("N° ORDEN" in fila or "Nº ORDEN" in fila or "R.U.T." in fila) and "NOMBRES" in fila:
                header_idx = i
                break
        if header_idx is None:
            continue

        asign_idx = max(0, header_idx - 1)
        headers = raw.iloc[header_idx].tolist()
        asignaturas_row = raw.iloc[asign_idx].tolist()

        carrera = _valor_cercano(raw.iloc[:header_idx+1], "carrera")
        nivel = _valor_cercano(raw.iloc[:header_idx+1], "nivel")
        periodo = _valor_cercano(raw.iloc[:header_idx+1], "periodo")
        anio = None
        for x in raw.iloc[:header_idx+1].astype(str).values.ravel().tolist():
            m = re.search(r"AÑO:\s*(\d{4})", x, flags=re.I)
            if m:
                anio = int(m.group(1)); break

        # Primeras 5 columnas: orden, paterno, materno, nombres, RUT.
        # Desde col 5: pares NF / %A; nombre de asignatura vive en la fila anterior.
        for r in range(header_idx + 1, len(raw)):
            orden = raw.iat[r, 0] if raw.shape[1] > 0 else None
            rut = raw.iat[r, 4] if raw.shape[1] > 4 else None
            if pd.isna(orden) or pd.isna(rut):
                continue
            if not str(orden).strip().replace(".", "", 1).isdigit():
                continue
            paterno = raw.iat[r, 1] if raw.shape[1] > 1 else ""
            materno = raw.iat[r, 2] if raw.shape[1] > 2 else ""
            nombres = raw.iat[r, 3] if raw.shape[1] > 3 else ""
            nombre = " ".join(str(x).strip() for x in [nombres, paterno, materno] if pd.notna(x) and str(x).strip())

            c = 5
            while c < raw.shape[1] - 1:
                h = str(headers[c]).strip().upper() if pd.notna(headers[c]) else ""
                if h == "NF":
                    asignatura = asignaturas_row[c]
                    if pd.isna(asignatura) or str(asignatura).strip() in {"", "nan"}:
                        c += 2; continue
                    nota = raw.iat[r, c]
                    asis = raw.iat[r, c + 1] if c + 1 < raw.shape[1] else None
                    nota_num = pd.to_numeric(pd.Series([nota]).replace("/", np.nan), errors="coerce").iloc[0]
                    asis_num = pd.to_numeric(pd.Series([asis]).replace("/", np.nan), errors="coerce").iloc[0]
                    resultados.append({
                        "student_id": str(rut).strip(),
                        "rut": str(rut).strip(),
                        "nombre": nombre,
                        "asignatura": str(asignatura).strip(),
                        "nota": nota_num,
                        "asistencia_pct": asis_num,
                        "carrera": carrera,
                        "nivel": nivel,
                        "periodo": periodo,
                        "anio": anio,
                        "hoja_origen": hoja,
                    })
                    c += 2
                else:
                    c += 1

    out = pd.DataFrame(resultados)
    if out.empty:
        raise ValueError("No se reconoció la estructura del Acta USEK. Verifica que sea un Acta de Calificaciones Semestrales.")
    return out
