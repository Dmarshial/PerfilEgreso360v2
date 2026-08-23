"""Configuración funcional de PerfilEgreso 360."""

APP_TITLE = "PerfilEgreso 360"
APP_SUBTITLE = "Sistema de seguimiento y aseguramiento del logro del Perfil de Egreso"
META_INSTITUCIONAL_DEFAULT = 85
ESCALA_NOTA_MIN = 1.0
ESCALA_NOTA_MAX = 7.0
NOTA_ALERTA = 4.0

TIPOS_REPORTE = [
    "Alerta temprana",
    "Competencias",
    "Líneas formativas",
    "Total líneas",
    "Total competencias",
]

LINEAS_DEMO = [
    "Fundamentos de la Actividad Física",
    "Evaluación Funcional",
    "Prescripción del Ejercicio",
    "Intervención en Contextos Reales",
    "Investigación Aplicada",
    "Gestión Deportiva",
    "Ética y Responsabilidad",
    "Comunicación y Liderazgo",
]


def clasificar_nivel(logro: float) -> str:
    """Clasificación inicial; debe validarse institucionalmente."""
    if logro >= 90:
        return "Desempeño Estratégico"
    if logro >= 80:
        return "Integrado Alto"
    if logro >= 70:
        return "En Desarrollo"
    return "Crítico"
