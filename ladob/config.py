"""Configuración central. Todo se lee de st.secrets (o variables de entorno) y nunca se hardcodea."""
import os

# Si Google discontinúa este modelo, cambialo acá o con GEMINI_MODEL en secrets.toml.
DEFAULT_GEMINI_MODEL = "gemini-3.1-flash-lite"

SHEET_WORKSHEET = "sesiones"
MIN_PALABRAS = 3
MIN_CARACTERES = 15
MAX_CARACTERES = 2000
REINTENTO_SEGUNDOS = 3
TIMEOUT_MS = 25000  # si Gemini no responde en 25 s, se usa el modo respaldo


def get_setting(name: str, default: str = "") -> str:
    """Busca primero en st.secrets y después en variables de entorno."""
    try:
        import streamlit as st

        if name in st.secrets:
            return str(st.secrets[name])
    except Exception:  # sin secrets.toml, st.secrets lanza excepción
        pass
    return os.environ.get(name, default)


def get_gcp_credentials() -> dict | None:
    """Credenciales de la cuenta de servicio (sección [gcp_service_account])."""
    try:
        import streamlit as st

        if "gcp_service_account" in st.secrets:
            return dict(st.secrets["gcp_service_account"])
    except Exception:
        pass
    return None

