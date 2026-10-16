"""Registro en Google Sheets: una fila por sesión/proyecto, actualizada a medida que avanza.

Pestañas: `sesiones` (empresa), `proyectos` (briefs confirmados, los que ve el junior) y
`postulaciones` (sesiones de juniors). Si Sheets no está configurado o falla, la app sigue andando:
se escribe a archivos locales (modo simulado) y el error va a los logs.
"""
import json
import logging
import re
from datetime import datetime
from pathlib import Path

log = logging.getLogger("ladob.sheets")

COLUMNAS = [
    "id_sesion", "fecha_hora", "texto_original", "brief_ia", "brief_final", "campos_editados",
    "estado", "segundos_hasta_confirmar", "uso_respaldo", "precision_percibida",
    "publicaria", "comentario",
]
COLUMNAS_PROYECTOS = ["id_proyecto", "fecha_hora", "categoria", "duracion", "brief_final"]
COLUMNAS_JUNIOR = [
    "id_sesion", "fecha_hora", "proyectos_vistos", "proyecto_id", "proyecto_categoria", "proyecto_es_ejemplo",
    "estado", "segundos_hasta_postular", "alias", "nivel", "horas_semana", "skills_que_tiene",
    "motivacion", "atractivo", "postularia_real", "comentario",
]
HOJA_SESIONES, HOJA_PROYECTOS, HOJA_JUNIOR = "sesiones", "proyectos", "postulaciones"
LOCAL_DIR = Path(__file__).resolve().parent.parent / "logs"


def a_json(obj) -> str:
    return json.dumps(obj, ensure_ascii=False)


def fila(datos: dict, columnas: list[str] = COLUMNAS) -> list:
    """Convierte el dict en la fila de la hoja, en el orden de `columnas`."""
    valores = []
    for col in columnas:
        v = datos.get(col, "")
        valores.append(a_json(v) if isinstance(v, (dict, list)) else ("" if v is None else v))
    return valores


class RowLogger:
    """Upsert de una fila por clave (`clave`). `row` se guarda para actualizar la misma fila."""

    def __init__(self, credentials: dict | None, sheet_id: str, hoja: str = HOJA_SESIONES,
                 columnas: list[str] = COLUMNAS, clave: str = "id_sesion"):
        self.credentials, self.sheet_id = credentials, sheet_id
        self.hoja, self.columnas, self.clave = hoja, columnas, clave
        self.row: int | None = None
        self._ws = None
        self.modo = "sheets" if credentials and sheet_id else "simulado"

    def _worksheet(self):
        if self._ws is None:
            import gspread

            gc = gspread.service_account_from_dict(self.credentials)
            sh = gc.open_by_key(self.sheet_id)
            try:
                ws = sh.worksheet(self.hoja)
            except gspread.WorksheetNotFound:
                ws = sh.add_worksheet(self.hoja, rows=1000, cols=len(self.columnas))
            if ws.row_values(1) != self.columnas:
                ws.update(range_name="A1", values=[self.columnas])
            self._ws = ws
        return self._ws

    def guardar(self, datos: dict) -> bool:
        """Crea o actualiza la fila. Devuelve False si falló (nunca lanza)."""
        try:
            if self.modo == "sheets":
                self._guardar_sheets(datos)
            else:
                self._guardar_local(datos)
            return True
        except Exception as e:  # noqa: BLE001
            log.error("No se pudo registrar %s en '%s': %s: %s", datos.get(self.clave), self.hoja, type(e).__name__, e)
            return False

    def _guardar_sheets(self, datos: dict) -> None:
        ws, valores = self._worksheet(), fila(datos, self.columnas)
        if self.row is None:
            r = ws.append_row(valores, value_input_option="RAW", table_range="A1")
            rango = r["updates"]["updatedRange"]  # ej. "sesiones!A5:L5"
            self.row = int(re.search(r"[A-Z]+(\d+)", rango.split("!")[-1]).group(1))
        else:
            ws.update(range_name=f"A{self.row}", values=[valores], raw=True)

    def _guardar_local(self, datos: dict) -> None:
        LOCAL_DIR.mkdir(exist_ok=True)
        ruta = LOCAL_DIR / f"{self.hoja}.jsonl"
        filas = {d[self.clave]: d for d in _leer_local(ruta)}
        filas[datos[self.clave]] = {**datos, "guardado": datetime.now().isoformat(timespec="seconds")}
        ruta.write_text("\n".join(a_json(d) for d in filas.values()) + "\n", encoding="utf-8")


SessionLogger = RowLogger  # nombre histórico


def _leer_local(ruta: Path) -> list[dict]:
    if not ruta.exists():
        return []
    return [json.loads(linea) for linea in ruta.read_text(encoding="utf-8").splitlines() if linea.strip()]


def leer_filas(credentials: dict | None, sheet_id: str, hoja: str) -> list[dict]:
    """Lee todas las filas de una pestaña como dicts. Si algo falla devuelve [] (y deja log)."""
    try:
        if credentials and sheet_id:
            import gspread

            sh = gspread.service_account_from_dict(credentials).open_by_key(sheet_id)
            return sh.worksheet(hoja).get_all_records()
        return _leer_local(LOCAL_DIR / f"{hoja}.jsonl")
    except Exception as e:  # noqa: BLE001
        log.error("No se pudo leer '%s': %s: %s", hoja, type(e).__name__, e)
        return []
