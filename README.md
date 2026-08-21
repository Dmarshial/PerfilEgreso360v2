# PerfilEgreso 360

Sistema de seguimiento y aseguramiento del logro del Perfil de Egreso, inspirado
en las fichas de rendimiento deportivo (radar de competencias, "ficha de jugador")
aplicadas a evidencia académica.

> Transforma calificaciones y evaluaciones dispersas en un perfil visual,
> longitudinal y accionable del logro del Perfil de Egreso — a nivel individual,
> de cohorte y de carrera — con detección de brechas, recomendaciones de mejora
> y análisis asistido por IA.

## Ejecutar localmente

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Abre el módulo **Captura** y presiona **"Cargar datos de demostración"** para
explorar la app sin necesidad de un archivo real.

## Estructura del proyecto

```
PerfilEgreso360/
├── app.py                 # App Streamlit — navegación por los 5 módulos
├── src/
│   ├── config.py           # Meta institucional, líneas formativas, umbrales
│   ├── data_io.py           # Datos demo + lectura de Excel (plantilla propia y acta USEK)
│   ├── engine.py            # Cálculo de logro, brechas, niveles y recomendaciones
│   ├── charts.py            # Radar de competencias y gráficos de evolución/brechas
│   ├── ai.py                 # Interpretación con IA (OpenAI opcional + fallback local)
│   └── reports.py            # Exportación de reportes a Excel
├── data/demo/                # (reservado para archivos de ejemplo)
├── requirements.txt
└── README.md
```

## Flujo conceptual

```
Evaluación → Resultado de Aprendizaje → Línea formativa → Perfil de Egreso
     ↓
Motor de tributación (engine.py) → Logro por línea/estudiante
     ↓
Brechas = Meta institucional − Logro observado
     ↓
Recomendaciones (reglas) + Diagnóstico ejecutivo (IA opcional)
     ↓
Reportes exportables (Excel)
```

## Los 5 módulos

1. **Captura** — carga datos de demostración, la plantilla propia (6 hojas) o
   un acta institucional real (USEK). Principio de diseño: *la app se adapta
   al archivo institucional, no al revés*.
2. **Configuración** — el "cerebro académico": meta institucional, líneas
   formativas, Resultados de Aprendizaje y ponderaciones por tipo de evidencia,
   editables por carrera.
3. **Análisis y diagnóstico** — vista Individual (ficha tipo jugador con
   radar), Cohorte y Carrera; brechas por línea, alertas tempranas y
   evolución por corte.
4. **Recomendaciones** — motor de reglas que prioriza acciones según el
   tamaño de la brecha, más un diagnóstico ejecutivo (IA opcional vía OpenAI,
   con fallback local si no hay API key).
5. **Reportes** — Alerta temprana, Competencias, Líneas formativas, Total
   líneas y Total competencias, todos agrupados bajo un mismo módulo y
   exportables a Excel.

## Pendientes conocidos

Estos quedaron identificados como trabajo abierto y conviene abordarlos antes
de un uso institucional real:

- [ ] Definir el modelo académico definitivo (competencias vs. líneas vs. RA)
- [ ] Construir la matriz de tributación real (qué asignatura/RA alimenta
      cada línea y con qué peso)
- [ ] Validar académicamente los umbrales de clasificación (70/80/90) y la
      meta de 85%
- [ ] Robustecer `leer_acta_usek()` para distintos formatos de acta y carreras
- [ ] Incorporar evidencias externas (pruebas nacionales, interciclo,
      estandarizadas) sin distorsionar el resultado
- [ ] Persistencia en base de datos (cohortes, cortes e históricos —
      Streamlit hoy solo procesa en memoria/sesión)
- [ ] Roles y permisos (Administrador, Calidad, Director de Carrera, Docente)
- [ ] Exportación a PDF ejecutivo (hoy solo Excel)
- [ ] Seguimiento de acciones de mejora (responsable, plazo, indicador,
      estado, resultado en el siguiente corte)
- [ ] Diseño UI definitivo tipo dossier/ejecutivo (ver mockup HTML del
      proyecto — ficha individual + panel ejecutivo)

## Despliegue

Pensado para desplegarse en **Streamlit Community Cloud** conectando este
repositorio de GitHub directamente.
