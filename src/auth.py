"""
Control de acceso de PerfilEgreso 360.

Usa la autenticación OIDC nativa de Streamlit (st.login / st.user / st.logout,
disponible desde Streamlit 1.42) con Google como proveedor de identidad.

Dos capas:
  1. Autenticación  — quién eres (lo resuelve Google).
  2. Autorización   — si ese correo puede entrar (lista blanca en secrets.toml).

Configuración esperada en .streamlit/secrets.toml (ver secrets.toml.example):

    [auth]
    redirect_uri = "http://localhost:8501/oauth2callback"
    cookie_secret = "..."
    client_id = "...apps.googleusercontent.com"
    client_secret = "..."
    server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"

    [acceso]
    dominios_permitidos = ["usek.cl", "uisek.cl"]
    correos_permitidos  = ["persona.externa@gmail.com"]
    permitir_sin_login  = false     # true solo para desarrollo local

    [acceso.roles]
    "diego.marcial@usek.cl" = "Administrador"
"""

import streamlit as st

from src import config

CLAVES_DATOS = [
    "estudiantes",
    "evaluaciones",
    "config_lineas",
    "config_ra",
    "ponderaciones",
    "_acta_cruda",
]


# --------------------------------------------------------------------------
# Lectura de configuración
# --------------------------------------------------------------------------
def _acceso() -> dict:
    try:
        return dict(st.secrets.get("acceso", {}))
    except Exception:
        return {}


def _auth_configurado() -> bool:
    try:
        return "auth" in st.secrets
    except Exception:
        return False


def _soporta_login() -> bool:
    """Streamlit >= 1.42 expone st.login y st.user.is_logged_in."""
    return hasattr(st, "login") and hasattr(st, "user")


def rol_de(email: str) -> str:
    roles = _acceso().get("roles", {}) or {}
    return roles.get(email, roles.get(email.lower(), "Invitado"))


def autorizado(email: str) -> bool:
    """True si el correo está en la lista blanca (dominio o correo puntual)."""
    if not email:
        return False
    email = email.strip().lower()
    acc = _acceso()
    dominios = [d.strip().lower().lstrip("@") for d in acc.get("dominios_permitidos", [])]
    correos = [c.strip().lower() for c in acc.get("correos_permitidos", [])]

    # Sin lista blanca definida: basta con haber iniciado sesión con Google.
    if not dominios and not correos:
        return True

    if email in correos:
        return True
    return any(email.endswith("@" + d) for d in dominios)


# --------------------------------------------------------------------------
# Pantallas
# --------------------------------------------------------------------------
def _portada(mensaje_error: str = "", detalle: str = ""):
    """Pantalla de acceso: nada de la app se dibuja detrás de esto."""
    izq, centro, der = st.columns([1, 1.6, 1])
    with centro:
        st.markdown(
            f"""
            <div class="pe-gate">
              <p class="pe-gate-eyebrow">Acceso restringido</p>
              <h1 class="pe-gate-title">{config.APP_TITLE}</h1>
              <p class="pe-gate-sub">{config.APP_SUBTITLE}</p>
              <p class="pe-gate-text">
                Esta plataforma contiene datos académicos individualizados.
                Ingresa con tu cuenta institucional de Google para continuar.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if mensaje_error:
            st.error(mensaje_error)
            if detalle:
                st.caption(detalle)
            return

        if st.button("Continuar con Google", type="primary", width="stretch"):
            st.login()  # proveedor por defecto definido en [auth]

        acc = _acceso()
        dominios = acc.get("dominios_permitidos", [])
        if dominios:
            st.caption("Cuentas habilitadas: " + ", ".join("@" + d for d in dominios))


# --------------------------------------------------------------------------
# API pública
# --------------------------------------------------------------------------
def exigir_login() -> dict:
    """
    Bloquea la app hasta que haya una sesión de Google válida y autorizada.
    Devuelve un dict con los datos del usuario.
    """
    acc = _acceso()

    # Escape controlado para desarrollo local sin credenciales OAuth.
    if acc.get("permitir_sin_login", False):
        return {"email": "local@desarrollo", "name": "Modo desarrollo", "rol": "Administrador"}

    if not _soporta_login():
        _portada(
            "Esta versión de Streamlit no soporta inicio de sesión.",
            "Actualiza a Streamlit 1.42 o superior: pip install -U 'streamlit>=1.42' authlib",
        )
        st.stop()

    if not _auth_configurado():
        # Permite revisar la aplicación sin bloquear el desarrollo.
        # No cargues datos personales reales mientras no configures OAuth.
        st.warning("Modo de demostración sin autenticación. Configura Google OAuth antes de usar datos institucionales reales.")
        return {"email": "demo@local", "name": "Modo demostración", "rol": "Administrador"}

    if not st.user.is_logged_in:
        _portada()
        st.stop()

    email = (st.user.email or "").lower()

    if not autorizado(email):
        _portada(
            f"La cuenta {email} no tiene acceso a esta plataforma.",
            "Solicita autorización al administrador del sistema.",
        )
        if st.button("Cerrar sesión e intentar con otra cuenta"):
            st.logout()
        st.stop()

    return {
        "email": email,
        "name": st.user.name or email,
        "picture": getattr(st.user, "picture", None),
        "rol": rol_de(email),
    }


def sincronizar_sesion(usuario: dict):
    """
    Sincroniza la sesión con la identidad recién autenticada.

    Si el correo cambia respecto de la sesión anterior en este navegador,
    se limpian los datos cargados: nadie hereda los datos académicos de otro.
    """
    anterior = st.session_state.get("_usuario_email")
    if anterior != usuario["email"]:
        for clave in CLAVES_DATOS:
            st.session_state[clave] = None
        st.session_state["meta"] = config.META_INSTITUCIONAL_DEFAULT
        st.session_state["_usuario_email"] = usuario["email"]
    st.session_state["_usuario"] = usuario


def barra_usuario(usuario: dict):
    """Tarjeta de identidad + cerrar sesión en la barra lateral."""
    st.sidebar.markdown(
        f"""
        <div class="pe-user">
          <span class="pe-user-rol">{usuario['rol']}</span>
          <span class="pe-user-name">{usuario['name']}</span>
          <span class="pe-user-mail">{usuario['email']}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if usuario["email"] == "local@desarrollo":
        st.sidebar.caption("Sesión local sin autenticación")
        return
    if st.sidebar.button("Cerrar sesión", width="stretch"):
        st.logout()
