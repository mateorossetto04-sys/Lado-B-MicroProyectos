"""Identidad visual de Lado B: violeta, amarillo y blanco. CSS puro, sin dependencias de pago."""
import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700;800&family=Inter:wght@400;500;600&display=swap');

:root {
  --v900:#2E1065; --v700:#5B21B6; --v600:#6D28D9; --v500:#7C3AED; --v200:#DDD6FE; --v100:#EDE9FE; --v50:#F5F3FF;
  --y500:#FACC15; --y400:#FDE047; --y100:#FEF9C3; --ink:#1E1B4B; --muted:#6B6890;
  --sombra: 0 10px 30px -12px rgba(91,33,182,.35);
}
html, body, [class*="css"], .stApp { font-family: 'Inter', system-ui, sans-serif; color: var(--ink); }
.stApp { background: linear-gradient(180deg, var(--v50) 0%, #fff 340px); }
#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; height: 0; }
.block-container { padding-top: 1.2rem !important; padding-bottom: 3rem; max-width: 760px; }
h1, h2, h3 { font-family: 'Poppins', sans-serif !important; color: var(--v900); letter-spacing: -.01em; }
h3 { font-size: 1.15rem !important; }

/* ---------- Animaciones ---------- */
@keyframes subir   { from {opacity:0; transform:translateY(14px);} to {opacity:1; transform:none;} }
@keyframes flotar  { 0%,100% {transform:translateY(0) rotate(-4deg);} 50% {transform:translateY(-6px) rotate(4deg);} }
@keyframes brillo  { 0% {background-position:0% 50%;} 100% {background-position:200% 50%;} }
@keyframes caer    { 0% {transform:translateY(-10vh) rotate(0); opacity:1;} 100% {transform:translateY(105vh) rotate(720deg); opacity:0;} }
@keyframes pulso   { 0%,100% {box-shadow:0 0 0 0 rgba(250,204,21,.6);} 50% {box-shadow:0 0 0 8px rgba(250,204,21,0);} }
.stApp [data-testid="stMainBlockContainer"] > div { animation: subir .5s ease both; }
@media (prefers-reduced-motion: reduce) { * { animation: none !important; transition: none !important; } }

/* ---------- Hero ---------- */
.hero { position:relative; overflow:hidden; display:flex; align-items:center; gap:1rem; padding:1.5rem 1.4rem;
  border-radius:24px; color:#fff; margin-bottom:1.1rem; box-shadow: var(--sombra);
  background: linear-gradient(120deg, var(--v900), var(--v600) 55%, var(--v500)); }
.hero .logo { flex:none; width:58px; height:58px; border-radius:16px; background:var(--y500); color:var(--v900);
  display:grid; place-items:center; font:800 1.9rem 'Poppins',sans-serif; animation: flotar 4s ease-in-out infinite; }
.hero .titulo { font:800 1.55rem/1.1 'Poppins',sans-serif; margin:0; }
.hero .titulo span { color:var(--y400); }
.hero .sub { margin:.35rem 0 0; color:#E9E3FF; font-size:.95rem; line-height:1.4; }
.hero .blob { position:absolute; border-radius:50%; opacity:.22; pointer-events:none; }
.hero .b1 { width:170px; height:170px; right:-40px; top:-60px; background:var(--y500); }
.hero .b2 { width:90px; height:90px; right:90px; bottom:-45px; background:#fff; }

/* ---------- Pestañas ---------- */
[role="tablist"] { gap:.4rem; background:var(--v100); padding:.3rem; border-radius:999px; }
.react-aria-SelectionIndicator, [data-baseweb="tab-highlight"], [data-baseweb="tab-border"] { display:none !important; }
[role="tab"] { flex:1; display:flex; justify-content:center; align-items:center; cursor:pointer; border-radius:999px; height:2.6rem; padding:0 1rem; transition: all .2s ease;
  font:600 .95rem 'Poppins',sans-serif; color:var(--v700); background:transparent; }
[role="tab"]:hover { background:rgba(255,255,255,.7); }
[role="tab"][aria-selected="true"] { background:var(--v600); color:#fff; box-shadow:0 6px 16px -6px rgba(109,40,217,.6); }
[role="tab"][aria-selected="true"] p { color:#fff; }
[role="tabpanel"] { padding-top:1rem; }

/* ---------- Bienvenida y notas ---------- */
.bienvenida { background:#fff; border:1px solid var(--v200); border-left:6px solid var(--y500); border-radius:16px;
  padding:1rem 1.1rem; color:var(--ink); font-size:1rem; line-height:1.55; margin-bottom:1.2rem; box-shadow:0 4px 14px -8px rgba(91,33,182,.25); }
.nota { color:var(--muted); font-size:.82rem; margin-top:.6rem; }

/* ---------- Pasos ---------- */
.pasos { display:flex; align-items:center; margin:.2rem 0 1.3rem; }
.paso { display:flex; align-items:center; gap:.45rem; font:600 .85rem 'Poppins',sans-serif; color:var(--muted); }
.paso .n { width:28px; height:28px; border-radius:50%; display:grid; place-items:center; background:var(--v100); color:var(--v700); transition:all .3s; }
.paso.activo { color:var(--v900); }
.paso.activo .n { background:var(--v600); color:#fff; animation:pulso 2s infinite; }
.paso.hecho .n { background:var(--y500); color:var(--v900); }
.linea { flex:1; height:3px; margin:0 .5rem; background:var(--v200); border-radius:3px; min-width:12px; }
.linea.hecha { background:var(--y500); }
@media (max-width:480px) { .paso .t { display:none; } .paso.activo .t { display:inline; } }

/* ---------- Tarjetas ---------- */
[class*="st-key-card"] { background:#fff; border:1px solid var(--v200); border-radius:20px; padding:1.1rem 1.2rem;
  box-shadow:0 4px 14px -8px rgba(91,33,182,.3); transition: transform .2s ease, box-shadow .2s ease, border-color .2s; animation: subir .5s ease both; }
[class*="st-key-card"]:hover { transform:translateY(-4px); box-shadow:var(--sombra); border-color:var(--v500); }
.card-top { display:flex; align-items:center; gap:.7rem; margin-bottom:.2rem; }
.card-icono { flex:none; width:44px; height:44px; border-radius:14px; background:var(--y100); display:grid; place-items:center; font-size:1.4rem; }
.card-titulo { font:700 1.05rem/1.25 'Poppins',sans-serif; color:var(--v900); }
.etiqueta { display:inline-block; background:var(--y500); color:var(--v900); font:700 .68rem 'Poppins',sans-serif; padding:.12rem .55rem;
  border-radius:999px; margin-left:.4rem; vertical-align:middle; letter-spacing:.03em; }
.meta { color:var(--muted); font-size:.85rem; margin:.1rem 0 .5rem; }
.chip { display:inline-block; background:var(--v100); color:var(--v700); padding:.2rem .75rem; border-radius:999px; font:500 .85rem 'Inter',sans-serif;
  margin:.15rem .3rem .15rem 0; border:1px solid var(--v200); }

/* ---------- Botones ---------- */
.stButton > button, .stFormSubmitButton > button { border-radius:14px; font:600 .95rem 'Poppins',sans-serif; min-height:2.8rem;
  transition: transform .15s ease, box-shadow .2s ease, background .2s; border:1.5px solid var(--v200); color:var(--v700); background:#fff; }
.stButton > button:hover, .stFormSubmitButton > button:hover { transform:translateY(-2px); border-color:var(--v500); color:var(--v600); box-shadow:0 8px 18px -10px rgba(91,33,182,.5); }
.stButton > button:active, .stFormSubmitButton > button:active { transform:translateY(0) scale(.98); }
button[data-testid="stBaseButton-primary"], button[data-testid="stBaseButton-primaryFormSubmit"], button[kind="primary"], button[kind="primaryFormSubmit"] {
  background: linear-gradient(110deg, var(--v600), var(--v500), var(--v600)) !important; background-size:200% 100% !important;
  border:none !important; color:#fff !important; box-shadow:0 10px 22px -10px rgba(109,40,217,.8); }
button[data-testid="stBaseButton-primary"]:hover, button[data-testid="stBaseButton-primaryFormSubmit"]:hover, button[kind="primary"]:hover {
  animation: brillo 1.4s linear infinite; color:var(--y400) !important; }

/* ---------- Campos ---------- */
.stTextInput input, .stTextArea textarea, [data-baseweb="select"] > div { border-radius:14px !important; border:1.5px solid var(--v200) !important; background:#fff !important; transition:all .2s; }
/* Texto siempre oscuro sobre fondo claro, aunque el dispositivo esté en modo oscuro */
.stTextInput input, .stTextArea textarea, [data-baseweb="select"] * { color:var(--ink) !important; -webkit-text-fill-color:var(--ink) !important; caret-color:var(--v600); }
.stTextInput input::placeholder, .stTextArea textarea::placeholder { color:#8B87A8 !important; -webkit-text-fill-color:#8B87A8 !important; opacity:1; }
.stApp p, .stApp label, .stApp li, .stApp h1, .stApp h2, .stApp h3, .stApp [data-testid="stCaptionContainer"] { color:var(--ink); }
.stApp .hero p, .stApp .hero .titulo, .stApp .hero .sub { color:#fff; }
.stApp .hero .titulo span { color:var(--y400); }
.stApp .hero .sub { color:#E9E3FF; }
.stApp .nota, .stApp .meta { color:var(--muted); }
.stApp .paso { color:var(--muted); } .stApp .paso.activo { color:var(--v900); }
button[data-testid="stBaseButton-secondary"], button[data-testid="stBaseButton-secondaryFormSubmit"] { background:#fff !important; color:var(--v700) !important; }
button[data-testid="stBaseButton-secondary"] p { color:var(--v700) !important; }
[data-baseweb="input"], [data-baseweb="textarea"], [data-baseweb="base-input"] { background:#fff !important; border-color:var(--v200) !important; border-radius:14px !important; }
.stButton > button { border:1.5px solid var(--v200) !important; }
button[data-testid="stBaseButton-primary"] p, button[data-testid="stBaseButton-primaryFormSubmit"] p { color:inherit !important; }
[data-testid="stRadio"] label p, [data-testid="stSelectSlider"] * { color:var(--ink); }
.stTextInput input:focus, .stTextArea textarea:focus { border-color:var(--v500) !important; box-shadow:0 0 0 4px rgba(124,58,237,.15) !important; }
[data-testid="stForm"] { border:1px solid var(--v200); border-radius:20px; background:#fff; padding:1.1rem; box-shadow:0 4px 14px -8px rgba(91,33,182,.25); }
.stTextInput label, .stTextArea label, .stRadio label, .stSelectSlider label, .stMultiSelect label { font-weight:600; color:var(--v900); }
[data-baseweb="tag"] { background:var(--v100) !important; color:var(--v700) !important; border-radius:999px !important; }

/* ---------- Avisos ---------- */
[data-testid="stAlert"] { border-radius:16px; }
[data-testid="stAlertContainer"] { border-radius:16px; border:none !important; }
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentInfo"]) { background:var(--v100) !important; color:var(--v900) !important; }
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentWarning"]) { background:var(--y100) !important; color:#713F12 !important; border-left:5px solid var(--y500) !important; }
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentSuccess"]) { background:var(--v100) !important; color:var(--v900) !important; border-left:5px solid var(--y500) !important; }
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentError"]) { border-left:5px solid #E11D48 !important; }
[data-testid="stAlertContainer"] p { color:inherit !important; }
/* ---------- Brief confirmado ---------- */
[class*="st-key-final"] { background:linear-gradient(135deg,#fff,var(--v50)); border:2px solid var(--v500); border-radius:22px; padding:1.2rem 1.3rem; box-shadow:var(--sombra); }

/* ---------- Confeti ---------- */
.confeti { position:fixed; inset:0; pointer-events:none; overflow:hidden; z-index:9999; }
.confeti i { position:absolute; top:-5vh; width:10px; height:16px; border-radius:2px; animation: caer 3.2s ease-in forwards; }
.confeti i:nth-child(odd) { background:var(--y500); } .confeti i:nth-child(even) { background:var(--v500); } .confeti i:nth-child(3n) { background:#fff; border:1px solid var(--v200); }
%(confeti_pos)s

/* Mantiene input + botón de borrar en la misma fila en el celular */
[data-testid="stHorizontalBlock"] { flex-wrap:nowrap !important; align-items:center; gap:.5rem; }
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:first-child { min-width:0 !important; flex:1 1 auto !important; }
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child { min-width:0 !important; flex:0 0 auto !important; width:auto !important; }
@media (max-width:480px) { .hero { padding:1.2rem 1rem; } .hero .titulo { font-size:1.3rem; } .hero .logo { width:48px; height:48px; font-size:1.5rem; } }
</style>
"""

_POS = "\n".join(
    f".confeti i:nth-child({n}) {{ left:{(n * 37) % 100}%; animation-delay:{(n % 8) * .12:.2f}s; animation-duration:{2.6 + (n % 5) * .35:.2f}s; }}"
    for n in range(1, 31)
)

ICONOS = [
    (("campaña", "ads", "paga", "pauta"), "📣"), (("red", "contenido", "instagram", "tiktok"), "📱"),
    (("seo", "web", "sitio"), "🌐"), (("email", "mail"), "✉️"), (("marca", "brand"), "🎨"),
    (("investig", "competencia", "mercado"), "🔎"),
]


def icono(categoria: str) -> str:
    c = (categoria or "").lower()
    return next((i for claves, i in ICONOS if any(k in c for k in claves)), "🚀")


def aplicar() -> None:
    st.markdown(CSS.replace("%(confeti_pos)s", _POS), unsafe_allow_html=True)


def hero() -> None:
    st.markdown(
        '<div class="hero"><span class="blob b1"></span><span class="blob b2"></span><div class="logo">B</div>'
        '<div><p class="titulo">Lado B <span>Microproyectos</span></p>'
        '<p class="sub">Proyectos reales y cortos de marketing: las empresas los publican, los juniors los resuelven.</p></div></div>',
        unsafe_allow_html=True,
    )


def pasos(nombres: list[str], actual: int) -> None:
    """Indicador de pasos. `actual` es el índice (0-based) del paso en curso."""
    partes = []
    for i, nombre in enumerate(nombres):
        estado = "hecho" if i < actual else ("activo" if i == actual else "")
        marca = "✓" if i < actual else str(i + 1)
        partes.append(f'<div class="paso {estado}"><span class="n">{marca}</span><span class="t">{nombre}</span></div>')
        if i < len(nombres) - 1:
            partes.append(f'<div class="linea {"hecha" if i < actual else ""}"></div>')
    st.markdown(f'<div class="pasos">{"".join(partes)}</div>', unsafe_allow_html=True)


def confeti() -> None:
    st.markdown('<div class="confeti">' + "<i></i>" * 30 + "</div>", unsafe_allow_html=True)


