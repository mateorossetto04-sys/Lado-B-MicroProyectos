# Lado B Microproyectos (prototipo, lado empresa)

La empresa escribe su necesidad en texto libre → una IA arma un brief → la empresa lo edita y confirma → feedback.
Cada sesión queda como **una fila** en una Google Sheet. Todo el stack es **gratis** (Streamlit Community Cloud, GitHub, Google Sheets, Microsoft Clarity, Gemini sin facturación). Nada de esto pide tarjeta.

```
app.py              pantalla única y flujo
ladob/brief.py      validación del JSON, modo respaldo, conteo de ediciones
ladob/ai.py         llamada a Gemini (salida estructurada, reintento ante 429)
ladob/sheets.py     registro en Google Sheets (una fila por sesión)
tests/              pruebas (pytest)
```

## 0. Cómo funciona sin configurar nada
Sin claves la app **igual anda**: usa el modo respaldo por reglas y guarda los registros en `logs/sesiones_simulado.jsonl`. Sirve para ver el flujo antes de cargar credenciales.

## 1. Clave gratuita de Gemini (Google AI Studio)
1. Entrá a https://aistudio.google.com con tu cuenta de Google.
2. **Get API key** → **Create API key** (si pregunta, elegí "Create API key in new project").
3. Copiala. **No actives facturación** (no hace falta y así no podés gastar nada).
4. Pegala en `GEMINI_API_KEY` dentro de `secrets.toml`.

Notas: el plan gratis tiene límites por minuto y por día (de ahí el modo respaldo). Además, en el plan gratis Google puede usar lo que se envíe para mejorar sus productos: por eso la nota de privacidad de la app dice que el texto se guarda de forma anónima y **no se pide nombre ni email**. Si Google discontinúa el modelo, cambiá `GEMINI_MODEL` en secrets (por defecto `gemini-3.1-flash-lite`; `gemini-2.5-flash` ya no está disponible para cuentas nuevas; los nombres vigentes están en https://ai.google.dev/gemini-api/docs/models).

## 2. Google Sheet + cuenta de servicio
1. Creá una hoja nueva en https://sheets.google.com (nombre libre). Copiá el **ID**: es el texto largo de la URL entre `/d/` y `/edit`. Va en `GOOGLE_SHEET_ID`.
2. Entrá a https://console.cloud.google.com → creá un proyecto (gratis, no pide tarjeta).
3. Menú **APIs y servicios → Biblioteca**: activá **Google Sheets API** y **Google Drive API**.
4. **APIs y servicios → Credenciales → Crear credenciales → Cuenta de servicio**. Poné un nombre y finalizá.
5. Entrá a la cuenta creada → pestaña **Claves → Agregar clave → Crear clave nueva → JSON**. Se descarga un archivo (¡no lo subas a GitHub!).
6. Abrí ese JSON y copiá sus campos dentro de la sección `[gcp_service_account]` de `secrets.toml` (el ejemplo ya tiene todos los nombres).
7. En tu Google Sheet: **Compartir** → pegá el `client_email` de la cuenta de servicio → rol **Editor**.

La app crea sola la pestaña `sesiones` con los encabezados. Columnas: id de sesión, fecha/hora, texto original, brief IA, brief final, campos editados, estado, segundos hasta confirmar, uso de respaldo, precisión (1–5), ¿lo publicaría?, comentario.

**Estados**: la fila se crea cuando la persona toca "Armar mi brief" y arranca como `abandonó`; pasa a `generó brief` y luego a `confirmó`. Quien entra y no escribe nada no genera fila (eso lo ves en Clarity).

## 3. Probar en local
Necesitás Python 3.10+.
```
python -m venv .venv
.venv\Scripts\activate          # en Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .streamlit\secrets.toml.example .streamlit\secrets.toml   # y completalo
streamlit run app.py
```
Tests: `pip install pytest` y después `pytest`.

## 4. Publicar en Streamlit Community Cloud (gratis, URL pública sin login)
1. Subí esta carpeta a un repositorio de GitHub (el `.gitignore` ya excluye `secrets.toml`, `.venv` y los `.json`). Si el repo es público, **revisá que no haya claves**.
2. Entrá a https://share.streamlit.io con tu cuenta de GitHub → **Create app** → elegí el repo, la rama y `app.py` como archivo principal.
3. Antes de desplegar, en **Advanced settings → Secrets**, pegá el contenido completo de tu `secrets.toml`.
4. **Deploy**. Te da una URL `https://…streamlit.app`, pública: cualquiera la abre sin login. Si pasa un tiempo sin visitas la app se "duerme" y se despierta con un clic; abrila vos antes de cada prueba.

## 5. Activar Microsoft Clarity (gratis)
1. Entrá a https://clarity.microsoft.com → **New project** → poné nombre y la URL de tu app.
2. En **Settings → Overview** copiá el **Project ID** (código corto de letras y números).
3. Pegalo en `CLARITY_PROJECT_ID` (secrets locales y los de Streamlit Cloud). Reiniciá la app.
4. Abrí tu URL pública, navegá un poco y esperá unos minutos: debería aparecer una sesión en Clarity (Recordings / Heatmaps).

Aviso: la app corre dentro de un iframe en Streamlit Cloud y el script se inyecta en la página que lo contiene; si Clarity no muestra sesiones, revisá la pestaña Setup de Clarity para ver si detecta el tag. Podés tomar esto como medición complementaria: la fuente principal de datos es la Sheet.

## 5 bis. Vista del junior
La app tiene dos pestañas: **🏢 Soy empresa** y **🎓 Soy junior**. El junior ve los microproyectos que las empresas confirmaron (más nuevos primero) y, al final de la lista, 3 proyectos de ejemplo marcados como tales para que nunca esté vacía. Elige uno, se postula (motivo, skills, momento, horas por semana, alias opcional, sin email) y responde cuán atractivo le pareció y si se postularía en la vida real.

- Link para empresas: la URL de la app. Link para juniors: la misma URL con `?rol=junior` al final (abre directo la pestaña del junior).
- Pestañas nuevas en la Sheet (se crean solas): `proyectos` (cada brief confirmado) y `postulaciones` (una fila por sesión de junior, con estados `exploró` → `vio proyecto` → `postuló`).
- Los proyectos nuevos tardan hasta 30 segundos en aparecer para los juniors.
- En el prototipo la postulación solo se registra: la empresa no la ve.

## 6. Cómo correr las 2 pruebas con personas externas
Ambas usan la misma URL; las diferencias están en qué mirás.
- **Prueba 1 – Comodidad con el texto libre** (supuesto 1): pasale el link a personas de empresas/emprendimientos sin explicarles nada más. Mirá en la Sheet: ¿cuántas filas llegaron a `generó brief` vs. `abandonó`? ¿qué largo tienen los textos? ¿usaron "Usar ejemplo" (se nota si el texto es idéntico al ejemplo)? En Clarity: dónde dudan y dónde se van.
- **Prueba 2 – Precisión y confianza** (supuesto 2): mirá `precision_percibida`, `¿lo publicaría?` (Sí / Con cambios / No), `campos_editados` (cuántos cambios hicieron) y `uso_respaldo` (separá esas filas: no miden la IA real). Los comentarios dan el porqué.

Tip: pedí 10–15 personas por prueba y, antes de arrancar, hacé vos una prueba completa y comprobá que aparezca la fila en la Sheet.

