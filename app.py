"""Lado B Microproyectos — prototipo del lado empresa (texto libre → brief editable → confirmación)."""
import json
import logging
import time
import uuid
from datetime import datetime

import streamlit as st
import streamlit.components.v1 as components

from ladob.ai import generar_brief
from ladob.brief import count_edits
from ladob import estilos
from ladob.config import DEFAULT_GEMINI_MODEL, MAX_CARACTERES, get_gcp_credentials, get_setting
from ladob.proyectos import a_fila_proyecto
from ladob.sheets import COLUMNAS_PROYECTOS, HOJA_PROYECTOS, RowLogger
from ladob.ui_junior import vista_junior

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("ladob.app")

EJEMPLO = "Necesito revisar las campañas de Meta Ads del último mes"
PLACEHOLDER = "Ej: Necesito revisar las campañas de Meta Ads del último mes y saber qué podemos mejorar."

st.set_page_config(page_title="Lado B Microproyectos", page_icon="🅱️", layout="centered")

estilos.aplicar()


# ---------- Clarity ----------
def inyectar_clarity() -> None:
    """Inserta el script de Microsoft Clarity en la página (no en el iframe del componente)."""
    clarity_id = get_setting("CLARITY_PROJECT_ID").strip()
    if not clarity_id or not clarity_id.replace("-", "").replace("_", "").isalnum():
        return
    components.html(
        f"""<script>
        (function() {{
          var doc = window.parent.document;
          if (doc.getElementById('clarity-script')) return;
          var s = doc.createElement('script');
          s.id = 'clarity-script';
          s.text = '(function(c,l,a,r,i,t,y){{c[a]=c[a]||function(){{(c[a].q=c[a].q||[]).push(arguments)}};' +
                   't=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;' +
                   'y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);}})' +
                   '(window,document,"clarity","script","{clarity_id}");';
          doc.head.appendChild(s);
        }})();
        </script>""",
        height=0,
    )


# ---------- Estado de sesión ----------
def init_state() -> None:
    ss = st.session_state
    if "sid" in ss:
        return
    ss.sid = str(uuid.uuid4())
    ss.t0 = time.time()
    ss.inicio = datetime.now().isoformat(timespec="seconds")
    ss.etapa = "texto"  # texto -> brief -> confirmado
    creds, sheet_id = get_gcp_credentials(), get_setting("GOOGLE_SHEET_ID")
    ss.logger = RowLogger(creds, sheet_id)
    ss.proy_logger = RowLogger(creds, sheet_id, HOJA_PROYECTOS, COLUMNAS_PROYECTOS, "id_proyecto")
    ss.sesion = {"id_sesion": ss.sid, "fecha_hora": ss.inicio, "estado": "abandonó", "uso_respaldo": "no"}
    ss.contador = 0
    ss.ia_brief = None
    ss.final = None
    ss.error_registro = False


def registrar(**campos) -> None:
    ss = st.session_state
    ss.sesion.update(campos)
    if not ss.logger.guardar(ss.sesion):
        ss.error_registro = True  # solo a logs; el usuario no ve nada


def nuevo_item(texto: str = "") -> dict:
    st.session_state.contador += 1
    return {"id": st.session_state.contador, "text": texto}


def cargar_ejemplo() -> None:
    st.session_state["texto"] = EJEMPLO


def borrar_item(lista: str, item_id: int) -> None:
    st.session_state.edicion[lista] = [i for i in st.session_state.edicion[lista] if i["id"] != item_id]


def agregar_item(lista: str) -> None:
    st.session_state.edicion[lista].append(nuevo_item())


# ---------- Acciones ----------
def accion_generar(texto: str) -> None:
    ss = st.session_state
    registrar(texto_original=texto, estado="abandonó")  # fila creada; avanza si sigue
    modelo = get_setting("GEMINI_MODEL", DEFAULT_GEMINI_MODEL)
    with st.spinner("Armando tu brief…"):
        res = generar_brief(texto, get_setting("GEMINI_API_KEY"), modelo)
    ss.mensaje_ia = res.mensaje
    ss.uso_respaldo = res.uso_respaldo
    b = res.brief
    if b["aviso"]:
        ss.etapa = "texto"
        ss.aviso = b["aviso"]
        return
    ss.aviso = ""
    ss.ia_brief = {k: b[k] for k in ("categoria", "tareas", "skills", "duracion")}
    ss.edicion = {
        "categoria": b["categoria"],
        "duracion": b["duracion"],
        "tareas": [nuevo_item(t) for t in b["tareas"]],
        "skills": [nuevo_item(s) for s in b["skills"]],
    }
    for k in [k for k in ss if k.startswith(("w_cat", "w_dur", "w_tareas_", "w_skills_"))]:
        del ss[k]  # limpia widgets de un brief anterior
    ss.etapa = "brief"
    registrar(brief_ia=ss.ia_brief, estado="generó brief", uso_respaldo="sí" if res.uso_respaldo else "no")


def brief_desde_edicion() -> dict:
    ss = st.session_state
    return {
        "categoria": ss.get("w_cat", ss.edicion["categoria"]).strip(),
        "duracion": ss.get("w_dur", ss.edicion["duracion"]).strip(),
        "tareas": [t.strip() for t in (ss.get(f"w_tareas_{i['id']}", i["text"]) for i in ss.edicion["tareas"]) if t.strip()],
        "skills": [s.strip() for s in (ss.get(f"w_skills_{i['id']}", i["text"]) for i in ss.edicion["skills"]) if s.strip()],
    }


def accion_confirmar() -> None:
    ss = st.session_state
    final = brief_desde_edicion()
    if not final["categoria"] or not final["tareas"]:
        ss.error_confirmar = "Para confirmar, el brief necesita una categoría y al menos una tarea."
        return
    ss.error_confirmar = ""
    ss.final = final
    ss.etapa = "confirmado"
    registrar(
        brief_final=final,
        campos_editados=count_edits(ss.ia_brief, final),
        estado="confirmó",
        segundos_hasta_confirmar=int(time.time() - ss.t0),
    )
    # lo que la empresa confirma queda disponible para los juniors
    ss.proy_logger.guardar(a_fila_proyecto(ss.sid, datetime.now().isoformat(timespec="seconds"), final))


# ---------- UI ----------
def lista_editable(clave: str, titulo: str, etiqueta_agregar: str) -> None:
    st.markdown(f"**{titulo}**")
    for item in st.session_state.edicion[clave]:
        c1, c2 = st.columns([8, 1])
        c1.text_input(titulo, value=item["text"], key=f"w_{clave}_{item['id']}", label_visibility="collapsed")
        c2.button("🗑️", key=f"del_{clave}_{item['id']}", help="Borrar", on_click=borrar_item, args=(clave, item["id"]))
    st.button(f"➕ {etiqueta_agregar}", key=f"add_{clave}", on_click=agregar_item, args=(clave,))


def vista_brief_final(b: dict) -> None:
    st.markdown(f"**Categoría:** {b['categoria']}")
    st.markdown(f"**Duración estimada:** {b['duracion'] or 'A definir'}")
    st.markdown("**Tareas**\n" + "\n".join(f"{n}. {t}" for n, t in enumerate(b["tareas"], 1)))
    if b["skills"]:
        st.markdown("**Skills requeridas**")
        st.markdown("".join(f'<span class="chip">{s}</span>' for s in b["skills"]), unsafe_allow_html=True)


def vista_empresa() -> None:
    ss = st.session_state
    st.markdown(
        '<div class="bienvenida">Lado B conecta a juniors de marketing con microproyectos reales de pymes, startups y agencias. '
        "<b>Contanos qué necesitás como se lo contarías a un colega</b> y te armamos un brief que podés revisar y ajustar.</div>",
        unsafe_allow_html=True,
    )
    pasos_ph = st.empty()  # se completa al final, cuando ya se sabe en qué paso está

    # --- Paso 1: texto libre ---
    if ss.etapa != "confirmado":
        st.subheader("1. Contanos qué necesitás")
        texto = st.text_area("Tu necesidad", key="texto", placeholder=PLACEHOLDER, height=130,
                             max_chars=MAX_CARACTERES, label_visibility="collapsed")
        b1, b2 = st.columns([3, 2])
        with b2:
            st.button("Usar ejemplo", on_click=cargar_ejemplo, use_container_width=True)
        with b1:
            generar = st.button("Armar mi brief", type="primary", use_container_width=True)
        st.markdown('<div class="nota">🔒 Guardamos tu texto y tus respuestas de forma anónima para mejorar el prototipo.</div>',
                    unsafe_allow_html=True)
        if generar:
            accion_generar(texto.strip())
        if ss.get("aviso"):
            st.warning(ss.aviso)

    # --- Paso 2: brief editable ---
    if ss.etapa == "brief":
        st.divider()
        st.subheader("2. Revisá y ajustá tu brief")
        st.info("Esta es **una propuesta que podés editar**: cambiá lo que no te cierre, borrá o agregá lo que haga falta.")
        if ss.get("mensaje_ia"):
            st.warning(ss.mensaje_ia)
        st.text_input("Categoría", value=ss.edicion["categoria"], key="w_cat")
        st.text_input("Duración estimada", value=ss.edicion["duracion"], key="w_dur")
        lista_editable("tareas", "Tareas", "Agregar tarea")
        lista_editable("skills", "Skills requeridas", "Agregar skill")
        if ss.get("error_confirmar"):
            st.error(ss.error_confirmar)
        st.button("Confirmar y publicar microproyecto", type="primary", use_container_width=True, on_click=accion_confirmar)

    # --- Paso 3: confirmación y feedback ---
    if ss.etapa == "confirmado":
        if not ss.get("feedback_enviado"):
            estilos.confeti()
        st.success("🎉 ¡Listo! Tu microproyecto quedó confirmado y listo para publicarse.")
        with st.container(key="final"):
            vista_brief_final(ss.final)
        st.divider()
        if ss.get("feedback_enviado"):
            st.success("¡Gracias por tu devolución! Nos ayuda un montón. 💙")
        else:
            st.subheader("Una última cosa")
            with st.form("feedback"):
                precision = st.radio("¿Qué tan preciso te pareció el brief? (1 = nada, 5 = muy preciso)",
                                     [1, 2, 3, 4, 5], index=None, horizontal=True)
                publicaria = st.radio("¿Lo publicarías así?", ["Sí", "Con cambios", "No"], index=None, horizontal=True)
                comentario = st.text_area("Comentario (opcional)", height=80)
                if st.form_submit_button("Enviar", type="primary", use_container_width=True):
                    if precision is None or publicaria is None:
                        st.error("Respondé las dos preguntas para enviar.")
                    else:
                        registrar(precision_percibida=precision, publicaria=publicaria, comentario=comentario.strip())
                        ss.feedback_enviado = True
                        st.rerun()

    with pasos_ph:
        estilos.pasos(["Contá", "Revisá", "Confirmá"], {"texto": 0, "brief": 1, "confirmado": 2}[ss.etapa])

    if ss.logger.modo == "simulado":
        st.caption("Modo de prueba: los registros se guardan localmente (Google Sheets no está configurado).")


def main() -> None:
    init_state()
    inyectar_clarity()
    estilos.hero()
    # Link para juniors: ?rol=junior abre directo esa pestaña (queda primera).
    junior_primero = st.query_params.get("rol", "") == "junior"
    nombres = ["🎓 Soy junior", "🏢 Soy empresa"] if junior_primero else ["🏢 Soy empresa", "🎓 Soy junior"]
    tabs = dict(zip(nombres, st.tabs(nombres)))
    with tabs["🏢 Soy empresa"]:
        vista_empresa()
    with tabs["🎓 Soy junior"]:
        vista_junior()


main()

