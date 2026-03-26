import streamlit as st
import os
from navigation import *
from components.top_bar import top_bar

# -- PASO 4 ----------------------------------------------------------------------------------------
def screen_verify():
    top_bar(title="Verifique los datos", back_to="Procesando con IA...", show_stepper=True, step=0)

    from streamlit_ace import st_ace
    import re

    # Limpiar el JSON si viene con ```json ... ```
    raw = st.session_state.response
    if isinstance(raw, str):
        texto_limpio = re.sub(r"```json|```", "", raw).strip()
        data = json.loads(texto_limpio)
        data = fix_fechas(data)
    else:
        data = raw

    texto_json = json.dumps(data, indent=2, ensure_ascii=False)

    # Editor tipo VSCode
    edited = st_ace(
        value=texto_json,
        language="json",
        theme="monokai",        # tema oscuro como tu app
        font_size=13,
        tab_size=2,
        height=500,
        key="json_editor",
    )

    if st.button("Generar documento"):
        try:
            data = json.loads(edited)
            generate_docx(data)
            st.session_state.step = 5
            st.rerun()
        except json.JSONDecodeError as e:
            st.error(f"JSON inválido: {e}")