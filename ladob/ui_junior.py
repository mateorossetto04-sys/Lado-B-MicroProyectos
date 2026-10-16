"""Vista del junior: ver microproyectos publicados → elegir uno → postularse → feedback."""
import time
import uuid
from datetime import datetime

import streamlit as st

from ladob import estilos
from ladob.config import get_gcp_credentials, get_setting
from ladob.proyectos import lista_proyectos
from ladob.sheets import COLUMNAS_JUNIOR, HOJA_JUNIOR, HOJA_PROYECTOS, RowLogger, leer_filas

NIVELES = ["Estudiante", "Recién graduado/a", "Con algo de experiencia"]
HORAS = ["Menos de 5 h", "5 a 10 h", "10 a 20 h", "Más de 20 h"]


@st.cache_data(ttl=30, show_spinner=False)
def _proyectos_cacheados(_creds, sheet_id: str) -> list[dict]:
    return lista_proyectos(leer_filas(_creds, sheet_id, HOJA_PROYECTOS))


def cargar_proyectos() -> list[dict]:
    creds, sheet_id = get_gcp_credentials(), get_setting("GOOGLE_SHEET_ID")
    if creds and sheet_id:
        return _proyectos_cacheados(creds, sheet_id)  # cache para no pasarnos de la cuota de lectura
    return lista_proyectos(leer_filas(None, "", HOJA_PROYECTOS))


def _init() -> None:
    ss = st.session_state
    if "j_sid" in ss:
        return
    ss.j_sid = str(uuid.uuid4())
    ss.j_t0 = time.time()
    ss.j_logger = RowLogger(get_gcp_credentials(), get_setting("GOOGLE_SHEET_ID"), HOJA_JUNIOR, COLUMNAS_JUNIOR)
    ss.j_datos = {"id_sesion": ss.j_sid, "fecha_hora": datetime.now().isoformat(timespec="seconds"),
                  "proyectos_vistos": 0, "estado": "exploró"}
    ss.j_sel = None
    ss.j_postulado = False
    ss.j_feedback = False
    ss.j_vistos = set()


def _registrar(**campos) -> None:
    ss = st.session_state
    ss.j_datos.update(campos)
    ss.j_logger.guardar(ss.j_datos)  # si falla queda en logs; el usuario no ve nada


def _ver(proyecto: dict) -> None:
    ss = st.session_state
    ss.j_sel = proyecto
    ss.j_vistos.add(proyecto["id_proyecto"])
    _registrar(proyectos_vistos=len(ss.j_vistos), proyecto_id=proyecto["id_proyecto"], proyecto_categoria=proyecto["categoria"],
               proyecto_es_ejemplo="sí" if proyecto["es_ejemplo"] else "no", estado="vio proyecto")


def _volver() -> None:
    st.session_state.j_sel = None


def _chips(items: list[str]) -> None:
    st.markdown("".join(f'<span class="chip">{s}</span>' for s in items), unsafe_allow_html=True)


def _tarjeta(p: dict) -> None:
    with st.container(key=f"card_{p['id_proyecto']}"):
        etiqueta = '<span class="etiqueta">EJEMPLO</span>' if p["es_ejemplo"] else ""
        st.markdown(
            f'<div class="card-top"><div class="card-icono">{estilos.icono(p["categoria"])}</div>'
            f'<div class="card-titulo">{p["categoria"]}{etiqueta}</div></div>'
            f'<div class="meta">⏱️ {p["duracion"] or "A definir"} &nbsp;·&nbsp; 📝 {len(p["tareas"])} tareas</div>',
            unsafe_allow_html=True,
        )
        _chips(p["skills"])
        st.button("Ver proyecto", key=f"ver_{p['id_proyecto']}", on_click=_ver, args=(p,), use_container_width=True)


def _detalle(p: dict) -> None:
    ss = st.session_state
    if not ss.j_postulado:
        st.button("← Volver a los proyectos", on_click=_volver)
    st.subheader(p["categoria"])
    if p["es_ejemplo"]:
        st.caption("Proyecto de ejemplo del prototipo.")
    st.markdown(f"**Duración estimada:** {p['duracion'] or 'A definir'}")
    st.markdown("**Qué vas a hacer**\n" + "\n".join(f"{n}. {t}" for n, t in enumerate(p["tareas"], 1)))
    if p["skills"]:
        st.markdown("**Skills que se buscan**")
        _chips(p["skills"])
    st.info("🏅 Al terminarlo, el resultado queda como evidencia verificable en tu perfil.")

    if ss.j_postulado:
        return
    st.markdown("### Postulate")
    with st.form("postulacion"):
        motivo = st.text_area("¿Por qué podés resolver este proyecto?", height=110, key="j_motivo",
                              placeholder="Contanos brevemente tu experiencia, cursos o cómo lo encararías.")
        skills = st.multiselect("¿Cuáles de estas skills ya tenés?", p["skills"], key="j_skills")
        nivel = st.radio("¿En qué momento estás?", NIVELES, index=None, key="j_nivel")
        horas = st.select_slider("¿Cuántas horas por semana podés dedicarle?", HORAS, value=HORAS[1], key="j_horas")
        alias = st.text_input("¿Cómo te llamamos? (opcional, no pedimos email)", key="j_alias")
        if st.form_submit_button("Postularme", type="primary", use_container_width=True):
            if len(motivo.strip()) < 10 or nivel is None:
                st.error("Contanos un poco por qué y en qué momento estás para postularte.")
            else:
                ss.j_postulado = True
                _registrar(estado="postuló", segundos_hasta_postular=int(time.time() - ss.j_t0), alias=alias.strip(),
                           nivel=nivel, horas_semana=horas, skills_que_tiene=skills, motivacion=motivo.strip())
                st.rerun()


def _feedback() -> None:
    ss = st.session_state
    if not ss.j_feedback:
        estilos.confeti()
    st.success("✅ ¡Listo! Tu postulación quedó registrada. En la versión completa, la empresa la vería junto a las demás.")
    if ss.j_feedback:
        st.success("¡Gracias por tu devolución! 💙")
        return
    st.subheader("Una última cosa")
    with st.form("feedback_junior"):
        atractivo = st.radio("¿Qué tan atractivo te pareció este microproyecto? (1 = nada, 5 = mucho)", [1, 2, 3, 4, 5],
                             index=None, horizontal=True, key="j_atractivo")
        real = st.radio("¿Te postularías a uno así en la vida real?", ["Sí", "Tal vez", "No"], index=None, horizontal=True, key="j_real")
        comentario = st.text_area("Comentario (opcional)", height=80, key="j_comentario")
        if st.form_submit_button("Enviar", type="primary", use_container_width=True):
            if atractivo is None or real is None:
                st.error("Respondé las dos preguntas para enviar.")
            else:
                _registrar(atractivo=atractivo, postularia_real=real, comentario=comentario.strip())
                ss.j_feedback = True
                st.rerun()


def vista_junior() -> None:
    _init()
    ss = st.session_state
    st.markdown(
        '<div class="bienvenida">Acá no competís por un puesto: <b>resolvés problemas concretos</b> que publican empresas reales, '
        "en proyectos cortos, y el resultado queda como evidencia en tu perfil. Elegí uno y postulate.</div>",
        unsafe_allow_html=True,
    )
    paso = 0 if ss.j_sel is None else (2 if ss.j_postulado else 1)
    estilos.pasos(["Explorá", "Elegí", "Postulate"], paso)
    if ss.j_sel is None:
        st.subheader("Microproyectos disponibles")
        for p in cargar_proyectos():
            _tarjeta(p)
    else:
        _detalle(ss.j_sel)
        if ss.j_postulado:
            _feedback()
    st.markdown('<div class="nota">🔒 Guardamos tus respuestas de forma anónima para mejorar el prototipo.</div>', unsafe_allow_html=True)


