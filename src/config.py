"""
Configuración institucional por defecto de PerfilEgreso 360.
Estos valores son de ejemplo/demostración: cada carrera debe poder
sobrescribirlos desde el módulo de Configuración de la app.
"""

APP_TITLE = "PerfilEgreso 360"
APP_SUBTITLE = "Sistema de seguimiento y aseguramiento del logro del Perfil de Egreso"

# Meta institucional de logro (%) — configurable en la app
META_INSTITUCIONAL_DEFAULT = 85

# Escala de notas chilena usada para normalizar a % de logro
ESCALA_NOTA_MIN = 1.0
ESCALA_NOTA_MAX = 7.0
NOTA_APROBACION = 4.0  # referencia para alertas tempranas

# Umbrales de clasificación de desempeño (en % de logro)
NIVELES_DESEMPENO = [
    (90, "Desempeño Estratégico"),
    (80, "Integrado Alto"),
    (70, "En Desarrollo"),
    (0, "Crítico"),
]

# Umbrales del motor de brechas (en puntos porcentuales bajo la meta)
BRECHA_CRITICA = 20
BRECHA_MEDIA = 10

# Líneas formativas de ejemplo (demo) — reemplazables por carrera
LINEAS_FORMATIVAS_DEMO = [
    "Evaluación y diagnóstico",
    "Prescripción del ejercicio",
    "Intervención profesional",
    "Investigación aplicada",
    "Gestión",
    "Comunicación y liderazgo",
]

# Ponderación por tipo de evidencia (%) — configurable
PONDERACIONES_DEMO = {
    "Evaluación académica": 40,
    "Actividad práctica": 30,
    "Evaluación interciclo": 20,
    "Evaluación externa/nacional": 10,
}

# Tipos de reportes agrupados bajo el módulo "Reportes"
TIPOS_REPORTE = [
    "Alerta temprana",
    "Competencias",
    "Líneas formativas",
    "Total líneas",
    "Total competencias",
]


def clasificar_nivel(logro_pct: float) -> str:
    """Devuelve la clasificación de desempeño para un % de logro dado."""
    for umbral, etiqueta in NIVELES_DESEMPENO:
        if logro_pct >= umbral:
            return etiqueta
    return NIVELES_DESEMPENO[-1][1]


def clasificar_prioridad(brecha_pts: float) -> str:
    """Clasifica la prioridad de intervención según el tamaño de la brecha."""
    if brecha_pts >= BRECHA_CRITICA:
        return "Crítica"
    if brecha_pts >= BRECHA_MEDIA:
        return "Media"
    return "Baja"
