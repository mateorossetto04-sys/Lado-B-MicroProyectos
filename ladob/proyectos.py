"""Proyectos que ve el junior: ejemplos fijos + los briefs que las empresas confirmaron."""
import json

from ladob.brief import parse_brief

EJEMPLOS = [
    {"id_proyecto": "ejemplo-1", "es_ejemplo": True, "categoria": "Auditoría de campañas pagas", "duracion": "1 semana",
     "tareas": ["Revisar las campañas de Meta Ads del último mes", "Identificar qué anuncios rinden peor", "Entregar un resumen con 3 recomendaciones"],
     "skills": ["Meta Ads", "Análisis de métricas"]},
    {"id_proyecto": "ejemplo-2", "es_ejemplo": True, "categoria": "Contenido para redes sociales", "duracion": "2 semanas",
     "tareas": ["Proponer 12 ideas de posteos para Instagram", "Redactar los textos de 6 piezas", "Armar un calendario de publicación"],
     "skills": ["Redes sociales", "Redacción"]},
    {"id_proyecto": "ejemplo-3", "es_ejemplo": True, "categoria": "Investigación de competencia", "duracion": "1 semana",
     "tareas": ["Relevar 5 competidores directos", "Comparar precios y propuesta de valor", "Sintetizar hallazgos en un informe corto"],
     "skills": ["Investigación de mercado", "Análisis de datos"]},
]


def proyecto_desde_fila(f: dict) -> dict | None:
    """Convierte una fila de la pestaña `proyectos` en proyecto; ignora filas rotas."""
    try:
        b = parse_brief(f["brief_final"])
        return {"id_proyecto": str(f["id_proyecto"]), "es_ejemplo": False, **{k: b[k] for k in ("categoria", "duracion", "tareas", "skills")}}
    except Exception:  # noqa: BLE001
        return None


def lista_proyectos(filas_publicadas: list[dict]) -> list[dict]:
    """Primero los publicados por empresas (más nuevos arriba), después los ejemplos."""
    reales = [p for p in map(proyecto_desde_fila, filas_publicadas) if p]
    return list(reversed(reales)) + EJEMPLOS


def a_fila_proyecto(id_proyecto: str, fecha: str, brief: dict) -> dict:
    return {"id_proyecto": id_proyecto, "fecha_hora": fecha, "categoria": brief["categoria"],
            "duracion": brief["duracion"], "brief_final": json.dumps(brief, ensure_ascii=False)}
