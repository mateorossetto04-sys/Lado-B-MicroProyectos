"""Lógica del brief que no depende de la UI: validación, modo respaldo y conteo de ediciones."""
import json
import re
import unicodedata

from pydantic import BaseModel, Field

from ladob.config import MIN_CARACTERES, MIN_PALABRAS


class BriefSchema(BaseModel):
    """Esquema de salida estructurada que se le pide a Gemini."""

    categoria: str = Field(description="Categoría del microproyecto, ej. Auditoría de Marketing Digital. Vacío si hay aviso.")
    tareas: list[str] = Field(description="Tareas concretas desglosadas, solo las que se desprenden del texto.")
    skills: list[str] = Field(description="Skills requeridas, solo las que se desprenden del texto.")
    duracion: str = Field(description="Duración estimada, ej. 1 semana. Vacío si hay aviso.")
    aviso: str = Field(description="Vacío si el pedido es suficiente. Si es muy corto, vago o no es de marketing, un mensaje pidiendo más detalle.")


class BriefError(ValueError):
    """El JSON del brief es inválido."""


def _limpiar_lista(valor) -> list[str]:
    if not isinstance(valor, list):
        raise BriefError("Se esperaba una lista.")
    salida = []
    for item in valor:
        texto = str(item).strip()
        if texto and texto not in salida:
            salida.append(texto)
    return salida


def parse_brief(raw) -> dict:
    """Valida un brief (str JSON o dict) y lo normaliza. Lanza BriefError si no sirve."""
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError as e:
            raise BriefError(f"JSON inválido: {e}") from e
    if not isinstance(raw, dict):
        raise BriefError("El brief debe ser un objeto JSON.")
    faltan = [k for k in ("categoria", "tareas", "skills", "duracion") if k not in raw]
    if faltan:
        raise BriefError(f"Faltan campos: {', '.join(faltan)}")
    brief = {
        "categoria": str(raw["categoria"]).strip(),
        "tareas": _limpiar_lista(raw["tareas"]),
        "skills": _limpiar_lista(raw["skills"]),
        "duracion": str(raw["duracion"]).strip(),
        "aviso": str(raw.get("aviso", "") or "").strip(),
    }
    if not brief["aviso"] and not (brief["categoria"] and brief["tareas"]):
        raise BriefError("Brief sin categoría o sin tareas.")
    return brief


def texto_insuficiente(texto: str) -> bool:
    texto = (texto or "").strip()
    return len(texto) < MIN_CARACTERES or len(texto.split()) < MIN_PALABRAS


AVISO_CORTO = (
    "Necesitamos un poco más de detalle para armar el brief. "
    "Contanos qué querés lograr, sobre qué canal o herramienta y, si podés, en cuánto tiempo."
)

# (palabras clave, categoría, tareas, skills, duración)
_REGLAS = [
    (("meta ads", "facebook ads", "instagram ads", "google ads", "campaña", "campanas", "pauta", "publicidad", "ads", "sem"),
     "Auditoría y optimización de campañas pagas",
     ["Revisar el rendimiento de las campañas del período indicado", "Identificar oportunidades de mejora", "Entregar un resumen con recomendaciones"],
     ["Publicidad digital", "Análisis de métricas"], "1 semana"),
    (("instagram", "tiktok", "redes", "contenido", "posteo", "post", "community", "linkedin", "reels"),
     "Contenido y redes sociales",
     ["Definir líneas de contenido", "Crear las piezas necesarias", "Armar un calendario de publicación"],
     ["Redes sociales", "Redacción", "Diseño básico"], "2 semanas"),
    (("seo", "posicionamiento", "google", "web", "sitio", "landing", "blog"),
     "SEO y presencia web",
     ["Analizar la situación actual del sitio", "Proponer mejoras priorizadas", "Documentar los hallazgos"],
     ["SEO", "Analítica web"], "1 semana"),
    (("mail", "email", "newsletter", "mailing"),
     "Email marketing",
     ["Revisar o diseñar las comunicaciones", "Armar una propuesta de envíos", "Medir resultados"],
     ["Email marketing", "Redacción"], "1 semana"),
    (("marca", "branding", "logo", "identidad", "posicionamiento de marca"),
     "Branding e identidad de marca",
     ["Relevar la identidad actual", "Proponer lineamientos de mejora"],
     ["Branding", "Pensamiento estratégico"], "2 semanas"),
    (("investigacion", "encuesta", "competencia", "mercado", "benchmark", "estudio"),
     "Investigación de mercado",
     ["Relevar información del mercado o la competencia", "Sintetizar hallazgos en un informe"],
     ["Investigación de mercado", "Análisis de datos"], "1 semana"),
]


def _norm(texto: str) -> str:
    t = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


def fallback_brief(texto: str) -> dict:
    """Brief simple por reglas (palabras clave → categoría y skills). No inventa más que eso."""
    if texto_insuficiente(texto):
        return {"categoria": "", "tareas": [], "skills": [], "duracion": "", "aviso": AVISO_CORTO}
    t = _norm(texto)
    palabras = set(re.findall(r"[a-z0-9]+", t))
    for claves, categoria, tareas, skills, duracion in _REGLAS:
        if any((c in t) if " " in c else (c in palabras) for c in map(_norm, claves)):
            return {"categoria": categoria, "tareas": list(tareas), "skills": list(skills), "duracion": duracion, "aviso": ""}
    return {
        "categoria": "Marketing general",
        "tareas": ["Entender el pedido en detalle", "Resolver lo que describe la empresa", "Entregar un resultado documentado"],
        "skills": ["Marketing digital"],
        "duracion": "1 semana",
        "aviso": "",
    }


def _items(lista: list[str]) -> list[str]:
    return [i.strip() for i in lista if i.strip()]


def count_edits(original: dict, final: dict) -> dict:
    """Compara el brief de la IA con el final. Devuelve {'campos': [...], 'cantidad': n}."""
    campos, total = [], 0
    for campo in ("categoria", "duracion"):
        if (original.get(campo) or "").strip() != (final.get(campo) or "").strip():
            campos.append(campo)
            total += 1
    for campo in ("tareas", "skills"):
        o, f = _items(original.get(campo, [])), _items(final.get(campo, []))
        quitados = [x for x in o if x not in f]
        agregados = [x for x in f if x not in o]
        cambios = max(len(quitados), len(agregados))  # reemplazar un ítem cuenta como 1 cambio
        if cambios:
            campos.append(campo)
            total += cambios
    return {"campos": campos, "cantidad": total}
